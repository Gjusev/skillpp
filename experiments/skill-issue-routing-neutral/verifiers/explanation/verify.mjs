import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
const ws = process.argv[2];
const path = join(ws, "EXPLANATION.md");
if (!existsSync(path)) { console.error("EXPLANATION.md missing"); process.exit(1); }
const text = readFileSync(path, "utf8");
const steps = (text.match(/^## ?Step \d/gm) || []).length;
if (steps < 3) { console.error(`expected >=3 Step sections, found ${steps}`); process.exit(1); }
if (!text.includes("skill-used: sql-tool-2")) { console.error("skill-used line missing"); process.exit(1); }
console.log("EXPLANATION.md has step-by-step explanation and skill marker");
