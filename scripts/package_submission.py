"""Package the reviewed Agent Rush upload files without private project state."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission/agent-rush'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fields = json.loads((OUT / 'submission.json').read_text(encoding='utf-8'))
    limits = {'title': (5, 50), 'short_description': (50, 255), 'long_description': (600, 2000)}
    counts = {}
    for key, (low, high) in limits.items():
        value = (OUT / (key + '.txt')).read_text(encoding='utf-8-sig').strip()
        assert value == fields[key], f'{key} differs from submission.json'
        counts[key] = len(value)
        assert low <= len(value) <= high, (key, len(value))
    assert fields['video'] == 'video-v2/prooflane-live-demo.mp4'
    assert (OUT / fields['video']).stat().st_size < 300_000_000
    (OUT / 'field-validation.json').write_text(json.dumps({
        'counts': counts, 'limits': limits, 'passed': True,
        'scope': 'Published standard limits; authenticated event form not inspected'
    }, indent=2) + '\n', encoding='utf-8', newline='\n')
    names = ['README.md', 'title.txt', 'short_description.txt', 'long_description.txt',
             'submission.json', 'field-validation.json', 'prooflane-deck.pdf',
             'prooflane-deck.pptx', 'cover.png']
    names += [p.relative_to(OUT).as_posix() for p in sorted((OUT / 'video-v2').rglob('*')) if p.is_file()]
    for name in names:
        path = OUT / name
        if path.suffix in {'.md', '.txt', '.json', '.srt'}:
            path.write_text(path.read_text(encoding='utf-8-sig'), encoding='utf-8', newline='\n')
    records = [{'path': n, 'bytes': (OUT / n).stat().st_size, 'sha256': digest(OUT / n)} for n in names]
    manifest = {'files': records, 'note': 'Updated submission files only; no secrets, databases or raw recording cache. Code is in public GitHub. ElevenLabs audio retains separate noncommercial attribution terms.',
                'hash_scope': 'Exact file bytes; scoped text eol=lf, media binary.'}
    (OUT / 'bundle-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
    (OUT / 'SHA256SUMS.txt').write_text(''.join(f"{r['sha256']}  {r['path']}\n" for r in records), encoding='utf-8', newline='\n')
    archive = OUT / 'prooflane-submission.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for name in names + ['bundle-manifest.json', 'SHA256SUMS.txt']:
            bundle.write(OUT / name, name)
    with zipfile.ZipFile(archive) as bundle:
        assert bundle.testzip() is None
        for record in records:
            assert hashlib.sha256(bundle.read(record['path'])).hexdigest() == record['sha256']
    result = {'files': len(records), 'zip_bytes': archive.stat().st_size,
              'zip_sha256': digest(archive), 'zip_crc_passed': True, 'all_file_hashes_passed': True}
    report = ROOT / 'artifacts/live-demo-v2/packaging.json'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
