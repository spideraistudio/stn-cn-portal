"""Verify preserved baseline source; ignores generated caches/runtime databases."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'baseline_manifest.json').read_text())
omitted=[]
private=set('fixtures/'+n for n in ('ashapura.pdf','ashapura_ipt.pdf','khammam_current_fy.pdf','khammam_previous_fy.pdf','krishna_ipt.pdf','maharashtra.pdf','surendranagar_combined.pdf'))
for name,expected in manifest['files'].items():
    path=root/'offline_baseline'/name
    if not path.is_file() and '--allow-private-fixtures' in sys.argv and name in private:
        omitted.append(name);continue
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
        raise SystemExit('Baseline mismatch: '+name)
print('PASS: '+str(len(manifest['files'])-len(omitted))+' preserved Update35.2 files match; '+str(len(omitted))+' private fixture PDFs intentionally absent.' if omitted else 'PASS: all '+str(len(manifest['files']))+' preserved Update35.2 files match.')
