import { describe, it, expect } from 'vitest';
import { validateAnalysisResult, isValidAnalysisResult } from '../src/validate.js';
import type { AnalysisResult } from '../src/types.js';

function makeResult(overrides: Partial<AnalysisResult> = {}): AnalysisResult {
  return {
    verdict: 'APPROVE',
    postType: 'vacancy',
    language: 'Serbian',
    riskLevel: 'low',
    reason: 'Valid test reason.',
    missingInfo: 'none',
    problemsFound: 'none',
    action: 'Objaviti bez izmena.',
    safeVersion: 'not needed',
    questionToAuthor: 'not needed',
    serbianVersion: 'not needed',
    adminNote: 'Test note.',
    ...overrides,
  };
}

describe('validateAnalysisResult', () => {
  it('accepts a valid APPROVE result', () => {
    const errors = validateAnalysisResult(makeResult());
    expect(errors).toHaveLength(0);
  });

  it('accepts a valid REJECT result', () => {
    const errors = validateAnalysisResult(
      makeResult({ verdict: 'REJECT', postType: 'spam', riskLevel: 'high' }),
    );
    expect(errors).toHaveLength(0);
  });

  it('accepts a valid ESCALATE result', () => {
    const errors = validateAnalysisResult(
      makeResult({ verdict: 'ESCALATE', postType: 'conflict', riskLevel: 'high' }),
    );
    expect(errors).toHaveLength(0);
  });

  it('rejects invalid verdict', () => {
    const errors = validateAnalysisResult(
      makeResult({ verdict: 'INVALID' as any }),
    );
    expect(errors.some((e) => e.field === 'verdict')).toBe(true);
  });

  it('rejects invalid postType', () => {
    const errors = validateAnalysisResult(
      makeResult({ postType: 'blog_post' as any }),
    );
    expect(errors.some((e) => e.field === 'postType')).toBe(true);
  });

  it('rejects invalid language', () => {
    const errors = validateAnalysisResult(
      makeResult({ language: 'German' as any }),
    );
    expect(errors.some((e) => e.field === 'language')).toBe(true);
  });

  it('rejects invalid riskLevel', () => {
    const errors = validateAnalysisResult(
      makeResult({ riskLevel: 'critical' as any }),
    );
    expect(errors.some((e) => e.field === 'riskLevel')).toBe(true);
  });

  it('rejects empty reason', () => {
    const errors = validateAnalysisResult(makeResult({ reason: '' }));
    expect(errors.some((e) => e.field === 'reason')).toBe(true);
  });

  it('rejects empty action', () => {
    const errors = validateAnalysisResult(makeResult({ action: '' }));
    expect(errors.some((e) => e.field === 'action')).toBe(true);
  });

  it('requires safeVersion when verdict is APPROVE_WITH_EDITS', () => {
    const errors = validateAnalysisResult(
      makeResult({ verdict: 'APPROVE_WITH_EDITS', safeVersion: 'not needed' }),
    );
    expect(errors.some((e) => e.field === 'safeVersion')).toBe(true);
  });

  it('accepts safeVersion when verdict is APPROVE_WITH_EDITS and text is provided', () => {
    const errors = validateAnalysisResult(
      makeResult({
        verdict: 'APPROVE_WITH_EDITS',
        safeVersion: 'Bezbedna verzija teksta.',
      }),
    );
    expect(errors.filter((e) => e.field === 'safeVersion')).toHaveLength(0);
  });

  it('requires questionToAuthor when verdict is NEEDS_CLARIFICATION', () => {
    const errors = validateAnalysisResult(
      makeResult({
        verdict: 'NEEDS_CLARIFICATION',
        questionToAuthor: 'not needed',
      }),
    );
    expect(errors.some((e) => e.field === 'questionToAuthor')).toBe(true);
  });

  it('requires serbianVersion for non-Serbian non-REJECT posts', () => {
    const errors = validateAnalysisResult(
      makeResult({ language: 'Russian', serbianVersion: 'not needed' }),
    );
    expect(errors.some((e) => e.field === 'serbianVersion')).toBe(true);
  });

  it('does not require serbianVersion for REJECTED non-Serbian posts', () => {
    const errors = validateAnalysisResult(
      makeResult({
        language: 'Russian',
        verdict: 'REJECT',
        serbianVersion: 'not needed',
      }),
    );
    expect(errors.filter((e) => e.field === 'serbianVersion')).toHaveLength(0);
  });

  it('accepts all 5 valid verdicts', () => {
    const verdicts = ['APPROVE', 'APPROVE_WITH_EDITS', 'NEEDS_CLARIFICATION', 'REJECT', 'ESCALATE'] as const;
    for (const v of verdicts) {
      const result = makeResult({
        verdict: v,
        safeVersion: v === 'APPROVE_WITH_EDITS' ? 'Bezbedna verzija.' : 'not needed',
        questionToAuthor: v === 'NEEDS_CLARIFICATION' ? 'Pitanje autoru?' : 'not needed',
      });
      expect(isValidAnalysisResult(result)).toBe(true);
    }
  });

  it('accepts all 10 valid post types', () => {
    const types = [
      'vacancy', 'worker_review', 'job_request', 'question', 'warning',
      'recommendation', 'admin_post', 'spam', 'conflict', 'unclear',
    ] as const;
    for (const t of types) {
      expect(isValidAnalysisResult(makeResult({ postType: t }))).toBe(true);
    }
  });
});
