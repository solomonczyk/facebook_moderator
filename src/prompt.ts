import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROMPT_PATH = resolve(__dirname, '..', 'SYSTEM_PROMPT.md');

const REQUIRED_SECTIONS = [
  '## ROLE',
  '## GROUP CONTEXT',
  '## CORE PRINCIPLES',
  '## POST TYPE TAXONOMY',
  '## VERDICT DECISION TREE',
  '## MODERATION RULES',
  '## VACANCY MODERATION RULES',
  '## WORKER REVIEW MODERATION RULES',
  '## PERSONAL DATA RULES',
  '## LANGUAGE HANDLING',
  '## ADMIN RESPONSE TEMPLATES',
  '## OUTPUT FORMAT',
  '## FEW-SHOT EXAMPLES',
];

let cachedPrompt: string | null = null;

/**
 * Load the system prompt from SYSTEM_PROMPT.md.
 * Caches in memory after first load.
 */
export function loadSystemPrompt(): string {
  if (cachedPrompt) return cachedPrompt;

  try {
    cachedPrompt = readFileSync(PROMPT_PATH, 'utf-8');
  } catch {
    throw new Error(
      `SYSTEM_PROMPT.md not found at ${PROMPT_PATH}. The system prompt is required for the copilot to function.`,
    );
  }

  if (cachedPrompt.trim().length === 0) {
    throw new Error('SYSTEM_PROMPT.md is empty. The system prompt is required.');
  }

  return cachedPrompt;
}

/**
 * Validate that the system prompt contains all required sections.
 * Returns a list of missing sections (empty = valid).
 */
export function validatePromptStructure(): string[] {
  const prompt = loadSystemPrompt();
  const missing: string[] = [];

  for (const section of REQUIRED_SECTIONS) {
    if (!prompt.includes(section)) {
      missing.push(section);
    }
  }

  return missing;
}

/**
 * Estimate token count for the system prompt.
 * Uses a simple heuristic: ~4 characters per token for Serbian/English mixed text.
 * Returns estimated token count.
 */
export function estimateTokens(): number {
  const prompt = loadSystemPrompt();
  return Math.ceil(prompt.length / 4);
}

/**
 * Build the full messages array for the Anthropic API.
 */
export function buildMessages(userText: string): {
  systemPrompt: string;
  userMessage: string;
} {
  const systemPrompt = loadSystemPrompt();
  const userMessage = `Analiziraj sledeći tekst za Facebook grupu "Sezonski rad Srbija | Poslovi i iskustva radnika". Vrati isključivo format sa 12 polja koji je definisan u OUTPUT FORMAT sekciji system prompta.

TEKST ZA ANALIZU:
---
${userText}
---`;

  return { systemPrompt, userMessage };
}

/**
 * Clear the cached prompt (useful for testing when the file changes).
 */
export function clearPromptCache(): void {
  cachedPrompt = null;
}
