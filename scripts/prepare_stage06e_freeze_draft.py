#!/usr/bin/env python3
"""Package reviewed development evidence into an explicitly UNFROZEN draft.

No independent RAW is read. No signed freeze receipt is generated.
"""
import argparse
import csv
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from smoke_stage06c_raise_chains import AUDIT_SHA256, ELIGIBLE_SHA256, sha256_file
from validate_stage06_freeze import validate

MODEL_SHA = '8b67ba7f3775254c2ab47b1a4a1c36b92554f17783abf60c6aa9612d9a3458fd'
WEIGHT_SHA = {'drunet_color.pth':'479abe3c5327dfd10ff54a80ec7d4098ca80752a5c9492cdff31cee430bec4b4',
              'fbcnn_color.pth':'8b0e4ef23d59cf7ac934a342cb31a17619e4fa4a0b3374a9d78c5174312387e8'}
ROLES = {'development_fit':495,'development_early_stop':150,
         'development_calibration':149,'external_pilot':50,'independent_test':150}
CODE = ['scripts/run_stage06f_sealed_independent.py',
        'scripts/run_stage06c_paired_development.py',
        'scripts/run_stage06d_feature_canary.py',
        'scripts/smoke_stage06c_raise_chains.py',
        'scripts/validate_stage06_freeze.py',
        'scripts/fit_stage06_reliability.py',
        'experiments/stage06/acquisition_chains.py']


def add_file(source, relative, output, records):
    if not source.is_file():
        raise FileNotFoundError(source)
    target=output/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    records.append({'path':relative,'byte_count':target.stat().st_size,
                    'sha256':sha256_file(target)})


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--project-dir',type=Path,required=True)
    ap.add_argument('--audit-csv',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args()
    repo=args.repo_root.resolve();project=args.project_dir.resolve()
    eligible=repo/'experiments/stage06/manifests/RAISE_1k_eligible_roles_v1_20260925.csv'
    if sha256_file(eligible)!=ELIGIBLE_SHA256 or sha256_file(args.audit_csv)!=AUDIT_SHA256:
        raise ValueError('Pinned eligibility or audit hash differs from reviewed 06B record')
    roles={key:[] for key in ROLES}
    with eligible.open(newline='') as handle:
        for row in csv.DictReader(handle):
            if row['role'] not in roles:
                raise ValueError('Unexpected role')
            roles[row['role']].append(row['source_id'])
    if {k:len(v) for k,v in roles.items()}!=ROLES:
        raise ValueError('Source allocation changed')
    if len(set(sum(roles.values(),[])))!=994:
        raise ValueError('Role identities overlap')
    model_dir=project/'results/stage06d_full_development_model_fit_only_v2'
    model=model_dir/'frozen_reliability_models.joblib'
    if sha256_file(model)!=MODEL_SHA:
        raise ValueError('Saved model hash differs from verified candidate')
    external_weights={}
    for name,digest in WEIGHT_SHA.items():
        weight=project/'model_cache'/name
        if not weight.is_file() or sha256_file(weight)!=digest:
            raise ValueError('Pretrained component weight differs: '+name)
        external_weights[name]={'path':str(weight),'byte_count':weight.stat().st_size,
                                'sha256':digest}
    receipt=json.loads((model_dir/'model_training_receipt.json').read_text())
    if (receipt.get('source_counts')!={**{k:ROLES[k] for k in ROLES if k!='independent_test'},'independent_test':0}
        or receipt.get('proposed_chain_aware_family')!='boosting'
        or receipt.get('training_partition')!='development_fit'
        or receipt.get('selection_partition')!='development_early_stop'
        or receipt.get('calibration_partition')!='development_calibration'
        or receipt.get('independent_evaluation_permitted') is not False):
        raise ValueError('Model receipt does not match reviewed development partitioning')
    if args.output_dir.exists():
        raise FileExistsError('Draft bundle exists: '+str(args.output_dir))
    args.output_dir.mkdir(parents=True)
    output=args.output_dir.resolve();records=[]
    add_file(model,'artifacts/frozen_reliability_models.joblib',output,records)
    for rel in CODE:
        add_file(repo/rel,rel,output,records)
    from run_stage06c_paired_development import STAGE05_NOTEBOOK
    stage05_rel=str(STAGE05_NOTEBOOK.relative_to(repo))
    add_file(STAGE05_NOTEBOOK,stage05_rel,output,records)
    add_file(eligible,'artifacts/eligible_roles.csv',output,records)
    add_file(args.audit_csv,'artifacts/external_source_audit.csv',output,records)
    add_file(model_dir/'model_training_receipt.json',
             'artifacts/model_training_receipt.json',output,records)
    add_file(model_dir/'export_manifest.json',
             'artifacts/model_export_manifest.json',output,records)
    add_file(model_dir/'reliability_metrics.csv',
             'artifacts/exploratory_pilot_metrics.csv',output,records)
    add_file(project/'results/stage06d_full_development_model_v1/event_support.csv',
             'artifacts/event_support.csv',output,records)
    add_file(project/'results/stage06e_development_gates_v1/receipt.json',
             'artifacts/development_transfer_receipt.json',output,records)
    code_hashes={rel:sha256_file(repo/rel) for rel in CODE}
    code_hashes[stage05_rel]=sha256_file(STAGE05_NOTEBOOK)
    try:
        commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    except (OSError,subprocess.CalledProcessError) as exc:
        raise ValueError('Repository commit must be available for freeze') from exc
    import numpy, pandas, sklearn, torch
    runtime={'python':platform.python_version(), 'numpy':numpy.__version__,
             'pandas':pandas.__version__, 'sklearn':sklearn.__version__,
             'torch':torch.__version__, 'repo_commit':commit}
    spec={
      'schema_version':'stage06-freeze-v1',
      'study_id':'stage06_external_transport_chain_reliability',
      'frozen_at_utc':'REPLACE_AFTER_PROVENANCE_SIGNOFF',
      'stage05_immutable':True,'source_unit':'image_source',
      'primary_question':'source_macro_mae_gain_on_two_represented_chains',
      'primary_questions':['source-level continuous reliability improvement on both represented chains'],
      'primary_continuous_target':'centre_patch_detail_rmse',
      'event_thresholds_rmse':[.0075,.01],
      'primary_operational_threshold_rmse':.0075,
      'multiplicity_rule':'Single primary pooled source-level MAE gain at two-sided 95% source bootstrap; all other endpoints descriptive',
      'unsupported_event_rule':'No positive or no negative independent events: report binary calibration non-estimable without changing threshold',
      'external_dataset':{'name':'RAISE-1k','version':'official 1k NEF release',
        'license':'Non-commercial research and education; original RAW files not redistributed',
        'source_url':'https://loki.disi.unitn.it/RAISE/download.html',
        'archive_sha256':'2bf21449ed458502c09407cd9260b5d91fe27e7bc9e98f33bd108bbd8e40f8dc',
        'retrieval_date':'REPLACE_WITH_DOCUMENTED_DATE',
        'training_overlap_risk':'REPLACE_WITH_DOCUMENTED_RESIDUAL_RISK_AND_DECISION'},
      'provenance_decision':{'checkpoint_overlap_decision':'PENDING_REVIEW',
                             'documentation_sha256':''},
      'solvers':[{'role':'primary','name':'DPIR DRUNet',
                  'checkpoint_id':'479abe3c5327dfd10ff54a80ec7d4098ca80752a5c9492cdff31cee430bec4b4'},
                 {'role':'replication','name':'gradient inverse strength 0.01',
                  'checkpoint_id':'no learned checkpoint; fixed regularizer gradient, strength 0.01'}],
      'acquisition_chains':['srgb_j75_b16_n2','linear_j75_b16_n2'],
      'reliability_score':{'name':'chain-aware boosting on represented chains',
        'model_path':'artifacts/frozen_reliability_models.joblib',
        'features':['forward_consistency_residual','cross_chain_disagreement','solver_uncertainty'],
        'fit_partition':'development_fit','selection_partition':'development_early_stop',
        'calibration_partition':'development_calibration'},
      'comparators':['constant','residual_only','strong_chain_agnostic'],
      'source_roles':roles,
      'sample_size':{'independent_source_count':150,
        'design_basis':'Source-level precision: exploratory 50-pilot SD 0.0007290 implies illustrative 95% halfwidth 0.0001167 at 150; adaptive pilot, not power guarantee'},
      'random_seeds':{'data':20260925,'model':20260925,'source_bootstrap':20260926},
      'runtime':runtime,'code_sha256':code_hashes,
      'external_checkpoint_weights':external_weights,'artifacts':records,
      'status':'draft_unfrozen_independent_test_sealed'}
    target=output/'freeze_spec.DRAFT.json'
    target.write_text(json.dumps(spec,indent=2)+'\n')
    errors=validate(target)
    expected={'Unfrozen field: frozen_at_utc','Unfrozen field: external_dataset.retrieval_date',
              'Unfrozen field: external_dataset.training_overlap_risk'}
    if set(errors)!=expected:
        raise ValueError('Unexpected freeze validation errors: '+repr(errors))
    (output/'draft_status.json').write_text(json.dumps({'status':'NOT_FROZEN',
         'reason':'Provenance decision and retrieval date still open; no freeze receipt',
         'expected_validator_errors':errors,'repo_commit':commit,
         'artifact_count':len(records)},indent=2)+'\n')
    print(json.dumps({'status':'DRAFT_NOT_FROZEN','output_dir':str(output),
          'artifact_count':len(records),'expected_validator_errors':errors},indent=2))


if __name__=='__main__':
    main()
