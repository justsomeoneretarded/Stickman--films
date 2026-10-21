"""Aggregate successful and failed niche outputs without invented rankings."""
import json
from pathlib import Path
from .schema import NICHES


def compare(directory,destination):
    root=Path(directory);reports={}
    for p in root.rglob('quality-report.json'):
        try:
            r=json.loads(p.read_text());plan=json.loads((p.parent/'plan.json').read_text())
            reports[plan['niche']]=(r,p.parent)
        except (ValueError,OSError):continue
    lines=['# Ten-niche production comparison','','Technical results and creative judgments are separate. Missing reports remain missing, never inferred successful.','','| Niche | Technical gates | Duration | Target | Review |','|---|---|---|---|---|']
    for niche in NICHES:
        if niche not in reports:lines.append(f'| {niche} | MISSING / FAILED | — | — | inspect job diagnostics |');continue
        r,p=reports[niche]
        lines.append(f'| {niche} | {"PASS" if r["technical_pass"] else "FAIL"} | {r["actual_seconds"]:.2f}s | {r["requested_seconds"]:.2f}s | {r["artistic_review"]["status"]} |')
    lines+=['','## Creative fit (engineering judgment, not an audience study)','','The finite prop/action vocabulary is best suited to small character stories, gentle comedy and practical habit examples. Science, history and cybersecurity need additional bespoke demonstrations, maps and diagrams; a technically valid render does not establish educational accuracy or visual completeness. The fictional history and survival samples are not factual documentaries or safety guidance.','','No niche has been assigned an invented quality score. Review each contact sheet, playback and audio before choosing a channel direction.','','## Review priorities','','1. Inspect foot contact in the benchmark preview and the full 60 FPS file.','2. Listen for pronunciation, missing words, voice fatigue and music balance.','3. Verify important spoken actions actually appear; extend the rig/props where they do not.','4. Review factual claims against the source notes.','5. Review whole scenes for timing and emotional impact; thumbnails cannot establish these.']
    dest=Path(destination);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('\n'.join(lines)+'\n')
