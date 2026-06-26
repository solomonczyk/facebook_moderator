import { readFileSync } from 'node:fs';
import { analyzePost } from './analyze.js';
import { formatResult, formatResultJson } from './cli.js';

interface Args {
  stdin: boolean;
  file?: string;
  json: boolean;
  postId?: string;
}

function parseArgs(argv: string[]): Args {
  const args: Args = { stdin: false, json: false };

  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    switch (arg) {
      case '--stdin':
        args.stdin = true;
        break;
      case '--json':
        args.json = true;
        break;
      case '--file':
        args.file = argv[++i];
        break;
      case '--post-id':
        args.postId = argv[++i];
        break;
      case '--help':
      case '-h':
        printHelp();
        process.exit(0);
        break;
      default:
        // Assume it's a file if it exists
        if (!args.file) {
          args.file = arg;
        }
    }
  }

  return args;
}

function printHelp(): void {
  console.log(`
Facebook Group Admin Copilot
Sezonski rad Srbija | Poslovi i iskustva radnika

USAGE:
  npm start -- [OPTIONS] [file]

OPTIONS:
  --stdin        Read post text from stdin (pipe mode)
  --file <path>  Read post text from a file
  --json         Output result as JSON instead of formatted text
  --post-id <id> Attach a post ID for tracking
  --help, -h     Show this help

EXAMPLES:
  npm start                          Interactive mode
  npm start -- --stdin < post.txt    Pipe text from file
  npm start -- --file post.txt       Read text from file
  npm start -- --json < post.txt     JSON output mode
  npm start -- post.txt              Shorthand for --file
`);
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);

  // Determine the text to analyze
  let text: string;

  if (args.stdin) {
    // Read from stdin
    text = readFileSync(process.stdin.fd, 'utf-8').trim();
  } else if (args.file) {
    // Read from file
    text = readFileSync(args.file, 'utf-8').trim();
  } else {
    // Interactive mode — delegate to CLI
    const { runInteractiveCLI } = await import('./cli.js');
    await runInteractiveCLI();
    return;
  }

  if (!text) {
    console.error('Error: No text provided. Use --stdin, --file, or run without arguments for interactive mode.');
    process.exit(1);
  }

  const response = await analyzePost({ text, postId: args.postId });

  if (response.success) {
    if (args.json) {
      console.log(formatResultJson(response.result));
    } else {
      console.log(formatResult(response.result));
    }
  } else {
    console.error(`ERROR: ${response.error}`);
    if (response.rawOutput) {
      console.error(`\nRaw LLM output:\n${response.rawOutput}`);
    }
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
