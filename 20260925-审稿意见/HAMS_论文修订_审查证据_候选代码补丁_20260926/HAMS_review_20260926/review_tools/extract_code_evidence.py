from pathlib import Path
import json,hashlib,zipfile,argparse
parser=argparse.ArgumentParser(description='Extract exact original code and seal against archive')
parser.add_argument('--repo',type=Path,required=True)
parser.add_argument('--out',type=Path,required=True)
parser.add_argument('--archive',type=Path,required=True)
a=parser.parse_args();root=a.repo.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
spec={
'R01_inertia_frame':('analysis/rocket_recovery/chrono_leg_model.py',109,127),
'R01_body_inertia_application':('analysis/rocket_recovery/chrono_leg_model.py',988,1016),
'R02_collision_geometry':('analysis/rocket_recovery/chrono_leg_model.py',1495,1535),
'R02_collision_pose':('analysis/rocket_recovery/chrono_leg_model.py',1717,1736),
'R02_legacy_plane':('analysis/rocket_recovery/chrono_leg_model.py',626,650),
'R03_actual_resampler':('analysis/rocket_recovery/chrono_two_way_recovery.py',784,816),
'R03_actual_caller':('analysis/rocket_recovery/chrono_same_platform_multibody.py',193,214),
'R04_compact_retention':('analysis/rocket_recovery/chrono_same_platform_multibody.py',256,273),
'R05_force_definition':('analysis/rocket_recovery/chrono_leg_model.py',1808,1829),
'R06_work_reference':('analysis/rocket_recovery/chrono_same_platform_multibody.py',65,103),
'R07_study_counts':('analysis/rocket_recovery/chrono_same_platform_multibody.py',370,405),
'R08_memory_initialization':('analysis/rocket_recovery/chrono_revision_study.py',653,704),
'R09_certificate_comparator':('CertTest/test_cert.py',1,93),
'R10_reference_alignment':('analysis/rocket_recovery/yang_2026_landing_identification.py',91,132),
'R10_optimizer':('analysis/rocket_recovery/yang_2026_landing_identification.py',260,327),
}
result=[]
for issue,(file,start,end) in spec.items():
 p=root/file;lines=p.read_text().splitlines();result.append({'issue':issue,'archive_member':file,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'start_line':start,'end_line':end,'extracted_text':'\n'.join(f'{i}: {lines[i-1]}' for i in range(start,min(end,len(lines))+1))})
(out/'code_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(out/'code_evidence.md').write_text('# 原始代码定位证据\n\n'+'\n\n'.join(f"## {x['issue']}\n\n`{x['archive_member']}`，原文件第{x['start_line']}–{x['end_line']}行。\n\nSHA-256 `{x['sha256']}`\n\n```text\n{x['extracted_text']}\n```" for x in result))
# Verify extracted source bytes against ZIP CRC (hash manifest separately retained).
zpath=a.archive
import zlib
with zipfile.ZipFile(zpath) as z:
 vals=[]
 for info in z.infolist():
  if info.is_dir():continue
  p=root/info.filename
  crc=zlib.crc32(p.read_bytes()) if p.exists() else None
  vals.append({'member':info.filename,'matches_crc_and_size':p.exists() and p.stat().st_size==info.file_size and crc==info.CRC})
seal={'archive_sha256':hashlib.sha256(zpath.read_bytes()).hexdigest(),'archive_bytes':zpath.stat().st_size,'file_members':len(vals),'unchanged_member_count':sum(x['matches_crc_and_size'] for x in vals),'nonmatching':[x for x in vals if not x['matches_crc_and_size']],'method':'Every ZIP file member checked against extracted size and CRC; full SHA-256 source manifest stored separately. Original archive not modified.'}
(out/'source_seal.json').write_text(json.dumps(seal,ensure_ascii=False,indent=2))
print(seal)
