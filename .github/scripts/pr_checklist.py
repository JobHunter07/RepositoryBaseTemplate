#!/usr/bin/env python3
import os
import sys
import json
import re
import requests

def read_changed_files(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [l.strip() for l in f.readlines() if l.strip()]

def detect_issues(files):
    issues = {}
    # Check: new root-level utils/helpers/services/components
    prohibited_roots = ('utils/', 'helpers/', 'services/', 'components/')
    found_prohibited = [f for f in files if any(f.startswith(p) or ('/' + p) in f for p in [pr.rstrip('/') for pr in prohibited_roots])]
    issues['no_root_utils'] = len(found_prohibited) == 0
    issues['found_prohibited_files'] = found_prohibited

    # Check: data files added under src/data or data/
    data_paths = [f for f in files if '/src/data/' in f or f.startswith('data/') or '/data/' in f]
    issues['data_location_ok'] = len(data_paths) > 0
    issues['data_paths'] = data_paths

    # Check: Screaming Architecture heuristic (no top-level generic components/services folders)
    issues['screaming_arch_ok'] = issues['no_root_utils']

    return issues

def github_request(method, url, token, payload=None):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github+json'
    }
    if method == 'GET':
        return requests.get(url, headers=headers)
    if method == 'PATCH':
        return requests.patch(url, headers=headers, json=payload)
    if method == 'POST':
        return requests.post(url, headers=headers, json=payload)

def update_pr_checklist(owner, repo, pr_number, token, results):
    pr_url = f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}'
    r = github_request('GET', pr_url, token)
    if r.status_code != 200:
        print('Failed to fetch PR', r.status_code, r.text)
        sys.exit(1)
    pr = r.json()
    body = pr.get('body') or ''

    # Mapping substrings to result keys
    mappings = [
        ("No new generic `utils/`, `helpers/`, or `services/` were added at the repository root without documented justification.", 'no_root_utils'),
        ("Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable.", 'data_location_ok'),
        ("The change follows _Screaming Architecture_ (feature/vertical-slice organization) where applicable.", 'screaming_arch_ok'),
    ]

    new_body = body
    for text, key in mappings:
        # find checkbox line containing the substring
        pattern = re.compile(r'(\- \[[ xX]\] .*' + re.escape(text) + r'.*)', re.DOTALL)
        m = pattern.search(new_body)
        checked = results.get(key, False)
        replacement = f"- [{'x' if checked else ' '}] {text}"
        if m:
            new_body = new_body.replace(m.group(1), replacement)
        else:
            # if not in body, append under checklist heading
            new_body += '\n' + replacement + '\n'

    patch = {'body': new_body}
    pr_patch = github_request('PATCH', pr_url, token, patch)
    if pr_patch.status_code not in (200, 201):
        print('Failed to update PR body', pr_patch.status_code, pr_patch.text)
        sys.exit(1)
    print('PR body updated with auto-checked results.')

def post_summary_comment(owner, repo, pr_number, token, results):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments'
    summary = ['Automated PR Checklist results:']
    if results['no_root_utils']:
        summary.append('- ✅ No new root `utils/helpers/services/components` detected')
    else:
        summary.append('- ❌ Found files in prohibited root folders:')
        for p in results.get('found_prohibited_files', [])[:10]:
            summary.append(f'  - {p}')
    if results['data_location_ok']:
        summary.append('- ✅ Data files are located under `src/data/` or `data/`')
    else:
        summary.append('- ⚠️ No data files were added under `src/data/` or `data/` in this PR (if you added config/data, please place under `src/data/` or justify in PR).')

    summary.append('\nNote: Some checklist items are subjective and require a human reviewer. This Action is educational and will not block merges.')
    payload = {'body': '\n'.join(summary)}
    r = github_request('POST', url, token, payload)
    if r.status_code not in (200,201):
        print('Failed to post comment', r.status_code, r.text)
        sys.exit(1)
    print('Posted summary comment on PR.')

def main():
    if len(sys.argv) < 2:
        print('Usage: pr_checklist.py <changed_files.txt>')
        sys.exit(2)
    changed_files_path = sys.argv[1]
    files = read_changed_files(changed_files_path)
    results = detect_issues(files)

    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path or not os.path.exists(event_path):
        print('GITHUB_EVENT_PATH not set; cannot update PR. Exiting (local run).')
        print('Detected results:', json.dumps(results, indent=2))
        return

    with open(event_path, 'r', encoding='utf-8') as f:
        event = json.load(f)

    pr = event.get('pull_request')
    if not pr:
        print('No pull_request object in event payload.')
        sys.exit(1)

    pr_number = pr['number']
    repo = event['repository']['name']
    owner = event['repository']['owner']['login']
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN is not set; cannot update PR.')
        sys.exit(1)

    # Update PR body checkboxes and post a summary comment
    update_pr_checklist(owner, repo, pr_number, token, results)
    post_summary_comment(owner, repo, pr_number, token, results)

if __name__ == '__main__':
    main()
