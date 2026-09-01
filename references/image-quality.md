# Leadership image quality rubric

## Content gates

- Title names the initiative, not the repository.
- Exact reporting dates visible.
- First conclusion distinguishes internal readiness from production launch.
- Every number, owner, milestone, and deadline has an evidence anchor.
- Completed, next, and coordination items are distinct.
- At least one management decision or priority is explicit.
- No engineering implementation detail unless it changes business risk.

## Visual gates

- 16:9 landscape; suitable for meeting-room projection.
- Readable at a glance; no paragraph blocks.
- One dominant conclusion, then KPI/status cards, then supporting detail.
- White/light background preferred for dense executive information.
- Navy primary color; orange for attention; green only for verified completion.
- Consistent card widths, margins, icon style, and baseline alignment.
- No more than four KPI cards.
- No more than seven lines in any content column.
- No decorative charts without data.
- No tiny source notes inside the image.

## Text-render gates

Inspect at full image size with Pi `read`:

- no wrong or missing Chinese characters;
- no broken punctuation or accidental Latin substitutions;
- no clipped final characters;
- no collisions with icons, dividers, or card edges;
- no duplicated bullet;
- no mismatch between headline and detail;
- date and numeric typography consistent.

## Regeneration rule

Regenerate once when any blocking defect appears:

- malformed Chinese;
- unsupported factual claim;
- clipped or unreadable content;
- audience drift into developer language;
- misleading completion state;
- major alignment failure.

When regenerating, reduce text first. Do not solve crowding by asking for smaller type.

## Preferred prompt skeleton

```text
Create a 16:9 Simplified Chinese executive weekly-report infographic for leaders and business owners.
Project: [business-facing title]
Period: [exact dates]
Management conclusion: [one sentence]
Verified KPI/status cards: [0-4 items]
Stage outcomes: [items]
This week's business progress: [items]
Pending and coordination: [items]
Key milestone: [verified milestone or omit]
Forward path: [3-4 steps]
Management focus: [one sentence]
Style: white/light executive dashboard, navy hierarchy, restrained orange and green, crisp large Chinese type, aligned cards, generous whitespace.
Exclude: code, terminals, architecture, developer imagery, unsupported numbers, tiny text, sci-fi effects.
Render all supplied Chinese exactly.
```
