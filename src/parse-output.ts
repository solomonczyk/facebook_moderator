import {
  type AnalysisResult,
  type Verdict,
  type PostType,
  type Language,
  type RiskLevel,
  OUTPUT_FIELD_LABELS,
} from './types.js';

/**
 * Parses the text-format LLM output into a structured AnalysisResult.
 *
 * The LLM output follows the spec format:
 *   VERDICT:
 *   <value>
 *   POST_TYPE:
 *   <value>
 *   ...
 *
 * Multi-line values (MISSING_INFO, PROBLEMS_FOUND, etc.) are parsed until
 * the next field label or end of text.
 */
export function parseAnalysisOutput(raw: string): AnalysisResult {
  const fields = extractFields(raw);

  return {
    verdict: parseVerdict(fields['VERDICT'] ?? ''),
    postType: parsePostType(fields['POST_TYPE'] ?? ''),
    language: parseLanguage(fields['LANGUAGE'] ?? ''),
    riskLevel: parseRiskLevel(fields['RISK_LEVEL'] ?? ''),
    reason: fields['REASON']?.trim() || '',
    missingInfo: fields['MISSING_INFO']?.trim() || 'none',
    problemsFound: fields['PROBLEMS_FOUND']?.trim() || 'none',
    action: fields['ACTION']?.trim() || '',
    safeVersion: fields['SAFE_VERSION']?.trim() || 'not needed',
    questionToAuthor: fields['QUESTION_TO_AUTHOR']?.trim() || 'not needed',
    serbianVersion: fields['SERBIAN_VERSION']?.trim() || 'not needed',
    adminNote: fields['ADMIN_NOTE']?.trim() || '',
  };
}

/**
 * Extract field values from the raw text output.
 * Each field starts with "FIELD_NAME:" on its own line, followed by content.
 * Stops at the next field label or end of text.
 */
function extractFields(raw: string): Record<string, string> {
  const result: Record<string, string> = {};

  // Remove markdown code fences if present
  let text = raw.trim();
  if (text.startsWith('```')) {
    text = text.replace(/^```[\w]*\n?/, '').replace(/\n?```$/, '');
  }

  // Match each label literally at the start of a line

  // Find all field boundaries
  const boundaries: Array<{ label: string; start: number; contentStart: number }> = [];
  let match: RegExpExecArray | null;

  // Use a simpler approach: split by field labels
  // First find all positions
  for (const label of OUTPUT_FIELD_LABELS) {
    const pattern = new RegExp(`^${escapeRegex(label)}:\\s*$`, 'gm');
    while ((match = pattern.exec(text)) !== null) {
      boundaries.push({
        label,
        start: match.index,
        contentStart: match.index + match[0].length,
      });
    }
  }

  // Sort by position in text
  boundaries.sort((a, b) => a.start - b.start);

  // Extract content for each field
  for (let i = 0; i < boundaries.length; i++) {
    const current = boundaries[i]!;
    const nextBoundary = boundaries[i + 1];
    const contentEnd = nextBoundary ? nextBoundary.start : text.length;
    const content = text.slice(current.contentStart, contentEnd).trim();

    // Handle the case where content is on the same line as the label
    // by checking if the original text had the content on the same line
    // (our regex matched the label line including newline, so content is after)
    result[current.label] = content;
  }

  return result;
}

/**
 * Alternative parsing approach: split by known labels.
 * This is more robust for LLM output that may have slight formatting variations.
 */
export function parseAnalysisOutputFallback(raw: string): AnalysisResult {
  let text = raw.trim();
  // Remove markdown code fences
  if (text.startsWith('```')) {
    text = text.replace(/^```[\w]*\n?/, '').replace(/\n?```$/, '');
  }

  const fields: Record<string, string> = {};

  for (const label of OUTPUT_FIELD_LABELS) {
    // Match "LABEL:\n<content>" or "LABEL: <content>"
    const patterns = [
      new RegExp(`${escapeRegex(label)}:\\s*\\n([\\s\\S]*?)(?=\\n(?:${OUTPUT_FIELD_LABELS.map(escapeRegex).join('|')}):|$)`, 'i'),
      new RegExp(`${escapeRegex(label)}:\\s*(.+?)(?=\\n(?:${OUTPUT_FIELD_LABELS.map(escapeRegex).join('|')}):|$)`, 'i'),
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match && match[1]) {
        fields[label] = match[1].trim();
        break;
      }
    }
  }

  return {
    verdict: parseVerdict(fields['VERDICT'] ?? ''),
    postType: parsePostType(fields['POST_TYPE'] ?? ''),
    language: parseLanguage(fields['LANGUAGE'] ?? ''),
    riskLevel: parseRiskLevel(fields['RISK_LEVEL'] ?? ''),
    reason: fields['REASON'] ?? '',
    missingInfo: fields['MISSING_INFO'] ?? 'none',
    problemsFound: fields['PROBLEMS_FOUND'] ?? 'none',
    action: fields['ACTION'] ?? '',
    safeVersion: fields['SAFE_VERSION'] ?? 'not needed',
    questionToAuthor: fields['QUESTION_TO_AUTHOR'] ?? 'not needed',
    serbianVersion: fields['SERBIAN_VERSION'] ?? 'not needed',
    adminNote: fields['ADMIN_NOTE'] ?? '',
  };
}

function parseVerdict(raw: string): Verdict {
  const upper = raw.trim().toUpperCase();
  if (['APPROVE', 'APPROVE_WITH_EDITS', 'NEEDS_CLARIFICATION', 'REJECT', 'ESCALATE'].includes(upper)) {
    return upper as Verdict;
  }
  return 'ESCALATE'; // Safe default
}

function parsePostType(raw: string): PostType {
  const lower = raw.trim().toLowerCase();
  if (
    [
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
    ].includes(lower)
  ) {
    return lower as PostType;
  }
  return 'unclear';
}

function parseLanguage(raw: string): Language {
  const cleaned = raw.trim();
  const lower = cleaned.toLowerCase();
  if (lower.includes('serbian') || lower.includes('srpski') || lower === 'sr') return 'Serbian';
  if (lower.includes('russian') || lower.includes('ruski') || lower === 'ru') return 'Russian';
  if (lower.includes('ukrainian') || lower.includes('ukrajinski') || lower === 'uk') return 'Ukrainian';
  if (lower.includes('hungarian') || lower.includes('mađarski') || lower === 'hu') return 'Hungarian';
  if (lower.includes('romanian') || lower.includes('rumunski') || lower === 'ro') return 'Romanian';
  return 'Other';
}

function parseRiskLevel(raw: string): RiskLevel {
  const lower = raw.trim().toLowerCase();
  if (lower === 'low') return 'low';
  if (lower === 'medium') return 'medium';
  if (lower === 'high') return 'high';
  return 'high'; // Safe default — when in doubt, treat as high risk
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
