// =============================================================================
// Facebook Group Admin Copilot — Core Type Definitions
// Group: Sezonski rad Srbija | Poslovi i iskustva radnika
// =============================================================================

/**
 * Moderation verdict — the agent's recommendation for the admin.
 */
export type Verdict =
  | 'APPROVE'
  | 'APPROVE_WITH_EDITS'
  | 'NEEDS_CLARIFICATION'
  | 'REJECT'
  | 'ESCALATE';

/**
 * Post type classification.
 */
export type PostType =
  | 'vacancy'
  | 'worker_review'
  | 'job_request'
  | 'question'
  | 'warning'
  | 'recommendation'
  | 'admin_post'
  | 'spam'
  | 'conflict'
  | 'unclear';

/**
 * Detected or declared language of the post.
 */
export type Language = 'Serbian' | 'Russian' | 'Ukrainian' | 'Hungarian' | 'Romanian' | 'Other';

/**
 * Risk level for the post.
 */
export type RiskLevel = 'low' | 'medium' | 'high';

/**
 * The structured output the agent must return for every analysis.
 * Matches the exact format from the spec (section 14).
 */
export interface AnalysisResult {
  verdict: Verdict;
  postType: PostType;
  language: Language;
  riskLevel: RiskLevel;
  reason: string;
  missingInfo: string;
  problemsFound: string;
  action: string;
  safeVersion: string;
  questionToAuthor: string;
  serbianVersion: string;
  adminNote: string;
}

/**
 * Raw text-format output fields, keyed by label.
 * Used during parsing of the LLM's text response.
 */
export const OUTPUT_FIELD_LABELS = [
  'VERDICT',
  'POST_TYPE',
  'LANGUAGE',
  'RISK_LEVEL',
  'REASON',
  'MISSING_INFO',
  'PROBLEMS_FOUND',
  'ACTION',
  'SAFE_VERSION',
  'QUESTION_TO_AUTHOR',
  'SERBIAN_VERSION',
  'ADMIN_NOTE',
] as const;

export type OutputFieldLabel = (typeof OUTPUT_FIELD_LABELS)[number];

/**
 * Maps field labels to their camelCase keys in AnalysisResult.
 */
export const FIELD_LABEL_TO_KEY: Record<OutputFieldLabel, keyof AnalysisResult> = {
  VERDICT: 'verdict',
  POST_TYPE: 'postType',
  LANGUAGE: 'language',
  RISK_LEVEL: 'riskLevel',
  REASON: 'reason',
  MISSING_INFO: 'missingInfo',
  PROBLEMS_FOUND: 'problemsFound',
  ACTION: 'action',
  SAFE_VERSION: 'safeVersion',
  QUESTION_TO_AUTHOR: 'questionToAuthor',
  SERBIAN_VERSION: 'serbianVersion',
  ADMIN_NOTE: 'adminNote',
};

/**
 * Valid verdict values.
 */
export const VALID_VERDICTS: Verdict[] = [
  'APPROVE',
  'APPROVE_WITH_EDITS',
  'NEEDS_CLARIFICATION',
  'REJECT',
  'ESCALATE',
];

/**
 * Valid post type values.
 */
export const VALID_POST_TYPES: PostType[] = [
  'vacancy',
  'worker_review',
  'job_request',
  'question',
  'warning',
  'recommendation',
  'admin_post',
  'spam',
  'conflict',
  'unclear',
];

/**
 * Valid language values.
 */
export const VALID_LANGUAGES: Language[] = [
  'Serbian',
  'Russian',
  'Ukrainian',
  'Hungarian',
  'Romanian',
  'Other',
];

/**
 * Valid risk level values.
 */
export const VALID_RISK_LEVELS: RiskLevel[] = ['low', 'medium', 'high'];

/**
 * Test case definition for the test suite.
 */
export interface TestCase {
  id: string;
  description: string;
  input: string;
  expectedVerdict: Verdict;
  expectedPostType: PostType;
  expectedRiskLevel: RiskLevel;
  expectedLanguage: Language;
  /** Key problems that should appear in problemsFound */
  expectedProblems: string[];
  notes: string;
}

/**
 * CLI input options.
 */
export interface CLIOptions {
  text?: string;
  postId?: string;
  stdin: boolean;
  batch?: string;
  json: boolean;
}

/**
 * Validation error from checking an AnalysisResult.
 */
export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Content for the safe version / Serbian version fields
 * when no rewrite is needed.
 */
export const NOT_NEEDED = 'not needed';
