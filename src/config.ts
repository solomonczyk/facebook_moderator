/**
 * Environment and configuration loading for the Facebook Admin Copilot.
 */

export interface Config {
  anthropicApiKey: string;
  anthropicModel: string;
  maxTokens: number;
}

let cachedConfig: Config | null = null;

/**
 * Load configuration from environment variables.
 * Cached after first call.
 */
export function loadConfig(): Config {
  if (cachedConfig) return cachedConfig;

  const apiKey = process.env['ANTHROPIC_API_KEY'] || '';
  const model = process.env['ANTHROPIC_MODEL'] || 'claude-sonnet-4-20250514';

  cachedConfig = {
    anthropicApiKey: apiKey,
    anthropicModel: model,
    maxTokens: 4096,
  };

  return cachedConfig;
}

/**
 * Check if we have an API key configured (needed for live LLM calls).
 */
export function hasApiKey(): boolean {
  const config = loadConfig();
  return config.anthropicApiKey.length > 0;
}

/**
 * Validate that required config is present.
 * Returns a list of missing items (empty = all good).
 */
export function validateConfig(): string[] {
  const issues: string[] = [];

  if (!process.env['ANTHROPIC_API_KEY']) {
    issues.push('ANTHROPIC_API_KEY environment variable is not set');
  }

  return issues;
}

/**
 * Clear cached config (useful for testing).
 */
export function clearConfigCache(): void {
  cachedConfig = null;
}
