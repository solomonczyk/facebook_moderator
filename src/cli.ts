import { createInterface } from 'node:readline';
import { analyzePost } from './analyze.js';
import { NOT_NEEDED } from './types.js';
import type { AnalysisResult } from './types.js';

const SEPARATOR = '='.repeat(60);
const THIN_SEP = '-'.repeat(60);

/**
 * Format an AnalysisResult for display in the terminal.
 */
export function formatResult(result: AnalysisResult): string {
  const lines: string[] = [
    SEPARATOR,
    `VERDICT:       ${colorVerdict(result.verdict)}`,
    `POST_TYPE:     ${result.postType}`,
    `LANGUAGE:      ${result.language}`,
    `RISK_LEVEL:    ${colorRisk(result.riskLevel)}`,
    THIN_SEP,
    `REASON:        ${wrapText(result.reason, 60)}`,
    THIN_SEP,
    `MISSING_INFO:  ${result.missingInfo}`,
    `PROBLEMS:      ${result.problemsFound}`,
    `ACTION:        ${result.action}`,
    THIN_SEP,
    `SAFE_VERSION:      ${result.safeVersion === NOT_NEEDED ? '(not needed)' : result.safeVersion}`,
    `QUESTION_TO_AUTHOR: ${result.questionToAuthor === NOT_NEEDED ? '(not needed)' : result.questionToAuthor}`,
    `SERBIAN_VERSION:    ${result.serbianVersion === NOT_NEEDED ? '(not needed)' : result.serbianVersion}`,
    THIN_SEP,
    `ADMIN_NOTE:    ${result.adminNote}`,
    SEPARATOR,
  ];

  return lines.join('\n');
}

/**
 * Format the result as compact JSON.
 */
export function formatResultJson(result: AnalysisResult): string {
  return JSON.stringify(result, null, 2);
}

function colorVerdict(verdict: string): string {
  // Simple ANSI coloring — works in most terminals
  const colors: Record<string, string> = {
    APPROVE: '\x1b[32m',             // Green
    APPROVE_WITH_EDITS: '\x1b[33m',  // Yellow
    NEEDS_CLARIFICATION: '\x1b[36m', // Cyan
    REJECT: '\x1b[31m',              // Red
    ESCALATE: '\x1b[35m',            // Magenta
  };
  const reset = '\x1b[0m';
  return `${colors[verdict] ?? ''}${verdict}${reset}`;
}

function colorRisk(risk: string): string {
  const colors: Record<string, string> = {
    low: '\x1b[32m',
    medium: '\x1b[33m',
    high: '\x1b[31m',
  };
  const reset = '\x1b[0m';
  return `${colors[risk] ?? ''}${risk}${reset}`;
}

function wrapText(text: string, width: number): string {
  // Simple word wrap
  const words = text.split(' ');
  const lines: string[] = [];
  let current = '';

  for (const word of words) {
    if ((current + word).length > width && current.length > 0) {
      lines.push(current.trimEnd());
      current = word + ' ';
    } else {
      current += word + ' ';
    }
  }
  if (current.trim()) lines.push(current.trimEnd());

  return lines.join('\n               ');
}

/**
 * Run interactive CLI mode.
 * Reads posts from stdin (piped or typed) until EOF or "---END---".
 */
export async function runInteractiveCLI(): Promise<void> {
  console.log(SEPARATOR);
  console.log('Facebook Group Admin Copilot');
  console.log('Sezonski rad Srbija | Poslovi i iskustva radnika');
  console.log(SEPARATOR);
  console.log();
  console.log('Paste the post text to analyze.');
  console.log('Type "---END---" on a new line to submit, or press Ctrl+D.');
  console.log('Type "quit" to exit.');
  console.log();

  const rl = createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: '',
  });

  let lines: string[] = [];
  let collecting = false;

  rl.on('line', async (line: string) => {
    const trimmed = line.trim();

    if (trimmed === 'quit' && !collecting) {
      console.log('Exiting. До виђења!');
      rl.close();
      process.exit(0);
    }

    if (trimmed === '---END---') {
      const text = lines.join('\n').trim();
      lines = [];
      collecting = false;

      if (!text) {
        console.log('(No text provided. Paste text or type quit to exit.)');
        return;
      }

      console.log('\nAnalyzing...\n');
      const response = await analyzePost({ text });

      if (response.success) {
        console.log(formatResult(response.result));
      } else {
        console.log(`ERROR: ${response.error}`);
        if (response.rawOutput) {
          console.log(`\nRaw LLM output:\n${response.rawOutput}`);
        }
      }
      console.log('\nPaste next post, or type "quit" to exit.\n');
      return;
    }

    if (!collecting && trimmed.length > 0) {
      collecting = true;
    }

    if (collecting) {
      lines.push(line);
    }
  });

  rl.on('close', () => {
    // Handle EOF (Ctrl+D) — submit whatever was collected
    const text = lines.join('\n').trim();
    if (text) {
      console.log('\nAnalyzing...\n');
      analyzePost({ text }).then((response) => {
        if (response.success) {
          console.log(formatResult(response.result));
        } else {
          console.log(`ERROR: ${response.error}`);
        }
        process.exit(0);
      });
    } else {
      process.exit(0);
    }
  });
}
