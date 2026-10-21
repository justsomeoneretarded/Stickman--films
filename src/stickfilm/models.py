"""Versioned free model downloads, bounded retries, pinned SHA-256 checks."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request

# Hashes are populated from locally verified downloads in config/models.json.
ROOT=Path(__file__).resolve().parents[2]


def fetch(url,destination,expected=None):
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    def checksum(p):
        h=hashlib.sha256()
        with p.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
        return h.hexdigest()
    if destination.exists() and expected and checksum(destination)==expected:return
    temporary=destination.with_suffix(destination.suffix+'.part')
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url,timeout=90) as response, temporary.open('wb') as f:
                while block:=response.read(1024*1024):f.write(block)
            actual=checksum(temporary)
            if expected and actual!=expected:raise ValueError(f'Checksum mismatch for {destination.name}')
            temporary.replace(destination);return
        except Exception:
            temporary.unlink(missing_ok=True)
            if attempt==2:raise
            time.sleep(2**attempt)


def download(directory,local=False):
    manifest=json.loads((ROOT/'config/models.json').read_text())
    for key,item in manifest.items():
        if key=='writer' and not local:continue
        fetch(item['url'],Path(directory)/item['file'],item['sha256'])
