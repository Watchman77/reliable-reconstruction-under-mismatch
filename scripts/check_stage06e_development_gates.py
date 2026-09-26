#!/usr/bin/env python3
"""Audited leave-one-chain-out development diagnostic and source precision plan.

Never reads independent rows. This is a pre-freeze engineering check; pilot
predictions contribute only an explicitly exploratory variance estimate.
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.isotonic import IsotonicRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

from fit_stage06_reliability import (sha256_file, validate_eligible_sources,
                                     validate_source_roles)

FEATURES = ['forward_consistency_residual', 'cross_chain_disagreement',
            'solver_uncertainty']
CHAINS = ('linear_j75_b16_n2', 'srgb_j75_b16_n2')


def source_gain(frame):
    grouped = frame.assign(gain=(frame.observed_detail_rmse - frame.residual_prediction).abs()
                           - (frame.observed_detail_rmse - frame.chain_prediction).abs())
    return grouped.groupby('source_id').gain.mean().to_numpy(float)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--development-csv', required=True, type=Path)
    ap.add_argument('--pilot-predictions-csv', required=True, type=Path)
    ap.add_argument('--eligible-source-manifest', required=True, type=Path)
    ap.add_argument('--output-dir', required=True, type=Path)
    args = ap.parse_args()
    if args.output_dir.exists():
        raise FileExistsError(args.output_dir)
    frame = pd.read_csv(args.development_csv)
    validate_source_roles(frame)
    eligible_sha = validate_eligible_sources(frame, args.eligible_source_manifest)
    if set(frame.role) != {'development_fit', 'development_early_stop',
                           'development_calibration'}:
        raise ValueError('Development table must contain exactly three non-pilot roles')
    if set(frame.chain_id) != set(CHAINS) or frame.source_id.nunique() != 794:
        raise ValueError('Expected two chains and all 794 audited development sources')
    if len(frame) != 794 * 288 or frame.duplicated(['source_id','chain_id','patch_id']).any():
        raise ValueError('Incomplete or duplicated development patches')
    if not np.isfinite(frame[FEATURES + ['observed_detail_rmse']].to_numpy()).all():
        raise ValueError('Non-finite predictor or target')
    pilot = pd.read_csv(args.pilot_predictions_csv)
    allowed = pd.read_csv(args.eligible_source_manifest).set_index('source_id').role
    if set(pilot.source_id.map(allowed)) != {'external_pilot'} or pilot.source_id.nunique()!=50:
        raise ValueError('Expected 50 previously inspected external-pilot sources only')
    if len(pilot) != 50*288 or set(pilot.source_id)&set(frame.source_id):
        raise ValueError('Pilot rows incomplete or cross development identities')
    for name in ('observed_detail_rmse','predicted_rmse__residual_only',
                 'predicted_rmse__proposed_chain_aware'):
        if name not in pilot or not np.isfinite(pilot[name].to_numpy()).all():
            raise ValueError('Malformed pilot prediction: '+name)
    pilot_d = pilot.assign(residual_prediction=pilot.predicted_rmse__residual_only,
                           chain_prediction=pilot.predicted_rmse__proposed_chain_aware)
    per_source = source_gain(pilot_d)
    sd = float(per_source.std(ddof=1))
    planning = {
        'basis': 'exploratory 50-source pilot variability; not independent power',
        'pilot_sources': len(per_source), 'pilot_source_difference_sd': sd,
        'independent_allocated_sources': 150,
        'anticipated_normal_95pct_halfwidth_at_150': 1.96*sd/math.sqrt(150),
        'illustrative_sources_for_0_00025_halfwidth': math.ceil((1.96*sd/.00025)**2),
        'planning_uncertainty': 'pilot was inspected adaptively; precision may not transport',
    }
    rows = []
    for training_chain, held_chain in ((CHAINS[0],CHAINS[1]), (CHAINS[1],CHAINS[0])):
        fit = frame[(frame.role=='development_fit')&(frame.chain_id==training_chain)]
        calibration = frame[(frame.role=='development_calibration')&(frame.chain_id==training_chain)]
        early = frame[(frame.role=='development_early_stop')&(frame.chain_id==held_chain)].copy()
        chain_model=GradientBoostingRegressor(max_depth=3,n_estimators=200,
                 learning_rate=.03,loss='huber',random_state=20260925)
        residual_model=make_pipeline(StandardScaler(), Ridge(alpha=.01))
        chain_model.fit(fit[FEATURES],fit.observed_detail_rmse)
        residual_model.fit(fit[['forward_consistency_residual']],fit.observed_detail_rmse)
        for name, model, cols in (
                ('chain_prediction',chain_model,FEATURES),
                ('residual_prediction',residual_model,['forward_consistency_residual'])):
            isotonic=IsotonicRegression(y_min=0,out_of_bounds='clip')
            isotonic.fit(model.predict(calibration[cols]),calibration.observed_detail_rmse)
            early[name]=isotonic.predict(model.predict(early[cols]))
        gain=source_gain(early)
        rng=np.random.default_rng(20260925)
        interval=np.quantile(rng.choice(gain,size=(10000,len(gain)),replace=True).mean(axis=1),[.025,.975])
        rows.append({'training_chain': training_chain, 'held_out_chain': held_chain,
             'fit_sources': int(fit.source_id.nunique()),
             'calibration_sources': int(calibration.source_id.nunique()),
             'held_out_early_stop_sources': len(gain),
             'mean_source_mae_improvement': float(gain.mean()),
             'sources_improved': int((gain>0).sum()),
             'source_bootstrap_95pct_low': float(interval[0]),
             'source_bootstrap_95pct_high': float(interval[1])})
    args.output_dir.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(args.output_dir/'leave_one_chain_out.csv',index=False)
    receipt={'schema':'stage06e-development-gates-v1',
             'independent_test_inference':False,
             'development_csv_sha256':sha256_file(args.development_csv),
             'pilot_prediction_sha256':sha256_file(args.pilot_predictions_csv),
             'eligible_manifest_sha256':eligible_sha,
             'transfer':rows,'source_precision_planning':planning,
             'status':'development_diagnostics_only_not_frozen'}
    (args.output_dir/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'transfer':rows,'planning':planning,'output_dir':str(args.output_dir)},indent=2))


if __name__ == '__main__':
    main()
