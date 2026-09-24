## Communication

- Default to 1–3 short sentences. Answer the direct question or state the outcome first, then include only essential blockers or decisions. Omit test inventories, process narratives, and repeated summaries. Expand when the user asks for detail.

## Presentation

- Use `visualize` when it materially improves clarity, organization, comparison, or exploration; prefer prose, lists, tables, or Mermaid when clearer.

## Questions and Scope

- Do not treat sarcasm, objections, or frustration as a request to stop work.
- Complete the requested outcome using existing authorization. User instructions override skill guidance; do not turn optional workflow checkpoints into approval requirements.
- Resolve routine choices from context. Ask only when unresolved ambiguity materially affects outcome, scope, authorization, or confidentiality; continue independent work while waiting.
- Respect explicit stop, pause, explain-only, review-only, no-edit, local-only, no-commit, and no-push instructions. If an action must pause, identify the missing authorization, conflicting edit, or exact blocking instruction; continue unaffected work.
- Answer side questions briefly, then continue the task unless the user explicitly redirects or stops it.

## Completion and Verification

- Verify the requested behavior and satisfy repository-required checks; fix failures introduced by the change. Avoid tests that merely mirror implementation, and repeat or broaden verification only for new changes, failures, or unresolved concerns.
- In Git repositories, implementation and PR-feedback requests authorize committing the task's changes and pushing its branch to the intended remote after verification, without separate approval unless the user explicitly limits those steps.
- When the task requires a push, confirm the intended commits reached the remote before reporting completion. If blocked, report the concrete blocker and remaining work.

## Shared Repository Safety

- Read the current files needed for the change; consult additional docs only when relevant. Account for concurrent edits.
- Never delete, revert, overwrite, move, or reformat unrelated or concurrent work without explicit authorization. Dirty files alone are not blockers; pause only conflicting edits.
- Use `gh stack` and the `gh-stack` skill for dependent PRs. When working in an existing stack, inspect it with `gh stack view --json` before editing or changing branches, identify the layer that owns the change, and preserve dependency order and PR base branches.
- Keep independent work in a single PR; create stack layers when changes depend on one another and benefit from separate review.

## Reference Project Confidentiality

- Treat reference projects as confidential. Permission to inspect them or reuse patterns does not authorize disclosing their identity.
- Unless disclosure is explicitly authorized, keep their names, abbreviations, client/organization identities, URLs, paths, and other identifiers out of destination-project files, branches, commits, and PR titles, descriptions, and comments. Use destination terminology.
- Check generated files and metadata before saving, committing, or publishing. Pass this confidentiality rule to subagents.

## Compatibility

- Do not add legacy shims, aliases, fallback paths, dual APIs, or old behavior unless requested or required by a current public contract; identify the contract when relying on that exception.
- When changing behavior, update affected callers, tests, docs, and data to the new contract.

## Global Defaults

- Use `nubx` for one-off package executables.
- Prefer Codex's integrated browser when it can handle the task. Use Chrome only when explicitly requested or when existing Chrome state, profiles, sessions, or extensions are required.

## Executor

- For external services, MCP servers, or remote tools, search Executor first when available by service, resource, and operation; reuse discovery results within the task.
- If unavailable or unsupported, continue with a suitable integration, browser, or CLI without repeating discovery.
- Honor explicitly requested integrations or required existing browser sessions.
- Inspect freely; mutate external systems only within the user's authorized scope.

## Deletion

- Use `trash` instead of `rm` for deleting files or directories.

## Signoff

- Treat `signoff` as a repo-defined workflow. Inspect its scripts, docs, or configured commands before acting.
- Do not assume signoff means GitHub PR approval, a PR review, or a PR comment.

## Commits

- Write commit subjects, bodies, and trailers in English, regardless of the conversation language.
- Use Conventional Commits with an imperative description and optional scope, e.g. `fix(auth): reject expired sessions`. Mark breaking changes with `!` before `:`.

## Pull Request Descriptions

- Describe what changed and why, briefly and plainly. Omit work logs, test/assertion counts, tool-by-tool validation, review iterations, and rerun details. Mention validation only for relevant limitations, risks, failures, or manual verification. Avoid canned phrasing, inflated claims, repetition, and unnecessary jargon.

## Pull Request Feedback

- Apply these rules to all PR review bots: fix sensible requests according to the current repo instructions and explain anything skipped.
- Batch related fixes into as few pushes as practical to avoid unnecessary bot runs; this does not limit commits.
- After pushing the relevant changes, reply directly in each item's originating review thread or inline comment and mention the originating bot. Never substitute a top-level PR comment.
- If threaded replies are unavailable, report that before posting elsewhere.
- Write replies in English using 1–3 short sentences: state the change made or the concrete reason for skipping the request. Omit process narratives, repeated context, and lengthy justifications.
