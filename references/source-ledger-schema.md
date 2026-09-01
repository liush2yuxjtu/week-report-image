# Source coverage sidecar

Save `source-coverage.json` beside the final image when an output directory is provided.

```json
{
  "schema_version": 1,
  "report_period": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "timezone": "Asia/Shanghai"},
  "scope": {"projects": [], "people": [], "requested_categories": []},
  "summary": {
    "sources_identified": 0,
    "sources_accessed": 0,
    "sources_fresh": 0,
    "sources_fact_contributing": 0,
    "categories_requested": 0,
    "categories_covered": 0,
    "accepted_facts": 0,
    "conflicts": 0
  },
  "sources": [
    {
      "source_id": "stable-short-id",
      "category": "source_control|project_record|work_tracking|meeting|release_runtime|business_metric|user_input",
      "label": "human-readable label",
      "location": "redacted or local path",
      "status": "accessed|missing|inaccessible|irrelevant|superseded",
      "freshness": "fresh|current_state|stale|unknown",
      "accessed_at": "ISO-8601",
      "facts_contributed": ["fact-id"],
      "limitations": []
    }
  ],
  "facts": [
    {
      "fact_id": "fact-1",
      "statement": "conservative evidence statement",
      "state": "completed|in_progress|blocked|planned|coordination_needed",
      "source_ids": ["source-1"],
      "confidence": "high|medium|low",
      "used_in_image": true
    }
  ],
  "conflicts": [],
  "limitations": []
}
```

## Counting rules

- Count one independent system/artifact once.
- Mirrored repositories count once.
- Same commit on several branches counts once.
- Generated reports derived from the same evidence do not create new independent sources.
- A directory scan is not a source.
- A source contributes only if it supports an accepted fact.
- Redact credentials, query tokens, private host details, and unrelated personal information.
