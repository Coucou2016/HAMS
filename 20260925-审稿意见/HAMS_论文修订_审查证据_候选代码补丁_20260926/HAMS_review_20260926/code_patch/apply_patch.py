#!/usr/bin/env python3
"""SHA-guarded installation of candidate review patches. Dry-run by default."""
from pathlib import Path
import argparse,hashlib,json,shutil
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--apply',action='store_true');a=p.parse_args()
repo=a.repo.resolve();bundle=Path(__file__).resolve().parent;manifest=json.loads((bundle/'expected_original_sha256.json').read_text())
if not (repo/'SourceCode').is_dir():raise SystemExit('Not the extracted HAMS project root')
for rel,digest in manifest.items():
 path=repo/rel
 if digest is None:
  if path.exists():raise SystemExit(f'Refuse to overwrite an existing new module: {path}')
 elif not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise SystemExit(f'Original SHA mismatch; reconcile local edits first: {rel}')
 print('VERIFIED',rel)
if not a.apply:
 print('Dry-run complete; add --apply to install on a working COPY of the project.')
 raise SystemExit(0)
backup=repo/'.review_20260926_backup';backup.mkdir(exist_ok=False)
for rel,digest in manifest.items():
 path=repo/rel
 if path.exists():
  dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
 path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(bundle/rel,path)
print('Candidate code installed. Full Chrono integration and research acceptance gates are still required.')
