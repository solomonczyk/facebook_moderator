/**
 * Validates that all expected output JSON files in sample_outputs/
 * conform to the AnalysisResult structure.
 */

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateAnalysisResult } from '../src/validate.js';
import type { AnalysisResult } from '../src/types.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const OUTPUTS_DIR = resolve(ROOT, 'sample_outputs');

function fail(msg: string): never {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

function main(): void {
  console.log('Validating sample outputs...\n');

  if (!existsSync(OUTPUTS_DIR)) {
    fail(`sample_outputs/ directory not found at ${OUTPUTS_DIR}`);
  }

  const files = readdirSync(OUTPUTS_DIR)
    .filter((f) => extname(f) === '.json')
    .sort();

  if (files.length === 0) {
    fail('No expected output files found in sample_outputs/');
  }

  console.log(`Found ${files.length} expected output files\n`);

  let errors = 0;

  for (const file of files) {
    const filePath = resolve(OUTPUTS_DIR, file);

    try {
      const raw = readFileSync(filePath, 'utf-8');
      const result = JSON.parse(raw) as AnalysisResult;

      // Validate the result
      const validationErrors = validateAnalysisResult(result);

      if (validationErrors.length > 0) {
        console.error(`  ✗ ${file}`);
        for (const err of validationErrors) {
          console.error(`      ${err.field}: ${err.message}`);
        }
        errors++;
      } else {
        console.log(`  ✓ ${file} — ${result.verdict} | ${result.postType} | ${result.language} | ${result.riskLevel}`);
      }
    } catch (err) {
      console.error(`  ✗ ${file} — Failed to parse/validate: ${err instanceof Error ? err.message : String(err)}`);
      errors++;
    }
  }

  console.log(`\n${errors === 0 ? '✓' : '✗'} Schema validation ${errors === 0 ? 'PASSED' : 'FAILED'} (${errors} error${errors !== 1 ? 's' : ''})`);

  if (errors > 0) {
    process.exit(1);
  }
}

main();
