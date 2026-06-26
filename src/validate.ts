import {
  type AnalysisResult,
  type ValidationError,
  VALID_VERDICTS,
  VALID_POST_TYPES,
  VALID_LANGUAGES,
  VALID_RISK_LEVELS,
  NOT_NEEDED,
} from './types.js';

/**
 * Validates an AnalysisResult against all business rules.
 * Returns a list of validation errors. Empty list = valid.
 */
export function validateAnalysisResult(result: AnalysisResult): ValidationError[] {
  const errors: ValidationError[] = [];

  // 1. Check verdict
  if (!VALID_VERDICTS.includes(result.verdict)) {
    errors.push({
      field: 'verdict',
      message: `Invalid verdict "${result.verdict}". Must be one of: ${VALID_VERDICTS.join(', ')}`,
    });
  }

  // 2. Check postType
  if (!VALID_POST_TYPES.includes(result.postType)) {
    errors.push({
      field: 'postType',
      message: `Invalid post type "${result.postType}". Must be one of: ${VALID_POST_TYPES.join(', ')}`,
    });
  }

  // 3. Check language
  if (!VALID_LANGUAGES.includes(result.language)) {
    errors.push({
      field: 'language',
      message: `Invalid language "${result.language}". Must be one of: ${VALID_LANGUAGES.join(', ')}`,
    });
  }

  // 4. Check riskLevel
  if (!VALID_RISK_LEVELS.includes(result.riskLevel)) {
    errors.push({
      field: 'riskLevel',
      message: `Invalid risk level "${result.riskLevel}". Must be one of: ${VALID_RISK_LEVELS.join(', ')}`,
    });
  }

  // 5. Reason is required
  if (!result.reason || result.reason.trim().length === 0) {
    errors.push({
      field: 'reason',
      message: 'Reason is required and cannot be empty.',
    });
  }

  // 6. Action is required
  if (!result.action || result.action.trim().length === 0) {
    errors.push({
      field: 'action',
      message: 'Action is required and cannot be empty.',
    });
  }

  // 7. Safe version should be "not needed" unless verdict is APPROVE_WITH_EDITS
  if (result.verdict === 'APPROVE_WITH_EDITS' && result.safeVersion === NOT_NEEDED) {
    errors.push({
      field: 'safeVersion',
      message:
        'safeVersion should contain the rewritten text when verdict is APPROVE_WITH_EDITS.',
    });
  }

  // 8. Question to author should be "not needed" unless verdict is NEEDS_CLARIFICATION
  if (result.verdict === 'NEEDS_CLARIFICATION' && result.questionToAuthor === NOT_NEEDED) {
    errors.push({
      field: 'questionToAuthor',
      message:
        'questionToAuthor should contain a question when verdict is NEEDS_CLARIFICATION.',
    });
  }

  // 9. Serbian version should be provided when language is not Serbian
  if (result.language !== 'Serbian' && result.language !== 'Other') {
    if (
      result.serbianVersion === NOT_NEEDED &&
      result.verdict !== 'REJECT'
    ) {
      errors.push({
        field: 'serbianVersion',
        message:
          'serbianVersion should contain a Serbian translation for non-Serbian posts that are not rejected.',
      });
    }
  }

  return errors;
}

/**
 * Returns true if the AnalysisResult passes all validations.
 */
export function isValidAnalysisResult(result: AnalysisResult): boolean {
  return validateAnalysisResult(result).length === 0;
}

/**
 * Validates that the output can be parsed and meets all business rules.
 * Returns errors or empty array.
 */
export function validateRawOutput(raw: string, parseFn: (raw: string) => AnalysisResult): ValidationError[] {
  try {
    const result = parseFn(raw);
    return validateAnalysisResult(result);
  } catch (err) {
    return [
      {
        field: '(root)',
        message: `Failed to parse output: ${err instanceof Error ? err.message : String(err)}`,
      },
    ];
  }
}
