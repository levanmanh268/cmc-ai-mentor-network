// Validate the rendering of Mermaid diagrams, not just Markdown patterns.
// A failing diagram identifies its Markdown file and ordinal.
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve, relative } from "node:path";
import { spawnSync } from "node:child_process";

const root = resolve(import.meta.dirname, "..");
const markdownPaths = [join(root, "README.md")];
function walk(folder) {
  for (const item of readdirSync(folder, { withFileTypes: true })) {
    const path = join(folder, item.name);
    if (item.isDirectory()) walk(path);
    else if (item.isFile() && item.name.toLowerCase().endsWith(".md")) markdownPaths.push(path);
  }
}
walk(join(root, "docs"));

const fence = String.fromCharCode(96).repeat(3);
const opener = new RegExp("^" + fence + "mermaid[ \\t]*\\r?$", "gm");
const block = new RegExp("^" + fence + "mermaid[ \\t]*\\r?\\n([\\s\\S]*?)^" + fence + "[ \\t]*\\r?$", "gm");
const diagrams = [];
for (const file of markdownPaths) {
  const markdown = readFileSync(file, "utf8");
  const opens = [...markdown.matchAll(opener)].length;
  const matches = [...markdown.matchAll(block)];
  if (opens !== matches.length) throw Error(relative(root, file) + ": missing Mermaid closing fence");
  matches.forEach((match, i) => diagrams.push({
    file: relative(root, file), index: i + 1, code: match[1].trim() + "\n"
  }));
}
const count = diagrams.filter(d => d.file === "docs/architecture.md").length;
if (count !== 5) throw Error("docs/architecture.md: expected 5 diagrams; got " + count);

const cli = join(root, "node_modules", ".bin", process.platform === "win32" ? "mmdc.cmd" : "mmdc");
if (!existsSync(cli)) throw Error("Missing Mermaid CLI. Install @mermaid-js/mermaid-cli.");
const scratch = mkdtempSync(join(tmpdir(), "architecture-mermaid-"));
try {
  for (const [i, diagram] of diagrams.entries()) {
    const input = join(scratch, "diagram-" + i + ".mmd");
    const output = join(scratch, "diagram-" + i + ".svg");
    writeFileSync(input, diagram.code, "utf8");
    const args = ["-i", input, "-o", output, "-p", join(root, "scripts", "puppeteer-ci.json")];
    const result = spawnSync(cli, args, { encoding: "utf8", timeout: 120000 });
    if (result.error || result.status !== 0 || !existsSync(output)) {
      throw Error("Mermaid render error: " + diagram.file + " diagram #" + diagram.index + "\n" +
        "Exit code: " + result.status + "\n" + (result.error || "") + "\n" +
        (result.stderr || "") + "\n" + (result.stdout || ""));
    }
    const svg = readFileSync(output, "utf8");
    if (!svg.includes("<svg") || !svg.includes("</svg>")) {
      throw Error(diagram.file + " #" + diagram.index + ": missing valid SVG envelope");
    }
    console.log("PASS " + diagram.file + " Mermaid #" + diagram.index + " -> SVG");
  }
  console.log("PASS: " + diagrams.length + " diagrams rendered by Chromium.");
} finally {
  rmSync(scratch, { recursive: true, force: true });
}
