#!/usr/bin/env python3
"""Read-only archive checks and explicitly scoped numerical reruns.
No synthetic Chrono replacement is used when PyChrono is unavailable.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys, time
from pathlib import Path
import numpy as np
sys.dont_write_bytecode = True

def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def save(p: Path, value) -> None:
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--wave-seeds',type=int,default=1000)
    a=ap.parse_args();root=a.repo.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(root))
    from analysis.rocket_recovery import yang_2026_landing_identification as yl
    from analysis.rocket_recovery import chrono_same_platform_multibody as cm
    from analysis.rocket_recovery import chrono_two_way_recovery as cw
    from analysis.rocket_recovery import chrono_revision_study as cs
    from analysis.rocket_recovery import chrono_leg_model as cl
    from analysis.rocket_recovery import barge_wave_revision as bw
    read=lambda p:json.loads((root/p).read_text(encoding='utf-8'))
    report={'audit_kind':'independent_execution_and_archive_check','python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'review_date':'2026-09-26','limitations':['No independent full Chrono solve in this environment','Hashes do not prove authorship or experimental authenticity','Only explicitly listed numerical runs were rerun']}
    files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts]
    save(out/'source_manifest.json',[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)])
    oldaudit=read('paper/yang_2026_extension/research-integrity-audit.json');check=[]
    for section in ('evidence_files','code_files'):
        for row in oldaudit.get(section,[]):
            p=root/row['path'];digest=sha(p) if p.exists() else None
            check.append({'section':section,'path':row['path'],'exists':p.exists(),'registered_sha256':row.get('sha256'),'current_sha256':digest,'matches':p.exists() and row.get('sha256')==digest})
    for row in oldaudit.get('figures',[]):
        for fmt,key in [('png','sha256'),('svg','svg_sha256')]:
            p=root/row[fmt];digest=sha(p) if p.exists() else None
            check.append({'section':'figures','path':row[fmt],'exists':p.exists(),'registered_sha256':row['checks'].get(key),'current_sha256':digest,'matches':p.exists() and row['checks'].get(key)==digest})
    report['registered_hash_checks']=check;report['source_file_count']=len(files)
    y=read('RocketRecoveryCases/Paper_Yang_2026/identified_landing_model/yang-2026-identified-landing-report.json')
    params=yl.IdentifiedParameters(**y['optimizer']['identified_parameters']);yr={}
    for case,cfg in yl.CONDITIONS.items():
        ref=yl.baseline_corrected_reference(cfg['figure']);sim=yl.simulate_condition(case,params);comp=yl.compare_condition(case,sim,ref);old=y['comparisons'][case]
        errors={k:float(np.max(np.abs(np.array(v)-np.array(old['model'][k])))) for k,v in comp['model'].items()}
        yr[case]={'execution':'fresh ODE integration from archived fitted parameters','model_vs_archived_max_abs_error':errors,'metrics':comp['metrics'],'reference_contact_time_s':ref['contact_time_s'],'model_equals_reference':{k:bool(np.allclose(comp['model'][k],comp['paper'][k],rtol=0,atol=1e-12)) for k in comp['model']}}
        np.savez_compressed(out/f'fresh_yang_{case}.npz',time_s=sim['time_s'],states=sim['states'],acceleration_up_m_s2=sim['acceleration_up_m_s2'],strut_force_n=sim['strut_force_n'],stroke_m=sim['stroke_m'])
    t=time.perf_counter();newparams,opt=yl.identify_parameters(yl.baseline_corrected_reference('fig09'))
    report['yang']={'cases':yr,'fresh_calibration':opt,'elapsed_s':time.perf_counter()-t,'parameter_difference':{k:newparams.as_dict()[k]-params.as_dict()[k] for k in params.as_dict()},'warning':'Withheld cases use reference-based baseline/contact alignment; not blind absolute-timing validation'}
    save(out/'independent_checks_partial.json',report)
    r=read('RocketRecoveryCases/Chrono_LeggedRecovery/chrono-same-platform-multibody-report.json');rr=read('RocketRecoveryCases/Chrono_LeggedRecovery/Output/RocketRecovery/chrono-same-platform-multibody-response.json')
    sim=rr['multibody'];tm=np.array(sim['time_s']);tp=np.array(rr['platform_time_s']);cfg=cm.landing_config(.0005)
    ft=cw.generalized_leg_force_from_chrono_6dof(sim,tp,footpad_radius_m=float(cfg['legs']['footpad_radius_m']))
    forces=np.array(ft['samples_6dof']);coarse=np.array(rr['platform_wrench_6dof']);normals=cw._deck_normal_from_rpy(sim,len(tm));normalsum=np.zeros(len(tm));verticalsum=np.zeros(len(tm));perleg={}
    for leg,f in sim['forces']['leg_contact_force_xyz_n'].items():
        fv=np.column_stack([f['x'],f['y'],f['z']]);recorded=np.array(sim['forces']['leg_contact_force_n'][leg]);n=np.maximum(0,np.einsum('ij,ij->i',fv,normals));v=np.maximum(0,fv[:,2]);normalsum+=n;verticalsum+=v
        perleg[leg]={'recorded_equals_positive_world_Fz':bool(np.array_equal(recorded,v)),'max_recorded_n':float(max(recorded)),'max_projected_normal_n':float(max(n))}
    oldimp=r['iterative_run']['passes'][-1]['contact_impulse']['total_normal_impulse_ns']
    ts=np.array([0,.002,.003,.004,.01,.02]);vs=np.array([0,0,1000,0,0,0]);tt=np.array([0,.01,.02])
    report['chrono_archive_audit']={
      'environment':cl.chrono_environment_report(),'saved_multibody_sample_count':len(tm),'nominal_integration_sample_count':40001,'saved_spacing_median_s':float(np.median(np.diff(tm))),'saved_fraction':len(tm)/40001,'compact_is_full_history':False,'field_definition':perleg,
      'compact_world_Fz_impulse_ns':float(np.trapezoid(verticalsum,tm)),'compact_normal_impulse_ns':float(np.trapezoid(normalsum,tm)),'archived_full_grid_summary_labelled_normal_impulse_ns':oldimp,'compact_vertical_impulse_relative_difference':float(np.trapezoid(verticalsum,tm)/oldimp-1),'saved_coarse_feedback_vertical_impulse_ns':float(np.trapezoid(-coarse[:,2],tp)),
      'compact_peak_world_Fz_n':float(max(max(x) for x in sim['forces']['leg_contact_force_n'].values())),'archived_peak_world_Fz_n':1000*float(r['iterative_run']['final_contact_summary']['max_leg_contact_force_kn']),
      'actual_resampling':'np.interp in generalized_leg_force_from_chrono_6dof','pulse_unit_test':{'source_impulse_ns':float(np.trapezoid(vs,ts)),'old_target_impulse_ns':float(np.trapezoid(np.interp(tt,ts,vs),tt)),'scope':'analytic regression, not a landing result'},
      'inertia_frame':{'legacy_z_up_body_inertia':cfg['rocket']['inertia_kg_m2'],'correct_total_before_component_allocation':{'Ixx':2.57e7,'Iyy':2.57e7,'Izz':3.76e5},'transverse_x_factor':2.57e7/cfg['rocket']['inertia_kg_m2']['roll_x'],'source':'Thies 2022 Table 3 and Figure 7: Y-up; current body: Z-up'},
      'deck_geometry':{'paper_length_beam_deck_z_m':[120,50,3],'legacy_collision_box_length_beam_m':[180,54],'legacy_deck_z_m':0,'compact_force_3m_roll_lever_sensitivity_nm':float(3*np.max(np.abs(forces[:,1]))),'scope':'algebraic sensitivity only; not a corrected dynamic result'},
      'work_counterexample':{'F':[1,0,0],'point_and_cg':[0,1,0],'omega':[0,0,1],'v_cg':[0,0,0],'correct_power_w':0,'legacy_power_w':-1},
      'action_reaction':'Assembly check: opposite arrays are constructed together. Not independent solver validation.',
      'study_passes':{'production':[4,526],'time_refinement':[2,516],'stiffness':[1,516]}}
    study=cs.default_study_config();study['time_domain']['end_s']=526.;operator=cs.load_platform_operator(study);wave=cs.build_wave_components(operator,study);wang=read('RocketRecoveryCases/Paper_WangZhi_2023/platform_config.json')
    fresh=cs.solve_platform(operator,study,wang,wave,tp,coarse[:,cs.ACTIVE_DOF_INDICES]);base=cs.solve_platform(operator,study,wang,wave,tp,np.zeros((len(tp),3)))
    report['platform_only_replay']={'scope':'fresh radiation-memory integration driven by archived contact forces, not a fresh coupled solve','max_abs_q_difference':np.max(np.abs(np.array(fresh['q_active'])-np.array(rr['final_q_active'])),axis=0).tolist(),'max_abs_baseline_difference':np.max(np.abs(np.array(base['q_active'])-np.array(rr['baseline_q_active'])),axis=0).tolist(),'energy':fresh['energy'],'initial_q':np.array(fresh['q_active'])[0].tolist(),'initial_qd':np.array(fresh['qd_active'])[0].tolist(),'nominal_touchdown_minus_start_s':4.0}
    np.savez_compressed(out/'fresh_platform_only_replay.npz',time_s=tp,q_active=fresh['q_active'],qd_active=fresh['qd_active'])
    save(out/'independent_checks_partial.json',report)
    wd=read('RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/wave-sensitivity-revision-600s.json');wr=read('RocketRecoveryCases/Barge_120x50/Output/RocketRecovery/deck-point-rao-medium.json');conf=read('RocketRecoveryCases/Barge_120x50/platform_config.json')
    omega=np.array(wd['frequency_grids']['random_synthesis']['frequencies_rad_s']);timegrid=np.arange(6000)*.1
    names,transfer=bw.build_revision_transfer_matrix(wr,90.,omega,wd['deck_points']['all']);_,amps=bw.spectrum_component_amplitudes(omega,1.,10.,3.3)
    physical=[x['id'] for x in wd['deck_points']['physical_legs']];allids=[x['id'] for x in wd['deck_points']['all']]
    seeds=list(range(int(wd['method']['seed_start']),int(wd['method']['seed_start'])+a.wave_seeds));samples=[];start=time.perf_counter()
    for bs in range(0,len(seeds),16):
        batch=seeds[bs:bs+16];phases=np.array([np.random.default_rng(s).uniform(0,2*np.pi,len(omega)) for s in batch]);response=bw.synthesize_response_batch(transfer,amps,phases,omega,timegrid);metrics=bw.response_metrics_batch(names,response,physical,allids,conf['platform'])
        for i,s in enumerate(batch):
            row={'seed':s};row.update({k:float(v[i])*3 for k,v in metrics.items() if k!='deck_edge.max_immersion_m'});row['deck_edge.max_immersion_m']=max(0,-(conf['platform']['deck_z_m']+row['deck_edge.minimum_dynamic_elevation_m']));samples.append(row)
    critical=None
    for c in wd['cases']:
        state=c.get('sea_state',c)
        if float(state.get('hs_m',-1))==3 and float(state.get('tp_s',-1))==10 and float(c.get('heading_deg',-1))==90:critical=c;break
    if critical is None:raise ValueError('Critical condition not found')
    old=critical['samples'];diffs={k:float(max(abs(row[k]-saved[k]) for row,saved in zip(samples,old))) for k in samples[0] if k!='seed'}
    speedkey=next(k for k in samples[0] if 'landing_center' in k and 'vertical_velocity' in k)
    report['wave_fresh_selected_case']={'hs_m':3,'tp_s':10,'heading_deg':90,'duration_s':600,'dt_s':.1,'realizations':len(samples),'elapsed_s':time.perf_counter()-start,'max_abs_metric_differences':diffs,'center_speed_key':speedkey,'center_speed_p95_m_s':float(np.quantile([x[speedkey] for x in samples],.95)),'scope':'ONE condition re-synthesized from BEM RAOs, other 62 not re-synthesized'}
    save(out/'fresh_wave_selected_samples.json',samples)
    report['archived_wave_metadata']={'condition_count':len(wd['cases']),'acceptance':wd['acceptance']}
    save(out/'independent_checks.json',report);print(json.dumps({'completed':True,'out':str(out)},ensure_ascii=False))
if __name__=='__main__':main()
