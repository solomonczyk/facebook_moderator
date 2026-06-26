import { describe, it, expect } from 'vitest';
import { hasApiKey } from '../src/config.js';
import { TEST_CASES } from './fixtures/test-cases.js';

/**
 * Live tests — gated on ANTHROPIC_API_KEY.
 *
 * These tests call the actual Anthropic API with the system prompt
 * and validate the responses. They are skipped when no API key is present.
 *
 * Because LLMs are non-deterministic, verdict/type mismatches are reported
 * as warnings rather than hard failures. The primary validation is:
 * 1. Output is parseable (the parser doesn't throw)
 * 2. Output passes schema validation (verdict, postType, language, riskLevel are valid)
 * 3. All 12 required fields are present
 */

const runLive = hasApiKey();

describe.skip.each(runLive ? [] : ['no API key'])('Live LLM Tests', () => {
  it('should be skipped when no API key', () => {
    expect(runLive).toBe(false);
  });
});

if (runLive) {
  // Dynamic import to avoid loading the module when API key is not present
  const { analyzePost } = await import('../src/analyze.js');

  describe('Live LLM Tests', () => {
    // Run each test case through the actual LLM
    for (const testCase of TEST_CASES) {
      it(`[${testCase.id}] ${testCase.description}`, async () => {
        const response = await analyzePost({
          text: testCase.input,
          postId: testCase.id,
        });

        if (!response.success) {
          // If the API call fails, fail the test with the error
          throw new Error(`API call failed for ${testCase.id}: ${response.error}`);
        }

        const result = response.result;

        // 1. Verdict should match expected
        expect(
          result.verdict,
          `[${testCase.id}] Verdict mismatch: expected ${testCase.expectedVerdict}, got ${result.verdict}. Reason: ${result.reason}`,
        ).toBe(testCase.expectedVerdict);

        // 2. Post type should match expected
        expect(
          result.postType,
          `[${testCase.id}] Post type mismatch: expected ${testCase.expectedPostType}, got ${result.postType}`,
        ).toBe(testCase.expectedPostType);

        // 3. Language should match expected
        expect(
          result.language,
          `[${testCase.id}] Language mismatch: expected ${testCase.expectedLanguage}, got ${result.language}`,
        ).toBe(testCase.expectedLanguage);

        // 4. Risk level should match expected
        expect(
          result.riskLevel,
          `[${testCase.id}] Risk level mismatch: expected ${testCase.expectedRiskLevel}, got ${result.riskLevel}`,
        ).toBe(testCase.expectedRiskLevel);

        // 5. Problems found should contain expected keywords
        for (const keyword of testCase.expectedProblems) {
          const problemsLower = result.problemsFound.toLowerCase();
          const keywordLower = keyword.toLowerCase();
          expect(
            problemsLower,
            `[${testCase.id}] Expected problem keyword "${keyword}" not found in: ${result.problemsFound}`,
          ).toContain(keywordLower);
        }

        // 6. All required fields should be non-empty
        expect(result.reason.length).toBeGreaterThan(0);
        expect(result.action.length).toBeGreaterThan(0);
        expect(result.missingInfo.length).toBeGreaterThan(0);
        expect(result.problemsFound.length).toBeGreaterThan(0);
        expect(result.adminNote.length).toBeGreaterThan(0);

        console.log(`✅ [${testCase.id}] ${testCase.description}`);
        console.log(`   Verdict: ${result.verdict} | Type: ${result.postType} | Risk: ${result.riskLevel}`);
      }, 30000); // 30s timeout per test case
    }
  });
}
