#!/usr/bin/env python3
"""One-time Stage 06F inference; preflight never reads independent RAW files.

This runner is inert until a validated freeze specification and separately
signed, hash-bound freeze receipt exist. It never fits or calibrates a model.
"""
import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

import joblib
import numpy as np

from run_stage06c_paired_development import (ROOT, STAGE05_NOTEBOOK,
                                              acquire, load_stage05_components,
                                              store_json)
from run_stage06d_feature_canary import features
from smoke_stage06c_raise_chains import (AUDIT_SHA256, ELIGIBLE_SHA256,
                                         decode_verified, load_unique_rows,
                                         sha256_file)
from validate_stage06_freeze import validate

CHAINS = ('srgb_j75_b16_n2', 'linear_j75_b16_n2')
EXPECTED_MODEL_SHA = '8b67ba7f3775254c2ab47b1a4a1c36b92554f17783abf60c6aa9612d9a3458fd'
EXPECTED_ROLES = {'development_fit':495, 'development_early_stop':150,
                  'development_calibration':149, 'external_pilot':50,
                  'independent_test':150}


def boundary(args):
    """Check only frozen metadata and files; no NEF path is read here."""
    errors = validate(args.freeze_spec)
    if errors:
        raise ValueError('Stage 06E validator failed: ' + '; '.join(errors))
    spec = json.loads(args.freeze_spec.read_text())
    receipt = json.loads(args.freeze_receipt.read_text())
    if (receipt.get('status') != 'frozen_for_one_time_independent_evaluation'
        or receipt.get('freeze_spec_sha256') != sha256_file(args.freeze_spec)
        or not receipt.get('signed_by') or not receipt.get('signed_at_utc')):
        raise ValueError('No signed, hash-bound Stage 06E freeze receipt')
    decision = spec.get('provenance_decision', {})
    if (decision.get('checkpoint_overlap_decision') != 'proceed_with_documented_residual_risk'
        or not decision.get('documentation_sha256')
        or not spec.get('external_dataset', {}).get('retrieval_date')):
        raise ValueError('Dataset provenance and checkpoint-overlap decision remain open')
    roles = spec.get('source_roles', {})
    if {k:len(roles.get(k,[])) for k in EXPECTED_ROLES} != EXPECTED_ROLES:
        raise ValueError('Frozen source allocation is incomplete')
    if spec.get('acquisition_chains') != list(CHAINS):
        raise ValueError('Unexpected frozen acquisition chains')
    if spec.get('event_thresholds_rmse') != [.0075,.01]:
        raise ValueError('Frozen thresholds differ from 06D development choice')
    if (spec.get('primary_continuous_target') != 'centre_patch_detail_rmse'
        or spec.get('primary_question') != 'source_macro_mae_gain_on_two_represented_chains'):
        raise ValueError('Primary endpoint or claim changed')
    if sha256_file(args.eligible_manifest) != ELIGIBLE_SHA256:
        raise ValueError('Eligible manifest changed')
    if sha256_file(args.audit_csv) != AUDIT_SHA256:
        raise ValueError('RAW audit changed')
    manifest=load_unique_rows(args.eligible_manifest)
    if len(manifest)!=994:
        raise ValueError('Expected 994 eligible sources')
    for role, values in roles.items():
        if any(x not in manifest or manifest[x]['role']!=role for x in values):
            raise ValueError('Frozen source identities differ from reviewed 06B manifest')
    frozen_model = args.freeze_spec.parent / spec['reliability_score']['model_path']
    if not frozen_model.is_file() or sha256_file(frozen_model)!=EXPECTED_MODEL_SHA:
        raise ValueError('Fitted model bytes differ from reviewed 06D candidate')
    model_artifacts=[x for x in spec['artifacts'] if x['sha256']==EXPECTED_MODEL_SHA]
    if len(model_artifacts)!=1 or (args.freeze_spec.parent/model_artifacts[0]['path']).resolve()!=frozen_model.resolve():
        raise ValueError('Fitted model was not included in validated freeze artifacts')
    runner_artifacts=[x for x in spec['artifacts'] if x['path'].endswith('run_stage06f_sealed_independent.py')]
    if len(runner_artifacts)!=1 or runner_artifacts[0]['sha256']!=sha256_file(Path(__file__)):
        raise ValueError('Runner is not the frozen version')
    required_code = ['scripts/run_stage06c_paired_development.py',
                     'scripts/run_stage06d_feature_canary.py',
                     'scripts/smoke_stage06c_raise_chains.py',
                     'scripts/validate_stage06_freeze.py',
                     'experiments/stage06/acquisition_chains.py']
    pinned_code = spec.get('code_sha256',{})
    for relative in required_code:
        actual=ROOT/relative
        if not actual.is_file() or pinned_code.get(relative)!=sha256_file(actual):
            raise ValueError('Imported code changed since freeze: '+relative)
    if pinned_code.get(str(STAGE05_NOTEBOOK.relative_to(ROOT)))!=sha256_file(STAGE05_NOTEBOOK):
        raise ValueError('Stage 05 component notebook changed since freeze')
    return spec,frozen_model


def run(args,spec,model_path):
    import torch
    from experiments.stage06.acquisition_chains import linear_to_srgb,srgb_to_linear
    if not torch.cuda.is_available():
        raise RuntimeError('Pinned reconstruction needs CUDA')
    if args.output_dir.exists():
        raise FileExistsError('One-time output path already exists: '+str(args.output_dir))
    test_ids=spec['source_roles']['independent_test']
    audit=load_unique_rows(args.audit_csv)
    eligible=load_unique_rows(args.eligible_manifest)
    # Source directory may be listed, but no RAW is read before freeze gates.
    for sid in test_ids:
        row=audit.get(sid)
        path=args.nef_dir/f'{sid}.NEF'
        if (row is None or row['role']!='independent_test'
            or row['relative_path']!=path.name
            or eligible[sid]['relative_path']!=path.name
            or not path.is_file() or path.stat().st_size!=int(row['byte_count'])):
            raise ValueError('Missing/mismatched independent source: '+sid)
    bundle=joblib.load(model_path)  # only the hash-verified local frozen artifact
    models=bundle.get('models',{})
    continuous=bundle.get('continuous_calibrators',{})
    binary=bundle.get('probability_calibrators',{})
    for name in ('residual_only','proposed_chain_aware'):
        if name not in models or name not in continuous:
            raise ValueError('Frozen predictor/calibrator absent: '+name)
    if bundle.get('thresholds') != [.0075,.01]:
        raise ValueError('Frozen model thresholds changed')
    device=torch.device('cuda')
    B01,L02,J04,dpir_model,fbcnn,settings,_=load_stage05_components(args.model_cache,device)
    # An exclusive file in the freeze directory prevents accidental reruns with
    # a different output directory. A failed attempt requires documented review.
    ledger=args.freeze_spec.parent/'stage06f_one_time_started.json'
    if not args.output_dir.parent.is_dir():
        raise ValueError('Independent output parent must exist before starting')
    try:
        fd=os.open(ledger,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError as exc:
        raise RuntimeError('Independent run already started; inspect its receipt') from exc
    with os.fdopen(fd,'w') as handle:
        json.dump({'freeze_spec_sha256':sha256_file(args.freeze_spec),
                   'output_dir':str(args.output_dir.resolve()),
                   'status':'one_time_started'},handle)
        handle.flush();os.fsync(handle.fileno())
    args.output_dir.mkdir(parents=True)
    receipt={'schema':'stage06f-one-time-v1','status':'running_sealed',
             'freeze_spec_sha256':sha256_file(args.freeze_spec),
             'freeze_receipt_sha256':sha256_file(args.freeze_receipt),
             'source_ids':test_ids,'completed_source_ids':[],
             'independent_test_inference':True,'failures':[]}
    store_json(args.output_dir/'execution_receipt.json',receipt)
    fields=['source_id','role','chain_id','patch_id','observed_detail_rmse',
            'predicted_rmse__residual_only','predicted_rmse__proposed_chain_aware',
            'event_probability_0.0075__residual_only',
            'event_probability_0.0075__proposed_chain_aware',
            'event_probability_0.01__residual_only',
            'event_probability_0.01__proposed_chain_aware']
    try:
        with (args.output_dir/'sealed_predictions.partial.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
            for sid in test_ids:
                raw=audit[sid];path=args.nef_dir/f'{sid}.NEF'
                if sha256_file(path)!=raw['file_sha256']:
                    raise ValueError('RAW hash changed: '+sid)
                rgb=decode_verified(path,raw['decoded_rgb_sha256'])
                h,w=rgb.shape[:2]
                ref=rgb[(h-256)//2:(h+256)//2,(w-256)//2:(w+256)//2].astype(np.float64)/255
                seed=20260925+int(hashlib.sha256(sid.encode()).hexdigest()[:8],16)
                recon={}
                for chain in CHAINS:
                    obs=acquire(ref,chain,seed,B01)
                    deblocked,_,_=J04.deblock(obs,fbcnn,device)
                    data=srgb_to_linear(deblocked) if chain.startswith('linear_') else deblocked
                    dpir,_,_=L02.reconstruct(data,1.0,dpir_model,device,settings)
                    grad=B01.inverse_spectrum(np.fft.fft2(data,axes=(0,1)),1.6,'gradient',.01)
                    if chain.startswith('linear_'):
                        dpir,grad=linear_to_srgb(dpir),linear_to_srgb(grad)
                    recon[chain]=(obs,deblocked,dpir,grad)
                for chain,(obs,deblocked,dpir,grad) in recon.items():
                    other=next(x for x in CHAINS if x!=chain)
                    values=features(ref,obs,deblocked,dpir,grad,recon[other][2],chain,B01)
                    import pandas as pd
                    frame=pd.DataFrame({k:v for k,v in values.items() if k!='observed_detail_rmse'})
                    outputs={}
                    for name in ('residual_only','proposed_chain_aware'):
                        fitted=models[name];raw_pred=fitted['model'].predict(frame[fitted['features']])
                        outputs['predicted_rmse__'+name]=continuous[name].predict(raw_pred)
                        for threshold in (.0075,.01):
                            key=f'{threshold:.6g}'
                            calibrator=binary[name][key]
                            col=f'event_probability_{key}__{name}'
                            outputs[col]=(np.full(144,np.nan) if calibrator is None
                                          else calibrator.predict(raw_pred))
                    for j in range(144):
                        writer.writerow({'source_id':sid,'role':'independent_test',
                            'chain_id':chain,'patch_id':j,
                            'observed_detail_rmse':float(values['observed_detail_rmse'][j]),
                            **{k:float(v[j]) for k,v in outputs.items()}})
                stream.flush()
                receipt['completed_source_ids'].append(sid)
                store_json(args.output_dir/'execution_receipt.json',receipt)
        partial=args.output_dir/'sealed_predictions.partial.csv'
        final=args.output_dir/'sealed_predictions.csv'
        partial.replace(final)
        receipt['predictions_sha256']=sha256_file(final)
        receipt['prediction_rows']=len(test_ids)*288
        receipt['status']='sealed_complete_unanalysed'
    except Exception as exc:
        receipt['status']='failed_sealed_partial'
        receipt['failures'].append({'type':type(exc).__name__,'message':str(exc)})
        raise
    finally:
        store_json(args.output_dir/'execution_receipt.json',receipt)
    print(json.dumps({'status':receipt['status'],'sources':len(test_ids),
                      'rows':receipt['prediction_rows'],
                      'predictions_sha256':receipt['predictions_sha256']},indent=2))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode',choices=('preflight','run'),default='preflight')
    ap.add_argument('--freeze-spec',type=Path,required=True)
    ap.add_argument('--freeze-receipt',type=Path,required=True)
    ap.add_argument('--eligible-manifest',type=Path,required=True)
    ap.add_argument('--audit-csv',type=Path,required=True)
    ap.add_argument('--nef-dir',type=Path)
    ap.add_argument('--model-cache',type=Path)
    ap.add_argument('--output-dir',type=Path)
    ap.add_argument('--permit-one-time-independent-run',action='store_true')
    args=ap.parse_args()
    spec,model_path=boundary(args)
    if args.mode=='preflight':
        print(json.dumps({'status':'freeze_preflight_passed_no_raw_read',
            'freeze_spec_sha256':sha256_file(args.freeze_spec),
            'model_sha256':sha256_file(model_path),
            'allocated_independent_sources':150},indent=2))
        return
    if (not args.permit_one_time_independent_run or not args.nef_dir
        or not args.model_cache or not args.output_dir):
        ap.error('Run requires explicit one-time flag, RAW dir, model cache and new output dir')
    run(args,spec,model_path)


if __name__=='__main__':
    main()
