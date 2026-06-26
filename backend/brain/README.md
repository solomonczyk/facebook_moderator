# Brain v1.0 — Canon Package

This is the intellectual core of the **Sezonski rad Srbija** Runtime Manager Agent.

## Structure

```
CANON/          — Identity, mission, operator charter, safety
KNOWLEDGE/      — Classification, risk, extraction, digest, languages, edge cases
PROMPTS/        — System prompt, few-shot examples, negative examples, JSON contract
TESTS/          — Canon tests, decision tests, acceptance criteria
```

## Principles

- Model-independent — works with DeepSeek, GPT, Claude, local models
- Safety-first — when in doubt, escalate to operator
- No invention — missing info is flagged, not fabricated
- Operator authority — agent recommends, operator decides
- Serbian-first — public text in Serbian, operator summary in Russian
