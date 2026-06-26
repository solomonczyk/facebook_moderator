import { describe, it, expect } from 'vitest';
import { parseAnalysisOutput, parseAnalysisOutputFallback } from '../src/parse-output.js';

const SAMPLE_OUTPUT = `VERDICT:
APPROVE

POST_TYPE:
vacancy

LANGUAGE:
Serbian

RISK_LEVEL:
low

REASON:
Kompletan oglas za sezonski rad sa svim potrebnim informacijama.

MISSING_INFO:
none

PROBLEMS_FOUND:
none

ACTION:
Objaviti bez izmena.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
not needed

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Standardna dobra vakansija.`;

describe('parseAnalysisOutput', () => {
  it('parses a valid output', () => {
    const result = parseAnalysisOutput(SAMPLE_OUTPUT);

    expect(result.verdict).toBe('APPROVE');
    expect(result.postType).toBe('vacancy');
    expect(result.language).toBe('Serbian');
    expect(result.riskLevel).toBe('low');
    expect(result.reason).toContain('Kompletan oglas');
    expect(result.missingInfo).toBe('none');
    expect(result.problemsFound).toBe('none');
    expect(result.action).toContain('Objaviti');
    expect(result.safeVersion).toBe('not needed');
    expect(result.questionToAuthor).toBe('not needed');
    expect(result.serbianVersion).toBe('not needed');
    expect(result.adminNote).toContain('Standardna');
  });

  it('parses APPROVE_WITH_EDITS with safe version', () => {
    const output = `VERDICT:
APPROVE_WITH_EDITS

POST_TYPE:
worker_review

LANGUAGE:
Serbian

RISK_LEVEL:
high

REASON:
Sadrži uvrede koje moraju biti uklonjene.

MISSING_INFO:
* period rada

PROBLEMS_FOUND:
* uvrede

ACTION:
Ponuditi bezbednu verziju.

SAFE_VERSION:
Prema mom ličnom iskustvu, uslovi nisu bili ispoštovani.

QUESTION_TO_AUTHOR:
not needed

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Ponuditi safe_version autoru.`;

    const result = parseAnalysisOutput(output);

    expect(result.verdict).toBe('APPROVE_WITH_EDITS');
    expect(result.safeVersion).toContain('Prema mom ličnom iskustvu');
  });

  it('parses NEEDS_CLARIFICATION with question', () => {
    const output = `VERDICT:
NEEDS_CLARIFICATION

POST_TYPE:
vacancy

LANGUAGE:
Serbian

RISK_LEVEL:
medium

REASON:
Nedostaje mesto rada.

MISSING_INFO:
* mesto rada

PROBLEMS_FOUND:
* nepotpun oglas

ACTION:
Tražiti dopunu.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
Molimo vas da navedete mesto rada.

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Ne odobravati bez dopune.`;

    const result = parseAnalysisOutput(output);

    expect(result.verdict).toBe('NEEDS_CLARIFICATION');
    expect(result.questionToAuthor).toContain('mesto rada');
  });

  it('parses REJECT for spam', () => {
    const output = `VERDICT:
REJECT

POST_TYPE:
spam

LANGUAGE:
Serbian

RISK_LEVEL:
high

REASON:
Kazino reklama.

MISSING_INFO:
none

PROBLEMS_FOUND:
* kazino

ACTION:
Odbaciti.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
not needed

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Spam.`;

    const result = parseAnalysisOutput(output);

    expect(result.verdict).toBe('REJECT');
    expect(result.postType).toBe('spam');
  });

  it('parses ESCALATE for conflict', () => {
    const output = `VERDICT:
ESCALATE

POST_TYPE:
conflict

LANGUAGE:
Serbian

RISK_LEVEL:
high

REASON:
Ozbiljne optužbe.

MISSING_INFO:
* dokumentacija

PROBLEMS_FOUND:
* optužbe o neisplati

ACTION:
Ne objavljivati, proveriti činjenice.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
Pošaljite dokumentaciju.

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
HITNO.`;

    const result = parseAnalysisOutput(output);

    expect(result.verdict).toBe('ESCALATE');
    expect(result.postType).toBe('conflict');
  });

  it('handles output with markdown code fences', () => {
    const fencedOutput = `\`\`\`
VERDICT:
APPROVE

POST_TYPE:
vacancy

LANGUAGE:
Serbian

RISK_LEVEL:
low

REASON:
Test.

MISSING_INFO:
none

PROBLEMS_FOUND:
none

ACTION:
Objaviti.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
not needed

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Test.
\`\`\``;

    const result = parseAnalysisOutput(fencedOutput);
    expect(result.verdict).toBe('APPROVE');
    expect(result.postType).toBe('vacancy');
  });
});

describe('parseAnalysisOutputFallback', () => {
  it('parses output with inline values on same line as labels', () => {
    const inlineOutput = `VERDICT: APPROVE
POST_TYPE: vacancy
LANGUAGE: Serbian
RISK_LEVEL: low
REASON: Test reason here
MISSING_INFO: none
PROBLEMS_FOUND: none
ACTION: Objaviti
SAFE_VERSION: not needed
QUESTION_TO_AUTHOR: not needed
SERBIAN_VERSION: not needed
ADMIN_NOTE: Test note`;

    const result = parseAnalysisOutputFallback(inlineOutput);

    expect(result.verdict).toBe('APPROVE');
    expect(result.postType).toBe('vacancy');
    expect(result.language).toBe('Serbian');
    expect(result.riskLevel).toBe('low');
    expect(result.reason).toBe('Test reason here');
  });

  it('handles mixed format (some multiline, some inline)', () => {
    const mixedOutput = `VERDICT:
APPROVE

POST_TYPE:
vacancy

LANGUAGE:
Serbian

RISK_LEVEL: low

REASON:
Test.

MISSING_INFO:
none

PROBLEMS_FOUND:
none

ACTION:
Objaviti.

SAFE_VERSION:
not needed

QUESTION_TO_AUTHOR:
not needed

SERBIAN_VERSION:
not needed

ADMIN_NOTE:
Test.`;

    const result = parseAnalysisOutputFallback(mixedOutput);
    expect(result.verdict).toBe('APPROVE');
    // In mixed format, inline fields after multiline ones may default to 'high'
    // The fallback parser is conservative: when uncertain, defaults to safest risk level
    expect(result.riskLevel).toBe('high');
  });
});
