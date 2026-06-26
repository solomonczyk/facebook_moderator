import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import {
  loadSystemPrompt,
  validatePromptStructure,
  estimateTokens,
  buildMessages,
  clearPromptCache,
} from '../src/prompt.js';

describe('System Prompt', () => {
  beforeAll(() => {
    clearPromptCache();
  });

  afterAll(() => {
    clearPromptCache();
  });

  it('loads successfully from SYSTEM_PROMPT.md', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toBeTruthy();
    expect(prompt.length).toBeGreaterThan(1000);
  });

  it('is cached on second load', () => {
    const first = loadSystemPrompt();
    const second = loadSystemPrompt();
    expect(first).toBe(second); // Same reference = cached
  });

  it('contains all required sections', () => {
    const missing = validatePromptStructure();
    expect(missing, `Missing sections: ${missing.join(', ')}`).toHaveLength(0);
  });

  it('contains role definition', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## ROLE');
    expect(prompt).toContain('Admin Copilot');
  });

  it('contains operator-in-the-loop constraint', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('operator-in-the-loop');
  });

  it('contains verdict decision tree', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## VERDICT DECISION TREE');
    expect(prompt).toContain('APPROVE');
    expect(prompt).toContain('REJECT');
    expect(prompt).toContain('ESCALATE');
    expect(prompt).toContain('APPROVE_WITH_EDITS');
    expect(prompt).toContain('NEEDS_CLARIFICATION');
  });

  it('contains post type taxonomy', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## POST TYPE TAXONOMY');
    expect(prompt).toContain('vacancy');
    expect(prompt).toContain('worker_review');
    expect(prompt).toContain('spam');
    expect(prompt).toContain('conflict');
  });

  it('contains output format specification', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## OUTPUT FORMAT');
    expect(prompt).toContain('VERDICT:');
    expect(prompt).toContain('POST_TYPE:');
    expect(prompt).toContain('LANGUAGE:');
    expect(prompt).toContain('RISK_LEVEL:');
    expect(prompt).toContain('REASON:');
    expect(prompt).toContain('MISSING_INFO:');
    expect(prompt).toContain('PROBLEMS_FOUND:');
    expect(prompt).toContain('ACTION:');
    expect(prompt).toContain('SAFE_VERSION:');
    expect(prompt).toContain('QUESTION_TO_AUTHOR:');
    expect(prompt).toContain('SERBIAN_VERSION:');
    expect(prompt).toContain('ADMIN_NOTE:');
  });

  it('contains few-shot examples', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## FEW-SHOT EXAMPLES');
    // Should have at least 3 examples
    const exampleCount = (prompt.match(/### Example \d+/g) || []).length;
    expect(exampleCount).toBeGreaterThanOrEqual(3);
  });

  it('contains moderation rules', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## MODERATION RULES');
    expect(prompt).toContain('Spam Detection');
    expect(prompt).toContain('Fraud Detection');
    expect(prompt).toContain('Insult');
    expect(prompt).toContain('Personal Data');
  });

  it('contains vacancy required fields', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('Mesto rada');
    expect(prompt).toContain('Plata');
    expect(prompt).toContain('Smeštaj');
    expect(prompt).toContain('Kontakt telefon');
  });

  it('contains safe rewriting rules', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('Safe Rewriting');
    expect(prompt).toContain('po mom iskustvu');
  });

  it('contains admin response templates', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## ADMIN RESPONSE TEMPLATES');
  });

  it('contains language handling section', () => {
    const prompt = loadSystemPrompt();
    expect(prompt).toContain('## LANGUAGE HANDLING');
    expect(prompt).toContain('Serbian');
    expect(prompt).toContain('Russian');
    expect(prompt).toContain('Ukrainian');
    expect(prompt).toContain('Hungarian');
    expect(prompt).toContain('Romanian');
  });

  it('fits within reasonable token limit', () => {
    const tokens = estimateTokens();
    // The system prompt should fit within ~8000 tokens
    // (leaving room for the user message and response)
    expect(tokens).toBeLessThan(8000);
  });

  it('builds messages with user text', () => {
    const { systemPrompt, userMessage } = buildMessages('Test post text');
    expect(systemPrompt).toBeTruthy();
    expect(userMessage).toContain('Test post text');
    expect(userMessage).toContain('TEKST ZA ANALIZU');
  });
});
