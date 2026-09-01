# Source coverage

Coverage quality means finding the strongest independent evidence for every requested category. Raw file count is not quality.

## Breadth matrix

Probe categories relevant to the request:

| Category | Typical evidence | Strong completion signal |
|---|---|---|
| User inputs | files, screenshots, links, pasted notes | explicit fact plus supporting artifact |
| Source control | Git refs, GitLab/GitHub/CNB changes, merge requests | accepted default-branch or release state |
| Project records | status, roadmap, gap, readiness, UAT, handoff | dated record tied to current revision |
| Work tracking | Fusion/kb tasks, issues, milestones | done state plus result evidence |
| Meetings/collaboration | minutes, decisions, approved action items | explicit decision, owner, and date |
| Release/runtime | release tags, deployment/readback, acceptance logs | current environment evidence |
| Business metrics | approved dashboards, CSV/XLSX, warehouse results | defined metric, period, and source |

Do not probe unrelated personal mail or private chat just because tools exist. The request must name or clearly imply the category.

## Coverage-first workflow

1. Convert the request into expected categories and named sources.
2. Run one bounded local inventory using `scripts/source_inventory.py` against likely roots.
3. Probe relevant external systems once, preferably in parallel.
4. Deduplicate mirrors, branches, repeated reports, and generated copies.
5. Deep-read candidates in strength order.
6. Stop when each expected category has a terminal state: accessed, missing, inaccessible, irrelevant, or superseded.

Avoid repeated broad `find`/`mdfind`/`rg` scans. One broad pass plus targeted follow-ups is enough. Never inspect another eval output or generated report as evidence.

## Source order

### 1. User-provided evidence

Treat explicit user facts as claims unless source or context confirms completion.

### 2. Authoritative project state

- freshly fetched authoritative remote refs;
- accepted default branch and release tags;
- GitLab/GitHub/CNB merge requests, issues, releases, and pipelines when authenticated.

Prefer remote accepted state over stale local checkout. If API authentication fails but Git fetch works, continue with refs and record narrower coverage.

### 3. Project records

Use current README, status, roadmap, gap, readiness, UAT, acceptance, release, and handoff reports. Check report date and target revision before relying on it.

### 4. Work tracking

Task titles prove intent, not completion. Completion requires state plus result evidence.

### 5. Meetings and collaboration

Distinguish decisions from proposals. Preserve owner and date only when explicit.

### 6. Release and business evidence

Deployment, readback, acceptance, usage, revenue, quality, or operational metrics outrank implementation activity when the reporting question is business readiness.

## Identity reconciliation

Build aliases from author/committer names, verified emails, platform usernames, co-author trailers, and user-provided mappings. Keep ambiguous shared accounts separate.

## Freshness and completeness

- Default window: seven calendar dates, inclusive.
- Fetch before summarizing remote Git state.
- Deduplicate identical commits reachable from multiple branches.
- Separate default-branch outcomes from feature-branch progress.
- Mark stale evidence; do not silently treat it as current.
- Record inaccessible sources; never replace missing authoritative evidence with weaker local evidence without disclosure.

## Coverage metrics

Report both numerator and denominator:

- `identified`: independent relevant sources expected or discovered;
- `accessed`: sources actually read or queried;
- `fresh`: accessed sources current for the reporting window or current state;
- `fact_contributing`: sources that support at least one accepted statement;
- `categories_covered`: relevant categories with at least one accessed source.

Useful coverage statement: `已访问 7/9 个相关来源，覆盖 5/6 类；GitLab API 与销售周报不可用。`

Bad coverage statement: `扫描了 1,283 个文件。`
