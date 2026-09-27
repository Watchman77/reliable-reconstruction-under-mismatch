#!/usr/bin/env python3
"""Finalize an already reviewed Stage 06E draft after owner provenance sign-off.

Never reads independent RAW. A signed receipt is created only after all
bundle artifacts, code and pretrained weights pass hash validation.
"""
import argparse
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
import shutil

from smoke_stage06c_raise_chains import AUDIT_SHA256, ELIGIBLE_SHA256, sha256_file
from validate_stage06_freeze import validate

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--draft-dir',type=Path,required=True)
    ap.add_argument('--decision-file',type=Path,required=True)
    ap.add_argument('--repo-root',type=Path,required=True)
    ap.add_argument('--eligible-manifest',type=Path,required=True)
    ap.add_argument('--audit-csv',type=Path,required=True)
    ap.add_argument('--model-cache',type=Path,required=True)
    args=ap.parse_args()
    draft=args.draft_dir.resolve()
    status=json.loads((draft/'draft_status.json').read_text())
    if status['status']!='NOT_FROZEN' or (draft/'freeze_spec.json').exists() or (draft/'freeze_receipt.json').exists():
        raise ValueError('Draft not ready or freeze already issued')
    original=draft/'freeze_spec.DRAFT.json'
    spec=json.loads(original.read_text())
    if spec.get('status')!='draft_unfrozen_independent_test_sealed':
        raise ValueError('Unexpected draft status')
    decision=json.loads(args.decision_file.read_text())
    required={'decision':'proceed_with_documented_residual_risk',
              'accepted_noncommercial_terms':True,
              'acknowledges_unverified_pretrained_image_overlap':True,
              'confirms_no_independent_outcomes_inspected':True}
    for key,value in required.items():
        if decision.get(key)!=value:
            raise ValueError('Protocol owner did not attest '+key)
    if not decision.get('protocol_owner') or not decision.get('decision_at_utc'):
        raise ValueError('Protocol owner and signed decision time are required')
    if not decision.get('risk_statement') or len(decision['risk_statement'].strip())<100:
        raise ValueError('Specific residual-overlap statement is required')
    retrieval=decision.get('official_raise_retrieval_date','')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(retrieval)):
        raise ValueError('A documented official RAISE retrieval date (YYYY-MM-DD) is required')
    retrieved_on=date.fromisoformat(retrieval)
    signed_time=datetime.fromisoformat(decision['decision_at_utc'].replace('Z','+00:00'))
    if signed_time.tzinfo is None or signed_time.utcoffset().total_seconds()!=0:
        raise ValueError('Decision must have UTC timestamp')
    if signed_time>datetime.now(timezone.utc):
        raise ValueError('Future decision timestamp')
    if retrieved_on>signed_time.date():
        raise ValueError('Dataset retrieval cannot postdate the signed decision')
    if sha256_file(args.eligible_manifest)!=ELIGIBLE_SHA256 or sha256_file(args.audit_csv)!=AUDIT_SHA256:
        raise ValueError('Source allowlist or audit changed')
    for record in spec['artifacts']:
        path=draft/record['path']
        if not path.is_file() or path.stat().st_size!=record['byte_count'] or sha256_file(path)!=record['sha256']:
            raise ValueError('Draft artifact changed: '+record['path'])
    repo=args.repo_root.resolve()
    for rel,digest in spec['code_sha256'].items():
        if sha256_file(repo/rel)!=digest:
            raise ValueError('Executable code changed since draft: '+rel)
    for name,meta in spec['external_checkpoint_weights'].items():
        actual=args.model_cache/name
        if not actual.is_file() or actual.stat().st_size!=meta['byte_count'] or sha256_file(actual)!=meta['sha256']:
            raise ValueError('Pinned checkpoint changed: '+name)
    doc=draft/'artifacts/provenance_decision.json'
    if doc.exists():
        raise FileExistsError(doc)
    # Copy the protocol owner's exact signed declaration into the bundle.
    shutil.copy2(args.decision_file,doc)
    doc_sha=sha256_file(doc)
    spec['artifacts'].append({'path':'artifacts/provenance_decision.json',
        'byte_count':doc.stat().st_size,'sha256':doc_sha})
    spec['external_dataset']['retrieval_date']=retrieval
    spec['external_dataset']['training_overlap_risk']=decision['risk_statement'].strip()
    spec['provenance_decision']={'checkpoint_overlap_decision':required['decision'],
                                 'documentation_sha256':doc_sha}
    spec['frozen_at_utc']=datetime.now(timezone.utc).isoformat()
    spec['status']='frozen_for_one_time_independent_evaluation'
    frozen=draft/'freeze_spec.json'
    frozen.write_text(json.dumps(spec,indent=2)+'\n')
    errors=validate(frozen)
    if errors:
        frozen.unlink()
        doc.unlink()
        raise ValueError('Freeze validator rejected candidate: '+repr(errors))
    # Require the precise additional gates of the independent preflight too.
    from run_stage06f_sealed_independent import boundary
    draft_receipt=draft/'freeze_receipt.json'
    now=datetime.now(timezone.utc).isoformat()
    receipt={'schema':'stage06e-freeze-receipt-v1',
        'status':'frozen_for_one_time_independent_evaluation',
        'freeze_spec_sha256':sha256_file(frozen),
        'signed_by':decision['protocol_owner'],
        'signed_at_utc':decision['decision_at_utc'],
        'receipt_created_at_utc':now,
        'provenance_decision_sha256':doc_sha,
        'independent_test_outcomes_inspected':False}
    draft_receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    try:
        boundary(argparse.Namespace(freeze_spec=frozen,freeze_receipt=draft_receipt,
               eligible_manifest=args.eligible_manifest,audit_csv=args.audit_csv))
    except Exception:
        draft_receipt.unlink()
        frozen.unlink()
        doc.unlink()
        raise
    print(json.dumps({'status':receipt['status'],'freeze_spec_sha256':receipt['freeze_spec_sha256'],
          'receipt_path':str(draft_receipt),'test_raw_read':False},indent=2))

if __name__=='__main__':
    main()
