---
type: audit
task: TASK-007B-FIX-1
date: 2026-06-26
---

# DeepSeek Brain Activation — Debug Log

## Root Cause

`anthropic` Python package was not installed in the VPS virtual environment.

The LLM client uses `import anthropic` with a try/except:
```python
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
```

Since the package was missing, `ANTHROPIC_AVAILABLE` was `False`, making `LLMClient.available` return `False` regardless of API key configuration.

## Fix

```bash
/opt/facebook_moderator/backend/.venv/bin/pip install anthropic
systemctl restart sezonski-runtime
```

## Before (broken)

```
available: false
llm_primary: false
regex_only_mode: true
fallback_active: true
```

## After (fixed)

```
available: true
llm_primary: true
regex_only_mode: false
fallback_active: false
provider: deepseek
model: DeepSeek-V4-Pro
```

## Smoke Test

```
Input: Tražimo 5 radnika za berbu malina Arilje...
Classification: employer_job_post ✅
Confidence: 1.0 ✅
LLM used: true ✅
Fallback used: false ✅
```
