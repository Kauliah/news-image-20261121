// Entry program for make.fun news-image-20261121.
//
// The entry image (entry.png, next to this file) is copied into the output
// directory the harness names through MAKEFUN_OUTPUT_DIR (falling back to
// "out" for a local run). Standard library only; runs on Node 22.
//
// Local run:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const targetDir = process.env.MAKEFUN_OUTPUT_DIR || "out";

if (!existsSync(source)) {
  console.error(`entry.png not found next to main.ts (${source})`);
  process.exit(1);
}

mkdirSync(targetDir, { recursive: true });
copyFileSync(source, join(targetDir, "entry.png"));
console.log(`entry.png -> ${join(targetDir, "entry.png")}`);
