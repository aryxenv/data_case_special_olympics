---
name: git-workflow
description: Enforces the project's Git branching model, conventional commits, PR workflow, and commit granularity rules. Use this when creating branches, writing commit messages, opening PRs, or performing any Git operations.
---

# Git Workflow — Special Olympics Data Dashboard

## Tooling — Always use `gh` CLI

**All Git operations MUST use the `gh` CLI** (GitHub CLI). This includes creating branches, pushing, creating PRs, viewing PR status, and merging.

- Do **not** fall back to raw `git` commands when `gh` provides the same functionality.
- Do **not** use the GitHub MCP API for operations `gh` can handle.
- `gh` is installed at `C:\Program Files\GitHub CLI\gh.exe` — add it to PATH if needed.

### Common `gh` commands

```bash
# Create and switch to a new branch
git checkout -b feat/my-feature

# Stage, commit, push, and create PR in one flow
git add src/extract.py
git commit -m "feat(etl): add extraction class"
gh pr create --title "feat(etl): add extraction class" --body "Description" --base main

# Check PR status
gh pr status
gh pr view 1

# List open PRs
gh pr list
```

## Branching Model

`main` is the single production + development branch.

- **Never commit directly to `main`.** All changes (features, fixes, docs, etc.) must go through a dedicated branch + pull request.
- Create a branch from `main` for each unit of work, then open a PR back to `main`.
- PRs require approval before merging — reviewers may request changes.
- Do **not** merge your own PR without approval.

## Branch Naming

Use the conventional commit type as a prefix:

```
feat/short-description     → new feature
fix/short-description      → bug fix
docs/short-description     → documentation only
refactor/short-description → code restructure (no behaviour change)
chore/short-description    → tooling, deps, CI, config
test/short-description     → adding or updating tests
```

### Steps to create a branch

```bash
git checkout main
git pull origin main
git checkout -b feat/my-new-feature
```

## Commit Granularity

Split work into **logical, atomic commits** — never lump all changes into a single commit per branch/PR.

- Each commit should represent one self-contained change (e.g., one function, one fix, one file group).
- If a feature touches extract + transform + tests, that is at least 3 separate commits.
- Keep commits reviewable: a reviewer should understand each commit on its own.

### How to stage logical groups

```bash
# Stage only related files for one logical commit
git add src/extract.py
git commit -m "feat(etl): add Excel extraction class"

# Then stage the next logical group
git add src/transform.py
git commit -m "feat(etl): add score normalization in transform"

# Then tests
git add tests/test_extract.py
git commit -m "test(etl): add unit tests for extraction"
```

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary>

[optional body]
```

### Types

| Type       | When to use                                    |
| ---------- | ---------------------------------------------- |
| `feat`     | New feature or capability                      |
| `fix`      | Bug fix                                        |
| `docs`     | Documentation only                             |
| `refactor` | Code restructure with no behaviour change      |
| `chore`    | Tooling, deps, CI, config                      |
| `test`     | Adding or updating tests                       |
| `style`    | Formatting, whitespace (no logic change)       |
| `perf`     | Performance improvement                        |
| `ci`       | CI/CD pipeline changes                         |
| `build`    | Build system or external dependency changes    |

### Examples

```
feat(etl): add score normalization for time-based results
fix(transform): handle DQ entries in rank parsing
docs: update data requirements with medal logic
chore: add openpyxl to requirements.txt
refactor(extract): simplify multi-sheet reading logic
test(transform): add edge cases for ordinal rank parsing
```

## Pull Requests

### PR titles

PR titles follow the same conventional commit format:

```
feat(etl): implement athlete dimension extraction
fix(transform): correct fuzzy club matching threshold
docs: add star schema diagram to README
```

### PR workflow

1. Push your branch and create a PR with `gh`:
   ```bash
   gh pr create --title "feat(etl): my feature" --body "Description" --base main
   ```
2. Use a conventional commit-style title for the PR.
3. Check PR status:
   ```bash
   gh pr status
   ```
4. Wait for review and approval — do **not** merge without it.
5. Address any requested changes with additional commits on the same branch.
6. Once approved, the reviewer (or you, after approval) merges the PR.

### What NOT to do

- ❌ Push directly to `main`
- ❌ Merge your own PR without approval
- ❌ Squash an entire feature into one giant commit
- ❌ Use vague commit messages like `"update files"` or `"WIP"`
- ❌ Use raw `git push` + GitHub web UI when `gh pr create` can do it
