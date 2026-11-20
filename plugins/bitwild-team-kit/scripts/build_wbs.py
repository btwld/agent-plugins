#!/usr/bin/env python3
"""Validate one WBS data file and render linked HTML/PDF review views.

Only the Python standard library is required. PDF export uses Chrome/Chromium.
Dates are calendar dates and intervals are start-inclusive, end-exclusive.
"""
import argparse
from collections import Counter
from datetime import date, timedelta
from html import escape
import hashlib
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time

from json_io import parse_json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def day(value):
    check(isinstance(value, str) and re.fullmatch(r'\d{4}-\d{2}-\d{2}', value), f'Invalid ISO date: {value!r}')
    return date.fromisoformat(value)


def keyed(rows, label):
    check(isinstance(rows, list), f'{label} must be a list')
    result = {}
    for row in rows:
        check(isinstance(row, dict), f'{label} entries must be objects')
        key = row.get('id')
        check(isinstance(key, str) and key.strip(), f'{label}: missing ID')
        check(key not in result, f'{label}: duplicate ID {key}')
        result[key] = row
    return result


def text_fields(row, fields, label):
    for field in fields:
        check(isinstance(row.get(field), str) and row[field].strip(), f'{label}: missing text {field}')


def bounds(package):
    return day(package['stages'][0]['start']), day(package['stages'][-1]['end'])


def validate(data):
    project = data['project']
    text_fields(project, ['name', 'subtitle', 'status', 'owner', 'baseline'], 'project')
    start, end = day(project['start']), day(project['end'])
    check(start < end, 'Project end must follow start')
    check((end - start).days <= 730, 'Split plans longer than two years into separate reviews')
    maps = {k: keyed(data[k], k) for k in ['stages', 'releases', 'groups', 'packages', 'milestones', 'requirements']}
    stages, releases, groups, packages, milestones, requirements = (maps[k] for k in ['stages', 'releases', 'groups', 'packages', 'milestones', 'requirements'])
    check(stages and groups and packages and requirements, 'Stages, groups, packages, and requirements cannot be empty')
    for s in stages.values():
        text_fields(s, ['name'], s['id'])
        check(re.fullmatch(r'#[0-9A-Fa-f]{6}', s.get('color', '')), f"{s['id']}: invalid color")
    for g in groups.values():
        text_fields(g, ['name'], g['id'])
    for r in releases.values():
        text_fields(r, ['name'], r['id'])
        check(start <= day(r['start']) < day(r['end']) <= end, f"{r['id']}: release outside project window")
    dispositions = {'Current', 'Optional', 'Deferred', 'Excluded'}
    for req in requirements.values():
        text_fields(req, ['title', 'statement', 'source'], req['id'])
        check(req['disposition'] in dispositions, f"{req['id']}: invalid disposition")
    assigned = {}
    for p in packages.values():
        pid = p['id']
        text_fields(p, ['name', 'owner', 'deliverable', 'done'], pid)
        check(p['group'] in groups, f'{pid}: unknown group')
        check(p['disposition'] in dispositions, f'{pid}: invalid disposition')
        for field in ['stages', 'dependencies', 'requirements']:
            check(isinstance(p[field], list), f'{pid}: {field} must be a list')
        check(len(p['dependencies']) == len(set(p['dependencies'])), f'{pid}: duplicate dependencies')
        if p['disposition'] == 'Current':
            check(p['release'] in releases and p['stages'], f'{pid}: current package needs release and stages')
        else:
            check(p['release'] is None and not p['stages'] and not p['dependencies'], f'{pid}: non-current scope must remain unscheduled')
        previous_end = start
        stage_order = -1
        for segment in p['stages']:
            check(segment['stage'] in stages, f'{pid}: unknown stage')
            index = list(stages).index(segment['stage'])
            check(index > stage_order, f'{pid}: stages repeated or out of order')
            stage_order = index
            a, b = day(segment['start']), day(segment['end'])
            check(start <= a < b <= end, f'{pid}: stage outside project window or empty')
            check(a >= previous_end, f'{pid}: stages overlap or are not ordered')
            previous_end = b
        if p['stages']:
            a, b = bounds(p)
            r = releases[p['release']]
            check(day(r['start']) <= a and b <= day(r['end']), f'{pid}: package outside its release window')
        for rid in p['requirements']:
            check(rid in requirements, f'{pid}: unknown requirement {rid}')
            check(rid not in assigned, f'{rid}: multiple primary WBS assignments')
            check(requirements[rid]['disposition'] == p['disposition'], f'{rid}: disposition differs from package')
            assigned[rid] = pid
    check(set(assigned) == set(requirements), f'Unassigned requirements: {sorted(set(requirements) - set(assigned))}')
    visited, visiting = set(), set()

    def visit(pid):
        check(pid not in visiting, f'Dependency cycle involving {pid}')
        if pid in visited:
            return
        visiting.add(pid)
        p = packages[pid]
        for dep in p['dependencies']:
            check(dep in packages, f'{pid}: unknown dependency {dep}')
            check(packages[dep]['stages'] and p['stages'], f'{pid}: dependency must be scheduled')
            visit(dep)
            check(bounds(packages[dep])[1] <= bounds(p)[0], f'{pid}: starts before dependency {dep} finishes')
        visiting.remove(pid)
        visited.add(pid)

    for pid in packages:
        visit(pid)
    for m in milestones.values():
        text_fields(m, ['name', 'owner', 'evidence', 'status'], m['id'])
        check(m['release'] in releases, f"{m['id']}: unknown release")
        r = releases[m['release']]
        when = day(m['date'])
        check(day(r['start']) <= when <= day(r['end']), f"{m['id']}: gate outside release")
        check(isinstance(m['requires'], list), f"{m['id']}: requires must be a list")
        for pid in m['requires']:
            check(pid in packages and packages[pid]['stages'], f"{m['id']}: unknown or unscheduled package {pid}")
            check(bounds(packages[pid])[1] <= when, f"{m['id']}: gate precedes package {pid} completion")
    return maps, assigned


def h(value):
    return escape(str(value), quote=True)


def table(headings, rows):
    return '<table><thead><tr>' + ''.join(f'<th>{h(v)}</th>' for v in headings) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{h(v)}</td>' for v in row) + '</tr>' for row in rows) + '</tbody></table>'


def timeline(data, maps):
    start, end = day(data['project']['start']), day(data['project']['end'])
    scheduled = [p for g in data['groups'] for p in data['packages'] if p['group'] == g['id'] and p['stages']]
    panels = []
    # A bounded number of columns and rows keeps long plans legible in print.
    for offset in range(0, (end - start).days, 84):
        a, b = start + timedelta(days=offset), min(end, start + timedelta(days=offset + 84))
        for chunk in range(0, len(scheduled), 10):
            items = scheduled[chunk:chunk + 10]
            left, width, row_h = 310, 780, 31
            duration = (b - a).days
            x = lambda d: left + ((d - a).days / duration) * width
            svg = []

            def text(xv, yv, value, size=12, weight='normal', anchor='start', color='#19354b'):
                svg.append(f'<text x="{xv:.1f}" y="{yv:.1f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{h(value)}</text>')

            def rect(xv, yv, w, hh, color):
                svg.append(f'<rect x="{xv:.1f}" y="{yv:.1f}" width="{w:.1f}" height="{hh:.1f}" fill="{color}"/>')

            text(8, 20, 'WBS / WORK PACKAGE', 12, 'bold')
            y = 32
            for r in data['releases']:
                ra, rb = max(a, day(r['start'])), min(b, day(r['end']))
                if ra < rb:
                    text(8, y + 14, r['name'], 11, 'bold')
                    rect(x(ra), y, x(rb) - x(ra), 20, '#e3def5')
                    y += 25
            y += 35
            grid_top = y - 28
            row_positions = {}
            group_id = None
            for p in items:
                if p['group'] != group_id:
                    group_id = p['group']
                    rect(0, y, 1100, row_h, '#e8eef3')
                    group_name = maps['groups'][group_id]['name']
                    text(8, y + 20, f'{group_id}  {group_name}', 12, 'bold')
                    y += row_h
                rect(0, y, 1100, row_h, '#f8fafc' if len(row_positions) % 2 == 0 else '#ffffff')
                label = f"{p['id']}  {p['name']}"
                # Full names remain in the dictionary; do not shrink labels indefinitely.
                text(12, y + 20, label if len(label) < 39 else label[:36] + '...', 12)
                row_positions[p['id']] = y + row_h / 2
                for seg in p['stages']:
                    sa, sb = max(a, day(seg['start'])), min(b, day(seg['end']))
                    if sa < sb:
                        color = maps['stages'][seg['stage']]['color']
                        rect(x(sa), y + 7, x(sb) - x(sa), 17, color)
                y += row_h
            for week in range(math.ceil(duration / 7) + 1):
                d = min(b, a + timedelta(days=week * 7))
                xx = x(d)
                svg.append(f'<path d="M{xx} {grid_top} V{y}" stroke="#cfd9e1" stroke-width="0.65"/>')
                if d < b:
                    text(xx + 5, grid_top + 10, f'W{offset // 7 + week + 1}', 11, 'bold')
                    text(xx + 5, grid_top + 23, d.strftime('%d %b'), 10)
            svg.append('<defs><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#29445c"/></marker></defs>')
            for p in items:
                for dep in p['dependencies']:
                    da, db = bounds(maps['packages'][dep])[1], bounds(p)[0]
                    if dep in row_positions and a <= da < b and a <= db < b:
                        sx, tx = x(da), x(db)
                        sy, ty = row_positions[dep], row_positions[p['id']]
                        bend = max(sx + 5, tx - 6)
                        svg.append(f'<path d="M{sx},{sy} H{bend} V{ty} H{tx}" fill="none" stroke="#29445c" stroke-width="1.3" marker-end="url(#arrow)"/>')
            y += 12
            for m in data['milestones']:
                d = day(m['date'])
                if a <= d < b or d == b == end:
                    xx = min(x(d), 1090)
                    text(8, y + 16, f"{m['id']}  {m['name']}", 11)
                    svg.append(f'<path d="M{xx},{y+3} l7,7 l-7,7 l-7,-7 z" fill="#183d5c"/>')
                    text(min(xx + 12, 1080), y + 15, m['date'], 10, anchor='end' if xx > 980 else 'start')
                    y += 24
            svg_text = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1110 {y + 8}" role="img" aria-label="Grouped work package timeline" font-family="Arial, sans-serif">' + ''.join(svg) + '</svg>'
            legend = '<div class="legend">' + ''.join(f'<span><i style="background:{s["color"]}"></i>{h(s["name"])}</span>' for s in data['stages']) + '<span>◆ Gate</span></div>'
            panels.append(f'<section class="timeline"><h2>Grouped delivery roadmap</h2><p>{a.isoformat()} to {b.isoformat()} · package rows {chunk + 1}–{chunk + len(items)} of {len(scheduled)}</p>{svg_text}{legend}</section>')
    return ''.join(panels)


CSS = '''
@page { size: A4 landscape; margin: 13mm 14mm; }
* { box-sizing: border-box; }
body { margin: 0; font: 11px/1.5 Arial, sans-serif; color: #19354b; background: #edf2f6; }
main { max-width: 1180px; margin: 24px auto; padding: 32px; background: white; }
h1 { font-size: 30px; margin: 6px 0; line-height: 1.15; }
h2 { font-size: 19px; margin: 20px 0 8px; }
h3 { font-size: 14px; margin: 10px 0 6px; }
p { margin: 6px 0 10px; }
.eyebrow { text-transform: uppercase; letter-spacing: 1.4px; font-size: 10px; }
.status { color: #73521b; font-weight: bold; }
.meta { display: flex; gap: 22px; flex-wrap: wrap; border-bottom: 1px solid #cad5de; padding-bottom: 12px; }
.legend { display: flex; flex-wrap: wrap; gap: 16px; padding: 10px 0; }
.legend i { display: inline-block; width: 13px; height: 10px; margin-right: 5px; }
svg { width: 100%; display: block; }
table { width: 100%; border-collapse: collapse; margin: 10px 0 18px; table-layout: auto; }
th { color: white; background: #203e56; text-align: left; }
td, th { border: 1px solid #d4dde5; padding: 7px 9px; vertical-align: top; overflow-wrap: anywhere; }
tr:nth-child(even) td { background: #f2f5f8; }
thead { display: table-header-group; }
tr, .package { break-inside: avoid; }
.package { border-top: 2px solid #d5e2eb; padding: 4px 0 7px; }
.package p { margin: 2px 0; }
.tag { font-size: 10px; color: #506777; }
.muted { color: #536a7b; }
.actions { text-align: right; }
button { padding: 8px 14px; cursor: pointer; border: 1px solid #b7c6d0; background: white; color: #19354b; }
@media print {
 body { background: white; font-size: 10px; }
 main { margin: 0; padding: 0; max-width: none; }
 .actions { display: none; }
 .timeline { break-before: page; break-inside: avoid; }
 .section { break-before: page; }
 h2, h3 { break-after: avoid; }
 * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
'''


def render(data, maps, assigned, digest):
    p = data['project']
    counts = Counter(r['disposition'] for r in data['requirements'])
    content = f'<div class="actions"><button onclick="window.print()">Print / Save PDF</button></div><p class="eyebrow">Delivery planning</p><h1>{h(p["name"])}</h1><h2>{h(p["subtitle"])}</h2><p class="status">{h(p["status"])}</p>'
    content += f'<div class="meta"><span>Owner: {h(p["owner"])}</span><span>Window: {h(p["start"])} to {h(p["end"])}</span><span>Source fingerprint: {digest}</span></div><p>Baseline: {h(p["baseline"])}</p>'
    content += '<h2>How to read this review</h2>' + table(['Part', 'What it tells you'], [
        ['1 Work hierarchy', 'Groups organize numbered work packages.'], ['2 Package definition', 'Deliverable, owner, dependencies, and completion evidence.'],
        ['3 Dates and dependencies', 'Calendar windows and finish-to-start prerequisites.'], ['4 Lifecycle stages', 'The colored steps inside a work package.'],
        ['5 Releases and gates', 'Delivery membership, readiness checkpoints, and acceptance evidence.'], ['6 Requirement coverage', 'Every supplied requirement has one primary package, including later scope.']])
    content += '<h2>Scope at a glance</h2>' + table(['Disposition', 'Requirements'], sorted(counts.items()))
    content += '<p class="muted">Structural checks passed for the supplied data. This does not approve scope, confirm estimates, or prove completeness against evidence not supplied. End dates are exclusive boundaries. Arrows show finish-to-start dependencies when both endpoints are in the same timeline panel; all dependencies are listed in the dictionary.</p>'
    content += timeline(data, maps)
    content += '<section class="section"><h2>Scheduled work package dictionary</h2>'
    for group in data['groups']:
        if not any(i['group'] == group['id'] and i['stages'] for i in data['packages']):
            continue
        content += f'<h3>{h(group["id"])} {h(group["name"])}</h3>'
        for item in data['packages']:
            if item['group'] != group['id'] or not item['stages']:
                continue
            release = maps['releases'][item['release']]['name'] if item['release'] else 'Not scheduled'
            window = ' to '.join(map(str, bounds(item))) if item['stages'] else 'Not scheduled'
            content += f'<article class="package"><h3>{h(item["id"])} {h(item["name"])}</h3><p class="tag">{h(item["disposition"])} · {h(release)} · {h(window)}</p>'
            for label, value in [('Deliverable', item['deliverable']), ('Owner', item['owner']), ('Done when', item['done']), ('Depends on', ', '.join(item['dependencies']) or 'None'), ('Requirements', ', '.join(item['requirements']) or 'No controlled requirement assigned')]:
                content += f'<p><b>{label}:</b> {h(value)}</p>'
            if item['stages']:
                content += '<p><b>Stages:</b> ' + h(' · '.join(f"{maps['stages'][s['stage']]['name']} {s['start']} to {s['end']}" for s in item['stages'])) + '</p>'
            content += '</article>'
    content += '</section><section class="section"><h2>Release gates and acceptance evidence</h2>'
    content += table(['Gate', 'Date / release', 'Prerequisites', 'Owner / status', 'Required evidence'], [(f"{m['id']} {m['name']}", f"{m['date']} / {maps['releases'][m['release']]['name']}", ', '.join(m['requires']), f"{m['owner']} / {m['status']}", m['evidence']) for m in data['milestones']])
    content += '<h2>Unscheduled work package dictionary</h2><p>Later, optional, and excluded scope remains outside the delivery roadmap.</p>' + table(['Group / package', 'Disposition / owner', 'Deliverable', 'Condition before delivery', 'Requirements'], [(f"{maps['groups'][i['group']]['name']} / {i['id']} {i['name']}", f"{i['disposition']} / {i['owner']}", i['deliverable'], i['done'], ', '.join(i['requirements']) or 'None') for i in data['packages'] if i['disposition'] != 'Current'])
    content += '<h2>Review response</h2><p>Response: Accept / Accept with recorded changes / Needs discussion</p><p>Reviewer and date: __________________________________________</p><p>Requested changes and affected IDs: __________________________________________</p><p>Approval record: __________________________________________</p></section>'
    content += '<section class="section"><h2>Requirement coverage</h2><p>One primary package per supplied requirement. Statements and source references are retained below.</p>'
    content += table(['Requirement', 'Exact statement', 'Primary package', 'Disposition / release', 'Source'], [(f"{r['id']} {r['title']}", r['statement'], assigned[r['id']], f"{r['disposition']} / " + (maps['releases'][maps['packages'][assigned[r['id']]]['release']]['name'] if maps['packages'][assigned[r['id']]]['release'] else 'Not scheduled'), r['source']) for r in data['requirements']])
    content += '</section>'
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>' + h(p['name'] + ' - WBS review') + '</title><style>' + CSS + '</style></head><body><main>' + content + '</main></body></html>'


def export_pdf(html_path, pdf_path, chrome=None):
    executable = chrome or os.environ.get('CHROME_BIN') or shutil.which('chromium') or shutil.which('google-chrome')
    if not executable:
        candidate = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        if candidate.exists():
            executable = str(candidate)
    check(executable, 'PDF export needs Chrome/Chromium; pass --chrome or set CHROME_BIN. HTML generation works without it.')
    # Isolate the export from the user's running browser and stage the output so
    # failed exports cannot be mistaken for an old successful PDF.
    with tempfile.TemporaryDirectory(prefix='wbs-pdf-') as tmp:
        staged = Path(tmp) / 'review.pdf'
        command = [executable, '--headless', '--disable-gpu', '--no-first-run', '--no-default-browser-check', '--disable-background-networking', '--no-pdf-header-footer', f'--user-data-dir={tmp}/profile', f'--print-to-pdf={staged}', html_path.resolve().as_uri()]
        with (Path(tmp) / 'chrome.log').open('w+') as log:
            process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=log)
            try:
                deadline, previous_size, complete = time.monotonic() + 90, None, False
                while time.monotonic() < deadline:
                    if staged.exists():
                        blob = staged.read_bytes()
                        complete = blob.startswith(b'%PDF') and b'%%EOF' in blob[-1024:] and len(blob) == previous_size
                        if complete:
                            break
                        previous_size = len(blob)
                    if process.poll() is not None:
                        # Allow one final stable-size check after normal exit.
                        if staged.exists() and previous_size:
                            time.sleep(.2)
                            blob = staged.read_bytes()
                            complete = blob.startswith(b'%PDF') and b'%%EOF' in blob[-1024:] and len(blob) == previous_size
                        break
                    time.sleep(.2)
                log.seek(0)
                check(complete, 'Chrome PDF export failed or timed out: ' + log.read()[-800:])
            finally:
                # Some Chrome builds remain alive after successful printing.
                # Stop only this isolated exporter, never an existing browser.
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
        shutil.copyfile(staged, pdf_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--out', type=Path, help='Output directory; required unless --check')
    parser.add_argument('--check', action='store_true', help='Validate without writing outputs')
    parser.add_argument('--pdf', action='store_true')
    parser.add_argument('--chrome')
    args = parser.parse_args()
    try:
        raw = args.data.read_bytes()
        data = parse_json(raw)
        maps, assigned = validate(data)
        if args.check:
            print(f'Valid: {len(maps["packages"])} packages; {len(assigned)} requirements assigned exactly once')
            return
        check(args.out is not None, '--out is required to generate documents')
        args.out.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(raw).hexdigest()[:16]
        html_path = args.out / 'wbs-review.html'
        html_path.write_text(render(data, maps, assigned, digest))
        print(html_path)
        if args.pdf:
            pdf_path = args.out / 'wbs-review.pdf'
            export_pdf(html_path, pdf_path, args.chrome)
            print(pdf_path)
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'WBS build failed: {exc}\n')


if __name__ == '__main__':
    main()
