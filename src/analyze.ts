import Anthropic from '@anthropic-ai/sdk';
import { loadConfig } from './config.js';
import { buildMessages } from './prompt.js';
import { parseAnalysisOutput, parseAnalysisOutputFallback } from './parse-output.js';
import { validateAnalysisResult } from './validate.js';
import type { AnalysisResult } from './types.js';

export interface AnalyzeOptions {
  /** The post text to analyze */
  text: string;
  /** Optional post ID for tracking */
  postId?: string;
}

export interface AnalyzeSuccess {
  success: true;
  result: AnalysisResult;
}

export interface AnalyzeError {
  success: false;
  error: string;
  rawOutput?: string;
}

export type AnalyzeResponse = AnalyzeSuccess | AnalyzeError;

/**
 * Analyze a post using the Anthropic API.
 * Returns a structured AnalysisResult or an error.
 */
export async function analyzePost(opts: AnalyzeOptions): Promise<AnalyzeResponse> {
  const config = loadConfig();

  if (!config.anthropicApiKey) {
    return {
      success: false,
      error: 'ANTHROPIC_API_KEY is not set. Set it in the environment to use the copilot.',
    };
  }

  const { systemPrompt, userMessage } = buildMessages(opts.text);

  const client = new Anthropic({ apiKey: config.anthropicApiKey });

  try {
    const response = await client.messages.create({
      model: config.anthropicModel,
      max_tokens: config.maxTokens,
      system: systemPrompt,
      messages: [
        {
          role: 'user',
          content: userMessage,
        },
      ],
    });

    // Extract text from response
    const textBlocks = response.content.filter((block) => block.type === 'text');
    if (textBlocks.length === 0) {
      return {
        success: false,
        error: 'LLM returned no text content in response.',
      };
    }

    const rawOutput = textBlocks.map((block) => (block.type === 'text' ? block.text : '')).join('\n');

    // Try primary parser first, then fallback
    let result: AnalysisResult;
    try {
      result = parseAnalysisOutput(rawOutput);
    } catch {
      try {
        result = parseAnalysisOutputFallback(rawOutput);
      } catch (fallbackErr) {
        return {
          success: false,
          error: `Failed to parse LLM output: ${fallbackErr instanceof Error ? fallbackErr.message : String(fallbackErr)}`,
          rawOutput,
        };
      }
    }

    // Validate the result
    const validationErrors = validateAnalysisResult(result);
    if (validationErrors.length > 0) {
      // Return the result but note the validation issues
      // The admin can still use it with awareness of the gaps
      return {
        success: true,
        result: {
          ...result,
          adminNote:
            result.adminNote +
            `\n[VALIDATION WARNINGS: ${validationErrors.map((e) => `${e.field}: ${e.message}`).join('; ')}]`,
        },
      };
    }

    return { success: true, result };
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err);

    // Detect common API errors
    if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
      return {
        success: false,
        error: 'Authentication failed. Check your ANTHROPIC_API_KEY.',
      };
    }

    if (errorMessage.includes('429') || errorMessage.includes('rate')) {
      return {
        success: false,
        error: 'API rate limit reached. Wait a moment and try again.',
      };
    }

    return {
      success: false,
      error: `API error: ${errorMessage}`,
    };
  }
}
