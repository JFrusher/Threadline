# ADR-001: One YAML file per item

**Status:** accepted · 2026-11-16

## Context
Regulatory items (needs, requirements, hazards, risk controls, SOUP…) change at different times, by different people.
One big YAML file per document type makes every PR touch the same file and conflict.

## Decision
Every item is one YAML file. The filename stem is the item ID (`dhf/srs/SRS-014.yaml` → `id: SRS-014`).
Links are stored on the child item only and point upward (child → parent).

## Consequences
- `git log dhf/srs/SRS-014.yaml` is the item's full change history.
- Two PRs creating the same ID cause a git add/add conflict. Git catches ID collisions; Threadline does not allocate IDs.
- The graph is rebuilt from files on every check. No index file to keep in sync.
