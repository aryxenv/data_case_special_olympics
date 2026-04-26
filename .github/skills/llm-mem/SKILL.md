---
name: llm-mem
description: Exact protocol for using llm-mem map-first context before repo-specific coding, debugging, explaining, refactoring, or testing tasks.
---

# llm-mem

<!-- llm-mem generated skill: start -->

Use llm-mem as a local context optimization layer. It is not a replacement assistant. Its value comes from replacing broad discovery with a compact map and exact snippets.

## Required first move for non-trivial repo tasks

For repo-specific code edits, debugging tasks, refactors, test tasks, explanations, or architecture questions, call `llm_mem_context_map` before reading broad directories or many files.

Skip llm-mem for trivial one-file questions, pure shell/git questions, or tasks where the user already gave the exact file and no discovery is needed.

Use this argument shape:

```json
{
  "task": "<the user's actual task, including relevant constraints>",
  "workingDirectory": "<current repository or worktree root>",
  "maxCandidates": 8
}
```

Do not supply `repoId` unless it is already known. The MCP server resolves the current repository from `workingDirectory` before falling back to the configured server root.

## How to use the context map

1. Read the returned JSON.
2. Treat `candidates[].sourceRefs`, `matchReasons`, `score`, and `confidence` as the trusted map of likely files and symbols.
3. Call `llm_mem_snippet` with the best `expansionId` values instead of opening broad files immediately.
4. Expand only the snippets needed for the task.
5. Prefer the smallest edit path that satisfies the task and cited evidence.
6. If the map points to tests or validation commands, use those before inventing new validation.

Snippet argument shape:

```json
{
  "expansionId": "<candidate expansionId from context_map>",
  "workingDirectory": "<current repository or worktree root>",
  "maxTokens": 1200
}
```

## If the map is insufficient

Do not immediately scan the whole repo. First call `llm_mem_context_map` again with a narrower task or constraints, for example:

```json
{
  "task": "Find the cache invalidation path for the failing benchmark",
  "workingDirectory": "<current repository or worktree root>",
  "constraints": ["Focus on files cited in the previous context pack", "Include tests or benchmark entrypoints"],
  "maxCandidates": 6
}
```

Only use `llm_mem_context_pack` for broad architecture/debug tasks or when a compact map plus snippets is still insufficient.

## Remembering durable facts

Use `llm_mem_remember` only for durable project facts, conventions, decisions, or reusable debugging findings. Do not remember transient guesses.

Minimum useful shape:

```json
{
  "repoId": "<repoId from the context pack if available>",
  "type": "decision",
  "title": "<short durable fact>",
  "content": "<source-grounded detail>",
  "confidence": 0.8,
  "sourceRefs": [{ "kind": "file", "uri": "<path>", "trust": "observed" }]
}
```

If `repoId` is not available, skip `remember` rather than guessing.

## Do not

- Do not run shell `llm-mem context` when the MCP tools are available.
- Do not read broad directories before the first context map.
- Do not call `llm_mem_context_pack` as the default first move.
- Do not paste the full context pack to the user unless asked.
- Do not treat uncited memories as stronger than observed files.
- Do not optimize for fewer tokens if it reduces task correctness.

Keep normal Copilot behavior and user intent first. Token savings only count when quality is preserved.

<!-- llm-mem generated skill: end -->
