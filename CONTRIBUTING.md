# Contributing

## Workflow

1. Branch off `main` using the issue number: `git checkout -b 5-retrieval-agent`
2. Make your changes
3. Run evals locally before pushing: `pytest evals/ -v`
4. Open a PR — the eval gate runs automatically on every PR
5. PRs are blocked from merging if faithfulness < 0.75 or relevance < 0.70
6. Squash and merge once the gate passes

## Branch naming

`{issue-number}-{short-description}` — e.g. `7-langgraph-orchestrator`

## Commit messages

Use imperative present tense: `Add retrieval agent`, `Fix chunking overlap`, `Update faithfulness threshold`
