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
    # Try to infer origin default branch, but fall back gracefully when remotes are missing.
    try:
        out = run("git rev-parse --abbrev-ref origin/HEAD")
        if out and out.startswith('origin/'):
            return out.split('/', 1)[1]
    except Exception:
        pass

    # If origin/HEAD not available, check common remote branches
    for b in ('main', 'master'):
        try:
            # check remote exists
            rc = subprocess.run(f'git ls-remote --exit-code --heads origin {b}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            if rc == 0:
                return b
        except Exception:
            continue

    # Last fallback: if no remote, try local main/master
    for b in ('main', 'master'):
        try:
            run(f'git rev-parse --verify {b}')
            return b
        except Exception:
            continue

    # Otherwise return the currently checked-out branch
    try:
        return run('git rev-parse --abbrev-ref HEAD')
    except Exception:
        return 'main'


def gather_changed_files(base):
    try:
        # Try to fetch the base branch from origin (if remote exists)
        subprocess.run(f'git fetch origin {base}', shell=True, check=False)

        # Prefer diff against origin/base when available, otherwise local base
        rc = subprocess.run(f'git rev-parse --verify --quiet origin/{base}', shell=True, stdout=subprocess.DEVNULL).returncode
        if rc == 0:
            diff_from = f'origin/{base}'
        else:
            # fallback to local base branch
            rc2 = subprocess.run(f'git rev-parse --verify --quiet {base}', shell=True, stdout=subprocess.DEVNULL).returncode
            if rc2 == 0:
                diff_from = base
            else:
                # no base found, diff against empty tree
                diff_from = ''

        if diff_from:
            out = run(f'git diff --name-only {diff_from}...HEAD')
        else:
            # list all tracked files as fallback (no base available)
            out = run('git ls-files')

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

    # detect current branch early
    try:
        current_branch = run('git rev-parse --abbrev-ref HEAD')
    except Exception:
        current_branch = ''

    # If on the base branch, create a new branch first (and optionally commit uncommitted changes)
    if current_branch and current_branch == base:
        print(f'You are on the base branch `{base}`.')
        # check for uncommitted changes
        status = ''
        try:
            status = run('git status --porcelain')
        except Exception:
            status = ''

        if status:
            print('Uncommitted changes detected:')
            print(status)
            if ask_yes_no('Commit uncommitted changes now before creating a PR branch?', default='y'):
                default_msg = ''
                try:
                    default_msg = run('git log -1 --pretty=%s')
                except Exception:
                    default_msg = 'chore: commit before PR'
                msg = input(f'Commit message (default: "{default_msg}"): ').strip() or default_msg
                subprocess.run('git add -A', shell=True)
                rc = subprocess.run(f'git commit -m "{msg.replace("\"","\\\"")}"', shell=True).returncode
                if rc != 0:
                    print('Failed to commit changes. Please commit manually and re-run the script.')
                    return
            else:
                print('Proceeding without committing uncommitted changes.')

        # create a new branch derived from base
        import re
        def slugify(s):
            s = s.lower()
            s = re.sub(r'[^a-z0-9]+', '-', s)
            s = s.strip('-')
            if len(s) > 50:
                s = s[:50].rstrip('-')
            return s or 'pr-branch'

        new_branch_base = f'pr/{slugify(get_latest_commit_title_and_body()[0] or "work")}'
        candidate = new_branch_base
        i = 0
        while True:
            exists_local = subprocess.run(f'git rev-parse --verify --quiet {candidate}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            exists_remote = subprocess.run(f'git ls-remote --exit-code --heads origin {candidate}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            if not (exists_local or exists_remote):
                break
            i += 1
            candidate = f'{new_branch_base}-{i}'

        new_branch = candidate
        print(f'Creating and checking out new branch `{new_branch}` from `{base}`...')
        subprocess.run(f'git fetch origin {base}', shell=True, check=False)
        rc = subprocess.run(f'git checkout {base}', shell=True).returncode
        if rc != 0:
            print(f'Failed to checkout {base}. Aborting.')
            return
        rc = subprocess.run(f'git checkout -b {new_branch}', shell=True).returncode
        if rc != 0:
            print(f'Failed to create branch {new_branch}. Aborting.')
            return
        rc = subprocess.run(f'git push -u origin {new_branch}', shell=True).returncode
        if rc != 0:
            print(f'Failed to push branch {new_branch} to origin. You may need to push manually later.')
        current_branch = new_branch

    # gather changed files after branch creation (if any)
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

                # If the user is on the base branch, create a new branch named from the PR title
                if current_branch == base_branch:
                    import re
                    def slugify(s):
                        s = s.lower()
                        s = re.sub(r'[^a-z0-9]+', '-', s)
                        s = s.strip('-')
                        if len(s) > 50:
                            s = s[:50].rstrip('-')
                        return s or 'pr-branch'

                    new_branch_base = f'pr/{slugify(title)}'
                    candidate = new_branch_base
                    i = 0
                    # find a non-existing branch name
                    while True:
                        exists_local = subprocess.run(f'git rev-parse --verify --quiet {candidate}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                        exists_remote = subprocess.run(f'git ls-remote --exit-code --heads origin {candidate}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
                        if not (exists_local or exists_remote):
                            break
                        i += 1
                        candidate = f'{new_branch_base}-{i}'

                    new_branch = candidate
                    print(f'Creating new branch {new_branch} from {base_branch} and pushing to origin...')
                    # ensure base is up-to-date
                    rc = subprocess.run(f'git fetch origin {base_branch}', shell=True).returncode
                    if rc != 0:
                        print(f'Warning: failed to fetch origin/{base_branch}; continuing')
                    rc = subprocess.run(f'git checkout {base_branch}', shell=True).returncode
                    if rc != 0:
                        print(f'Failed to checkout {base_branch}. Aborting PR creation.')
                    else:
                        rc = subprocess.run(f'git checkout -b {new_branch}', shell=True).returncode
                        if rc != 0:
                            print(f'Failed to create branch {new_branch}. Aborting PR creation.')
                        else:
                            rc = subprocess.run(f'git push -u origin {new_branch}', shell=True).returncode
                            if rc != 0:
                                print(f'Failed to push branch {new_branch} to origin. Aborting PR creation.')
                            else:
                                current_branch = new_branch

                cmd = f'gh pr create --base {base_branch} --head {current_branch} --title "{title.replace("\"","\\\"")}" --body-file {out_path}'

                # Ensure there is at least one commit between base and head. If not, offer to commit or create an empty commit.
                try:
                    count = run(f'git rev-list --count {base_branch}..{current_branch}')
                except Exception:
                    count = '0'

                if count.strip() == '0':
                    print('\nNo commits found between base and head.')
                    try:
                        status = run('git status --porcelain')
                    except Exception:
                        status = ''

                    if status:
                        print('Uncommitted changes detected:')
                        print(status)
                        if ask_yes_no('Commit uncommitted changes now so the PR can be created?', default='y'):
                            msg = input('Commit message: ').strip() or 'chore: commit before PR'
                            subprocess.run('git add -A', shell=True)
                            rc = subprocess.run(f'git commit -m "{msg.replace("\"","\\\"")}"', shell=True).returncode
                            if rc != 0:
                                print('Failed to commit changes. Aborting PR creation.')
                                rc = 1
                            else:
                                subprocess.run('git push', shell=True)
                        else:
                            if ask_yes_no('Create an empty commit to allow PR creation?', default='n'):
                                rc = subprocess.run('git commit --allow-empty -m "chore: create PR branch"', shell=True).returncode
                                if rc != 0:
                                    print('Failed to create empty commit. Aborting.')
                                    rc = 1
                                else:
                                    subprocess.run('git push', shell=True)
                            else:
                                print('PR creation cancelled by user (no commits).')
                                rc = 1

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
