#!/usr/bin/env python3
"""Numerical comparisons at actually rerun points; no whole-mesh claim."""
from pathlib import Path
import sys,json,hashlib,subprocess,argparse
import numpy as np
sys.dont_write_bytecode=True
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--evidence',type=Path,required=True)
parser.add_argument('--binary',type=Path,required=True)
args=parser.parse_args()
root=args.repo.resolve();out=args.evidence.resolve()
if not (root/'SourceCode').is_dir(): raise SystemExit('Not a HAMS project root')
if not args.binary.is_file(): raise SystemExit('Compiled HAMS binary missing')
sys.path.insert(0,str(root))
from analysis.rocket_recovery.barge_hydrodynamic_convergence import parse_radiation_outputs,parse_motion_outputs
from analysis.rocket_recovery.common import parse_hydrostar_rao

def compare(a,b):
 rows=[]
 for p in sorted(a.rglob('*.rao')):
  q=b/p.relative_to(a)
  if not q.exists():continue
  aa=parse_hydrostar_rao(p);bb=parse_hydrostar_rao(q);br={x['frequency']:x for x in bb['rows']}
  if aa['headings']!=bb['headings']:raise ValueError('Heading mismatch')
  pairs=[(x,br[x['frequency']]) for x in aa['rows']]
  for field in ['amplitudes','phases']:
   if not pairs or field not in pairs[0][0]:continue
   av=np.array([x[field] for x,y in pairs]);bv=np.array([y[field] for x,y in pairs]);delta=np.abs(av-bv)
   if field=='phases':delta=np.abs((av-bv+180)%360-180)
   scale=max(np.max(np.abs(bv)),1.e-12)
   rows.append({'file':p.relative_to(a).as_posix(),'field':field,'frequency_count':len(pairs),'value_count':av.size,'max_absolute_difference':float(delta.max()),'max_difference_over_file_max':float(delta.max()/scale),'count_outside_10pct_plus1e-7':int(np.sum(delta>1e-7+.1*np.abs(bv)))})
 return {'files':len({x['file'] for x in rows}),'rows':rows,'max_file_scaled_amplitude_difference':max(x['max_difference_over_file_max'] for x in rows if x['field']=='amplitudes'),'files_with_nonzero_amplitude_difference':sum(x['max_absolute_difference']>0 for x in rows if x['field']=='amplitudes')}
med=root/'RocketRecoveryCases/Barge_120x50/validation/hydrodynamic_runs/medium_local025_high5/Output'
d={'scope':'Fresh Fortran solver; medium only five anchor frequencies. Comparison is of parsed Hydrostar .rao values; not the original all-format certification comparator.','compiler':subprocess.check_output(['gfortran','--version'],text=True).splitlines()[0],'binary_sha256':hashlib.sha256(args.binary.read_bytes()).hexdigest()}
d['medium_five_anchors_vs_archived']=compare(out/'fresh_medium_anchors/Output',med)
d['cylinder_vs_archived']=compare(out/'fresh_cylinder/Output',root/'CertTest/Cylinder/Output')
d['cylinder_vs_benchmark']=compare(out/'fresh_cylinder/Output',root/'CertTest/Cylinder/Output_Benchmark')
d['fresh_medium_motion']=parse_motion_outputs(out/'fresh_medium_anchors/Output')
(out/'fresh_hams_comparison.json').write_text(json.dumps(d,ensure_ascii=False,indent=2))
for k in ['medium_five_anchors_vs_archived','cylinder_vs_archived','cylinder_vs_benchmark']:
 r=d[k];print(k,{a:b for a,b in r.items() if a!='rows'});print(sorted(r['rows'],key=lambda x:x['max_difference_over_file_max'],reverse=True)[:4])
