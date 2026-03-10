#!/usr/bin/env python3
"""
Interactive pre-PR checklist (local).

Automatically gathers changed files against the repository default branch
and walks the author through the educational PR checklist in the terminal.

Usage:
  python .github/scripts/pre_pr_interactive.py

The script prints a final checklist and copies it to the clipboard (Windows `clip`) when available.
"""
import subprocess
import sys
import os
import re


def run(cmd):
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def detect_base_branch():
    # Try to infer origin default branch
    try:
        out = run("git rev-parse --abbrev-ref origin/HEAD")
        # origin/main or origin/HEAD -> parse
        if out.startswith('origin/'):
            return out.split('/', 1)[1]
    except Exception:
        pass
    # fallback common names
    for b in ('main', 'master'):
        try:
            run(f'git rev-parse --verify origin/{b}')
            return b
        except Exception:
            continue
    return 'main'


def gather_changed_files(base):
    try:
        # fetch base to ensure up-to-date
        subprocess.run(f'git fetch origin {base}', shell=True, check=False)
        out = run(f'git diff --name-only origin/{base}...HEAD')
        files = [l for l in out.splitlines() if l.strip()]
        return files
    except Exception:
        return []


def get_latest_commit_title_and_body():
    try:
        title = run('git log -1 --pretty=%s')
        body = run('git log -1 --pretty=%b')
        return title, body
    except Exception:
        return '', ''


def detect_issues(files):
    issues = {}
    prohibited_roots = ('utils/', 'helpers/', 'services/', 'components/')
    found_prohibited = [f for f in files if any(f.startswith(p) for p in prohibited_roots)]
    issues['no_root_utils'] = len(found_prohibited) == 0
    issues['found_prohibited_files'] = found_prohibited

    data_paths = [f for f in files if '/src/data/' in f or f.startswith('data/') or '/data/' in f]
    issues['data_location_ok'] = len(data_paths) > 0
    issues['data_paths'] = data_paths

    issues['screaming_arch_ok'] = issues['no_root_utils']
    return issues


def ask_yes_no(prompt, default='y'):
    choices = '(Y/n)' if default == 'y' else '(y/N)'
    while True:
        ans = input(f"{prompt} {choices}: ").strip().lower()
        if ans == '' and default:
            return default == 'y'
        if ans in ('y', 'yes'):
            return True
        if ans in ('n', 'no'):
            return False


def main():
    print('Gathering repository info...')
    base = detect_base_branch()
    print(f'Using base branch: {base}')
    files = gather_changed_files(base)
    print(f'Found {len(files)} changed file(s).')

    title, body = get_latest_commit_title_and_body()
    if not title:
        title = input('PR title (suggested): ').strip()
    else:
        print('\nDetected PR title from latest commit:')
        print(title)
        if ask_yes_no('Use this as PR title?', default='y'):
            pass
        else:
            title = input('PR title: ').strip()

    if not body:
        body = input('PR short description: ').strip()
    else:
        print('\nDetected PR description from latest commit body:')
        print(body or '(empty)')
        if not ask_yes_no('Use this as PR description?', default='y'):
            body = input('PR short description: ').strip()

    issues = detect_issues(files)

    # Checklist items (order matches PULL_REQUEST_TEMPLATE.md)
    items = []

    # 1 People-First & Simplicity (subjective)
    items.append({
        'text': 'I verified this change follows the People-First & Simplicity principle (clear, maintainable code).',
        'auto': False,
        'result': ask_yes_no('\nDoes this change follow People-First & Simplicity (clear, maintainable)?', default='y')
    })

    # 2 Screaming Architecture (subjective but we check root utils)
    items.append({
        'text': 'The change follows Screaming Architecture (feature/vertical-slice organization) where applicable.',
        'auto': True,
        'evidence': issues['found_prohibited_files'],
        'result': issues['screaming_arch_ok'] or ask_yes_no('Screaming Architecture check failed heuristically. Confirm manually?', default='n')
    })

    # 3 No new root utils/helpers/services
    items.append({
        'text': "No new generic `utils/`, `helpers/`, or `services/` were added at the repository root without documented justification.",
        'auto': True,
        'evidence': issues['found_prohibited_files'],
        'result': issues['no_root_utils']
    })

    # 4 Data location
    items.append({
        'text': 'Data/config was added under `src/data/` (or `data/` with justification) and exported as a single well-typed constant when applicable.',
        'auto': True,
        'evidence': issues['data_paths'],
        'result': issues['data_location_ok'] or ask_yes_no('No data files detected under `src/data/`. Is this OK (provide justification)?', default='n')
    })

    # 5 Airplane Mode (subjective)
    items.append({
        'text': 'The change preserves or documents Airplane Mode requirements (local mocks, no runtime external deps for dev/tests).',
        'auto': False,
        'result': ask_yes_no('Does this change preserve or document Airplane Mode requirements?', default='y')
    })

    # 6 Shared-library exception documented
    items.append({
        'text': 'Any shared-library or cross-feature exception is documented in the repo README or exceptions file with rationale.',
        'auto': False,
        'result': ask_yes_no('Any shared-library exceptions documented in README/exceptions?', default='y')
    })

    # 7 Tests + Last Day
    items.append({
        'text': 'The author included tests or a clear testing note, and the change leaves the repo in a releasable state (Last Day).',
        'auto': False,
        'result': ask_yes_no('Are tests included or a testing note present, and is the repo left in a releasable state?', default='y')
    })

    # 8 Performance optimizations documented
    items.append({
        'text': 'Performance optimizations are documented and justified with benchmarks if they reduce readability.',
        'auto': False,
        'result': ask_yes_no('Any performance optimizations that reduce readability documented and justified?', default='y')
    })

    # Build final checklist text
    checklist_lines = []
    checklist_lines.append(f"# PR Checklist for: {title}\n")
    checklist_lines.append(body + "\n")
    for it in items:
        mark = 'x' if it['result'] else ' '
        checklist_lines.append(f"- [{mark}] {it['text']}")
        if it.get('evidence'):
            ev = it['evidence']
            if ev:
                checklist_lines.append('  Evidence:')
                for e in ev[:20]:
                    checklist_lines.append(f'  - {e}')

    output = '\n'.join(checklist_lines)

    out_path = '.github/pre_pr_check_result.md'
    os.makedirs('.github', exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print('\n--- Pre-PR Checklist ---\n')
    print(output)

    # Try to copy to clipboard on Windows using clip
    try:
        p = subprocess.Popen('clip', stdin=subprocess.PIPE, shell=True)
        p.communicate(output.encode('utf-8'))
        print('\nChecklist copied to clipboard (Windows clip).')
    except Exception:
        print('\nCould not copy to clipboard automatically. Checklist saved to', out_path)

    print('\nYou can paste the checklist into PR body or rely on the automated Action to re-check after opening the PR.')

    # Offer to create PR via GitHub CLI
    try:
        gh_check = subprocess.run('gh --version', shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if gh_check.returncode == 0:
            if ask_yes_no('\nCreate a GitHub PR now using `gh` CLI with this checklist as the PR body?', default='y'):
                try:
                    current_branch = run('git rev-parse --abbrev-ref HEAD')
                except Exception:
                    current_branch = ''
                base_branch = base
                if not current_branch:
                    current_branch = input('Enter the branch name to create the PR from: ').strip()
                cmd = f'gh pr create --base {base_branch} --head {current_branch} --title "{title.replace("\"","\\\"")}" --body-file {out_path}'
                print('Running:', cmd)
                rc = subprocess.run(cmd, shell=True)
                if rc.returncode == 0:
                    print('\nPR created successfully via gh.')
                else:
                    print('\nFailed to create PR via gh. Return code:', rc.returncode)
        else:
            print('\n`gh` CLI not detected; skipping automatic PR creation.')
    except Exception:
        print('\nError while attempting to run `gh`. Skipping automatic PR creation.')


if __name__ == '__main__':
    main()
