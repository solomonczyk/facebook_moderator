# Facebook Group Admin Copilot

## Sezonski rad Srbija | Poslovi i iskustva radnika

AI-powered moderation assistant for the Facebook group [Sezonski rad Srbija](https://www.facebook.com/groups/992369183697618).

### What It Does

The Admin Copilot helps the group administrator:

- **Analyze** posts before approval (vacancies, reviews, questions, warnings)
- **Classify** posts into 10 types (vacancy, worker_review, job_request, question, warning, recommendation, admin_post, spam, conflict, unclear)
- **Detect** spam, fraud, insults, and personal data
- **Rewrite** risky text into safe, factual language
- **Translate** between Serbian, Russian, Ukrainian, Hungarian, and Romanian
- **Prepare** admin responses, questions to authors, and internal notes

### Key Principle: Operator-in-the-Loop

The copilot **advises** — the human **decides**. The copilot never:

- Logs into Facebook
- Publishes, deletes, or edits posts automatically
- Bans or approves members automatically
- Scrapes the group
- Creates fake reviews or fake vacancies

All Facebook actions are performed **manually by the administrator**.

---

## Quick Start

### Prerequisites

- Node.js 20+
- npm
- Anthropic API key (for live analysis)

### Setup

```bash
npm install
export ANTHROPIC_API_KEY="sk-ant-..."   # or add to .env
```

### Usage

**Interactive mode:**
```bash
npm start
```
Paste the post text, type `---END---` on a new line to submit, or press Ctrl+D.

**Pipe mode:**
```bash
npm start -- --stdin < post.txt
```

**File mode:**
```bash
npm start -- --file post.txt
npm start -- post.txt                  # shorthand
```

**JSON output:**
```bash
npm start -- --json < post.txt
```

---

## Commands

| Command | Description |
|---------|-------------|
| `npm start` | Run the interactive CLI |
| `npm run build` | Compile TypeScript |
| `npm run lint` | Run ESLint |
| `npm run typecheck` | Type-check without emitting |
| `npm test` | Run unit tests (no API key needed) |
| `npm run test:live` | Run live LLM tests (needs API key) |
| `npm run proof` | Validate proof.json |
| `npm run validate-schema` | Validate all expected outputs against schema |

---

## Project Structure

```
├── README.md                    # This file
├── SYSTEM_PROMPT.md             # THE core product — LLM system prompt
├── MODERATION_POLICY.md         # Detailed moderation rules for admins
├── TEST_CASES.md                # Test case catalog
├── proof.json                   # Delivery proof manifest
├── package.json
├── tsconfig.json
│
├── src/                         # Source code
│   ├── index.ts                 # Entry point / CLI
│   ├── cli.ts                   # Interactive readline CLI
│   ├── analyze.ts               # LLM API integration
│   ├── prompt.ts                # System prompt loader
│   ├── types.ts                 # TypeScript types
│   ├── validate.ts              # Output validation
│   ├── parse-output.ts          # LLM output parser
│   └── config.ts                # Environment config
│
├── tests/                       # Test suite
│   ├── validate.test.ts         # Schema validation tests
│   ├── prompt.test.ts           # Prompt structure tests
│   ├── parse-output.test.ts     # Parser tests
│   ├── live.test.ts             # Live LLM tests (gated)
│   └── fixtures/
│       └── test-cases.ts        # 15 test case definitions
│
├── sample_inputs/               # 15 raw post texts
├── sample_outputs/              # 15 expected outputs (JSON)
└── scripts/                     # Utility scripts
    ├── validate-proof.ts
    └── validate-schema.ts
```

---

## Output Format

The copilot returns analysis in this format:

```
VERDICT:        <APPROVE|APPROVE_WITH_EDITS|NEEDS_CLARIFICATION|REJECT|ESCALATE>
POST_TYPE:      <10 types>
LANGUAGE:       <Serbian|Russian|Ukrainian|Hungarian|Romanian|Other>
RISK_LEVEL:     <low|medium|high>
REASON:         <explanation>
MISSING_INFO:   <list or "none">
PROBLEMS_FOUND: <list or "none">
ACTION:         <admin instruction>
SAFE_VERSION:   <safe rewrite or "not needed">
QUESTION_TO_AUTHOR: <question or "not needed">
SERBIAN_VERSION:    <translation or "not needed">
ADMIN_NOTE:     <internal note>
```

---

## Test Cases

15 test cases cover all verdicts, post types, and languages:

| ID | Description | Verdict |
|----|-------------|---------|
| 001 | Full vacancy — all 12 fields | APPROVE |
| 002 | Incomplete vacancy — no pay | NEEDS_CLARIFICATION |
| 003 | Incomplete vacancy — no city | NEEDS_CLARIFICATION |
| 004 | Suspicious vacancy "brza zarada" | REJECT |
| 005 | Worker negative review — factual | APPROVE |
| 006 | Review with insults | APPROVE_WITH_EDITS |
| 007 | Review with personal data | APPROVE_WITH_EDITS |
| 008 | Off-topic post (iPhone sale) | REJECT |
| 009 | Job request in Russian | APPROVE |
| 010 | Complete employer vacancy | APPROVE |
| 011 | Russian → Serbian translation | APPROVE |
| 012 | Hungarian → Serbian translation | APPROVE |
| 013 | Romanian → Serbian translation | APPROVE |
| 014 | Worker-employer conflict | ESCALATE |
| 015 | Spam — casino ad | REJECT |

See [TEST_CASES.md](TEST_CASES.md) for full details.

---

## Verdict System

| Verdict | Meaning |
|---------|---------|
| **APPROVE** | Publish without changes |
| **APPROVE_WITH_EDITS** | Publish after safe rewrite |
| **NEEDS_CLARIFICATION** | Ask author for missing info |
| **REJECT** | Do not publish |
| **ESCALATE** | Manual admin review required |

---

## Supported Languages

- **Serbian** (primary, Latin and Cyrillic)
- **Russian**
- **Ukrainian**
- **Hungarian**
- **Romanian**

---

## Status

**ACCEPTED FOR OPERATOR-IN-THE-LOOP MVP**

- `production_accepted`: `false` (requires operator validation on real cases)
- All 15 test cases defined and expected outputs documented
- Unit tests pass without API key
- Live tests gated on `ANTHROPIC_API_KEY`

---

## License

Private — for internal use by the "Sezonski rad Srbija" group administration.
