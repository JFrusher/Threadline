// Regenerates the README graphics: banner PNGs and terminal GIFs.
//   NODE_PATH=$(npm root -g) node docs/assets/make.mjs
// Needs: playwright (chromium), ffmpeg, gifsicle, ssh-keygen, Inter + JetBrains Mono fonts, and `uv sync` done.
// Terminal output in the GIFs is real: every command below is run in a scratch git worktree and captured.
import { execSync, spawnSync } from "node:child_process";
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const { chromium } = createRequire(import.meta.url)("playwright"); // require() honours NODE_PATH
const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "../..");
const work = mkdtempSync(join(tmpdir(), "threadline-assets-"));

const THEMES = {
  light: { bg: "#ffffff", ink: "#0e2238", muted: "#5b6b7c", line: "#c9d3dd", teal: "#128a82", panel: "#f4f7f9" },
  dark: { bg: "#0d1117", ink: "#e6edf3", muted: "#8b98a5", line: "#33404d", teal: "#4fd1c5", panel: "#131b24" },
};

const MARK = (c, size) => `
<svg width="${size}" height="${size}" viewBox="0 0 48 48" fill="none">
  <path d="M8 12C20 12 12 24 24 24S28 36 40 36" stroke="${c.teal}" stroke-width="3.5" stroke-linecap="round"/>
  <circle cx="8" cy="12" r="5" fill="${c.bg}" stroke="${c.ink}" stroke-width="3"/>
  <circle cx="24" cy="24" r="5" fill="${c.bg}" stroke="${c.ink}" stroke-width="3"/>
  <circle cx="40" cy="36" r="5.5" fill="${c.teal}"/>
</svg>`;

// The banner thread uses real items from examples/breathe-triage.
const THREAD = [
  ["UN-003", "user need"],
  ["SYS-003", "system requirement"],
  ["SRS-002", "software requirement"],
  ["RC-001", "risk control"],
  ["test_infant_threshold", "passing test"],
  ["signed release", "technical file"],
];

function bannerHtml(c) {
  const nodes = THREAD.map(([id, kind], i) => {
    const last = i === THREAD.length - 1;
    return `<div class="node"><i class="${last ? "end" : ""}"></i><b>${id}</b><span>${kind}</span></div>`;
  }).join("");
  return `<!doctype html><meta charset="utf-8"><style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 1280px; height: 372px; background: ${c.bg}; color: ${c.ink}; font-family: "Inter", sans-serif;
         padding: 56px 72px 0; -webkit-font-smoothing: antialiased; }
  .brand { display: flex; align-items: center; gap: 18px; }
  h1 { font: 600 60px/1 "Inter Display", "Inter", sans-serif; letter-spacing: -0.03em; }
  p { margin-top: 18px; font-size: 23px; color: ${c.muted}; letter-spacing: -0.005em; }
  .thread { position: relative; margin-top: 62px; display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1.4fr 0.8fr; }
  .thread::before { content: ""; position: absolute; left: 7px; right: calc(100% * 0.8 / 6.2 - 9px); top: 6px;
                    border-top: 2.5px solid ${c.teal}; }
  .node i { position: relative; display: block; width: 15px; height: 15px; border-radius: 50%;
            background: ${c.bg}; border: 2.5px solid ${c.ink}; }
  .node i.end { background: ${c.teal}; border-color: ${c.teal}; }
  .node b { display: block; margin-top: 16px; font: 500 17px/1.2 "JetBrains Mono", monospace; letter-spacing: -0.02em; }
  .node span { display: block; margin-top: 7px; font-size: 15px; color: ${c.muted}; }
  </style>
  <div class="brand">${MARK(c, 62)}<h1>Threadline</h1></div>
  <p>QMS-as-code for Software as a Medical Device. Traceability that fails the build when it breaks.</p>
  <div class="thread">${nodes}</div>`;
}

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

function terminalHtml(title, cwd, rows) {
  const c = THEMES.dark;
  return `<!doctype html><meta charset="utf-8"><style>
  * { margin: 0; box-sizing: border-box; }
  body { width: 920px; height: 540px; background: ${c.bg}; font: 14.5px/1.5 "JetBrains Mono", monospace; color: #c9d4de;
         display: flex; flex-direction: column; border: 1px solid ${c.line}; border-radius: 10px; overflow: hidden; }
  header { padding: 9px 16px; background: ${c.panel}; border-bottom: 1px solid ${c.line}; color: ${c.muted};
           font-size: 12.5px; }
  main { flex: 1; overflow: hidden; display: flex; flex-direction: column; justify-content: flex-end; padding: 14px 18px; }
  pre { font: inherit; white-space: pre-wrap; word-break: break-word; }
  .p { color: ${c.teal}; } .cmd { color: #f0f4f8; } .note { color: ${c.muted}; }
  .cur { display: inline-block; width: 8px; height: 17px; background: #c9d4de; vertical-align: -3px; }
  </style><header>${esc(title)}</header><main>${rows
    .map((r) =>
      r.out !== undefined
        ? `<pre>${esc(r.out)}</pre>`
        : `<pre><span class="p">${esc(cwd)} $</span> <span class="${r.cmd.startsWith("#") ? "note" : "cmd"}">${esc(r.cmd)}</span>${r.cursor ? '<span class="cur"></span>' : ""}</pre>`,
    )
    .join("")}</main>`;
}

async function shot(page, html, file, size) {
  await page.setViewportSize(size);
  await page.setContent(html);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: file });
}

async function gif(browser, name, title, cwd, runIn, commands) {
  const page = await browser.newPage({ deviceScaleFactor: 1.5 });
  const frames = [];
  const rows = [];
  let n = 0;
  const frame = async (seconds) => {
    const file = join(work, `${name}-${String(n++).padStart(4, "0")}.png`);
    await shot(page, terminalHtml(title, cwd, rows), file, { width: 920, height: 540 });
    frames.push(`file '${file}'\nduration ${seconds}`);
  };
  for (const cmd of commands) {
    const row = { cmd: "", cursor: true };
    rows.push(row);
    for (let i = 3; i < cmd.length; i += 3) {
      row.cmd = cmd.slice(0, i);
      await frame(0.05);
    }
    row.cmd = cmd;
    await frame(0.5);
    row.cursor = false;
    if (/^cd \S+$/.test(cmd)) {
      runIn = join(runIn, cmd.slice(3));
      await frame(0.4);
      cwd = cmd.slice(3);
      continue;
    }
    if (!cmd.startsWith("#")) {
      const r = spawnSync("bash", ["-c", cmd], { cwd: runIn, encoding: "utf8", env: { ...process.env, PATH: `${repo}/.venv/bin:${process.env.PATH}` } });
      const out = (r.stdout + r.stderr).trimEnd();
      if (out) rows.push({ out });
    }
    await frame(out_pause(cmd));
  }
  await frame(3);
  await page.close();
  const list = join(work, `${name}.txt`);
  writeFileSync(list, frames.join("\n") + "\n" + frames.at(-1).split("\n")[0] + "\n");
  const raw = join(work, `${name}.gif`);
  execSync(`ffmpeg -y -loglevel error -f concat -safe 0 -i ${list} -vf "split[a][b];[a]palettegen=max_colors=48[p];[b][p]paletteuse=dither=none" -fps_mode vfr ${raw}`);
  execSync(`gifsicle -O3 ${raw} -o ${join(here, `${name}.gif`)}`);
}

const out_pause = (cmd) => (cmd.startsWith("#") ? 0.9 : cmd.startsWith("threadline") ? 3.2 : 1.2);

const browser = await chromium.launch();

const page = await browser.newPage({ deviceScaleFactor: 2 });
for (const [name, c] of Object.entries(THEMES)) {
  await shot(page, bannerHtml(c), join(here, `banner-${name}.png`), { width: 1280, height: 372 });
}
await page.close();

// check.gif: the worked example, with one test's link removed and then restored.
const wt = join(work, "wt");
execSync(`git -C ${repo} worktree add -q --detach ${wt} HEAD`);
const example = join(wt, "examples/breathe-triage");
await gif(browser, "check", "breathe-triage: threadline check", "breathe-triage", example, [
  "# a refactor drops the marker that links a test to SRS-004 and RC-004",
  `sed -i '/verifies("SRS-004", "RC-004")/d' tests/test_triage.py`,
  "pytest -q --junitxml=junit.xml | tail -n 1",
  "threadline check --junit junit.xml | grep -v -e ^NOTE -e ^skipped",
  "# tests still pass, but the danger-sign control has no evidence. put it back:",
  "git checkout tests/test_triage.py",
  "pytest -q --junitxml=junit.xml | tail -n 1",
  "threadline check --junit junit.xml | grep -v -e ^NOTE -e ^skipped",
]);
execSync(`git -C ${repo} worktree remove --force ${wt}`);

// init.gif: a fresh scaffold is red until the design file exists.
const scratch = join(work, "scratch");
mkdirSync(scratch);
await gif(browser, "init", "threadline init", "~", scratch, [
  "threadline init my-qms",
  "cd my-qms",
  "git init -q && ls -Am",
  "pytest -q --junitxml=junit.xml | tail -n 1",
  "threadline check --junit junit.xml | grep ^TL- | cut -d' ' -f1 | sort | uniq -c",
  "threadline check --junit junit.xml | grep ^TL-C01 | head -n 4",
]);

await browser.close();
rmSync(work, { recursive: true });
