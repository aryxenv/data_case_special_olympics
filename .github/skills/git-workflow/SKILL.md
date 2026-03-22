---
name: git-workflow
description: Enforces the project's Git branching model, conventional commits, PR workflow, and commit granularity rules. Use this when creating branches, writing commit messages, opening PRs, or performing any Git operations.
---

# Git Workflow — Special Olympics Data Dashboard

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

1. Push your branch to the remote:
   ```bash
   git push -u origin feat/my-new-feature
   ```
2. Open a PR targeting `main`.
3. Use a conventional commit-style title for the PR.
4. Wait for review and approval — do **not** merge without it.
5. Address any requested changes with additional commits on the same branch.
6. Once approved, the reviewer (or you, after approval) merges the PR.

### What NOT to do

- ❌ Push directly to `main`
- ❌ Merge your own PR without approval
- ❌ Squash an entire feature into one giant commit
- ❌ Use vague commit messages like `"update files"` or `"WIP"`
