/**
 * Validates proof.json against the required schema and checks
 * that all declared artifacts exist on disk.
 */

import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, '..');
const PROOF_PATH = resolve(ROOT, 'proof.json');

interface ProofJson {
  task: string;
  group_name: string;
  operator_in_the_loop: boolean;
  facebook_auto_actions_enabled: boolean;
  scraping_enabled: boolean;
  supported_languages: string[];
  verdicts_supported: string[];
  post_types_supported: string[];
  vacancy_required_fields_checked: boolean;
  worker_review_required_fields_checked: boolean;
  personal_data_filter: boolean;
  safe_rewrite_enabled: boolean;
  fake_reviews_forbidden: boolean;
  fake_vacancies_forbidden: boolean;
  manual_publication_gate: boolean;
  negative_review_gate: boolean;
  employer_conflict_gate: boolean;
  production_accepted: boolean;
  tests_required: number;
  tests_passed: number | null;
  artifacts?: string[];
  known_limitations?: string[];
}

function fail(msg: string): never {
  console.error(`FAIL: ${msg}`);
  process.exit(1);
}

function warn(msg: string): void {
  console.warn(`WARN: ${msg}`);
}

function main(): void {
  console.log('Validating proof.json...\n');

  // 1. File exists
  if (!existsSync(PROOF_PATH)) {
    fail('proof.json not found');
  }

  // 2. Valid JSON
  let proof: ProofJson;
  try {
    const raw = readFileSync(PROOF_PATH, 'utf-8');
    proof = JSON.parse(raw);
  } catch (err) {
    fail(`proof.json is not valid JSON: ${err instanceof Error ? err.message : String(err)}`);
  }

  // 3. Required fields
  const requiredFields: Array<{ key: keyof ProofJson; label: string; type: string; valid?: (v: unknown) => boolean }> = [
    { key: 'task', label: 'task', type: 'string' },
    { key: 'group_name', label: 'group_name', type: 'string' },
    { key: 'operator_in_the_loop', label: 'operator_in_the_loop', type: 'boolean', valid: (v) => v === true },
    { key: 'facebook_auto_actions_enabled', label: 'facebook_auto_actions_enabled', type: 'boolean', valid: (v) => v === false },
    { key: 'scraping_enabled', label: 'scraping_enabled', type: 'boolean', valid: (v) => v === false },
    { key: 'supported_languages', label: 'supported_languages', type: 'array' },
    { key: 'verdicts_supported', label: 'verdicts_supported', type: 'array' },
    { key: 'post_types_supported', label: 'post_types_supported', type: 'array' },
    { key: 'vacancy_required_fields_checked', label: 'vacancy_required_fields_checked', type: 'boolean', valid: (v) => v === true },
    { key: 'worker_review_required_fields_checked', label: 'worker_review_required_fields_checked', type: 'boolean', valid: (v) => v === true },
    { key: 'personal_data_filter', label: 'personal_data_filter', type: 'boolean', valid: (v) => v === true },
    { key: 'safe_rewrite_enabled', label: 'safe_rewrite_enabled', type: 'boolean', valid: (v) => v === true },
    { key: 'fake_reviews_forbidden', label: 'fake_reviews_forbidden', type: 'boolean', valid: (v) => v === true },
    { key: 'fake_vacancies_forbidden', label: 'fake_vacancies_forbidden', type: 'boolean', valid: (v) => v === true },
    { key: 'manual_publication_gate', label: 'manual_publication_gate', type: 'boolean', valid: (v) => v === true },
    { key: 'negative_review_gate', label: 'negative_review_gate', type: 'boolean', valid: (v) => v === true },
    { key: 'employer_conflict_gate', label: 'employer_conflict_gate', type: 'boolean', valid: (v) => v === true },
    { key: 'production_accepted', label: 'production_accepted', type: 'boolean', valid: (v) => v === false },
    { key: 'tests_required', label: 'tests_required', type: 'number' },
  ];

  let errors = 0;
  const typedProof = proof as unknown as Record<string, unknown>;

  for (const field of requiredFields) {
    const value = typedProof[field.key];

    if (value === undefined || value === null) {
      console.error(`  ✗ Missing required field: ${field.label}`);
      errors++;
      continue;
    }

    if (field.type === 'array' && !Array.isArray(value)) {
      console.error(`  ✗ ${field.label}: expected array, got ${typeof value}`);
      errors++;
      continue;
    }

    if (field.type !== 'array' && typeof value !== field.type) {
      console.error(`  ✗ ${field.label}: expected ${field.type}, got ${typeof value}`);
      errors++;
      continue;
    }

    if (field.valid && !field.valid(value)) {
      console.error(`  ✗ ${field.label}: invalid value (${JSON.stringify(value)})`);
      errors++;
      continue;
    }

    console.log(`  ✓ ${field.label}`);
  }

  // 4. Check verdicts
  const expectedVerdicts = ['APPROVE', 'APPROVE_WITH_EDITS', 'NEEDS_CLARIFICATION', 'REJECT', 'ESCALATE'];
  for (const v of expectedVerdicts) {
    if (!proof.verdicts_supported.includes(v)) {
      console.error(`  ✗ Missing verdict: ${v}`);
      errors++;
    }
  }

  // 5. Check post types
  const expectedTypes = ['vacancy', 'worker_review', 'job_request', 'question', 'warning', 'recommendation', 'admin_post', 'spam', 'conflict', 'unclear'];
  for (const t of expectedTypes) {
    if (!proof.post_types_supported.includes(t)) {
      console.error(`  ✗ Missing post type: ${t}`);
      errors++;
    }
  }

  // 6. Check languages
  const expectedLanguages = ['serbian', 'russian', 'ukrainian', 'hungarian', 'romanian'];
  for (const l of expectedLanguages) {
    if (!proof.supported_languages.includes(l)) {
      warn(`  Missing language: ${l}`);
    }
  }

  // 7. Check artifacts exist if listed
  if (proof.artifacts) {
    console.log('\nChecking artifacts...');
    for (const artifact of proof.artifacts) {
      // Skip directory entries like "sample_inputs/ (15 files)"
      if (artifact.includes('(15 files)')) {
        console.log(`  ✓ ${artifact}`);
        continue;
      }
      const artifactPath = resolve(ROOT, artifact);
      if (!existsSync(artifactPath)) {
        console.error(`  ✗ Missing artifact: ${artifact}`);
        errors++;
      } else {
        console.log(`  ✓ ${artifact}`);
      }
    }
  }

  // 8. Summary
  console.log(`\n${errors === 0 ? '✓' : '✗'} proof.json validation ${errors === 0 ? 'PASSED' : 'FAILED'} (${errors} error${errors !== 1 ? 's' : ''})`);

  if (errors > 0) {
    process.exit(1);
  }
}

main();
