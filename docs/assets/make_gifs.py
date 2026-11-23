"""Render the README's terminal GIFs from captured command output in docs/assets/tapes/.

The GIFs replay real output; nothing is typed by hand. To refresh them after the CLI's output changes,
recapture each tape from the repository root, then run `python docs/assets/make_gifs.py` (needs Pillow
and the DejaVu Sans Mono fonts).

demo-catch-a-bug.gif, run in examples/breathe-triage with ROOT=87785d9a6e5fd9fa56d7f36ca3256c91d349238a:
  a1  sed -i 's/respiratory_rate >= threshold/respiratory_rate > threshold/' src/breathe_triage/triage.py
      git diff -U0 --no-color src/breathe_triage/triage.py
  a2  pytest -q --tb=no -p no:cacheprovider --junitxml=junit.xml
  a3  threadline check --junit junit.xml --trust-root $ROOT
  a4  git checkout src/breathe_triage/triage.py && pytest -q --tb=no -p no:cacheprovider --junitxml=junit.xml
  a5  threadline check --junit junit.xml --trust-root $ROOT

demo-init.gif, run in an empty directory:
  b1  threadline init my-qms
      cd my-qms && git init -q && git add -A && git commit -qm 'Start the QMS'
  b3  pytest -q -p no:cacheprovider --junitxml=junit.xml
  b4  threadline check --junit junit.xml
"""

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

COLS, ROWS, FS, LH, PAD, BAR = 118, 26, 15, 21, 18, 34
FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", FS)
BOLD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", FS)
CW = FONT.getbbox("M")[2]
W, H = PAD * 2 + CW * COLS, BAR + PAD * 2 + LH * ROWS
BG, FG, DIM, RED, GREEN, YELLOW, BLUE, CYAN = (
    "#0d1117", "#e6edf3", "#7d8590", "#ff7b72", "#3fb950", "#d29922", "#79c0ff", "#a5d6ff")


def spans(line: str):
    """[(text, colour, bold)] for one logical line."""
    if line.startswith("$ "):
        return [("$ ", GREEN, True), (line[2:], FG, True)]
    if line.startswith("# "):
        return [(line, DIM, False)]
    if m := re.match(r"(TL-\w+)( \[[^\]]*\])(.*)", line):
        return [(m[1], RED, True), (m[2], DIM, False), (m[3], FG, False)]
    if line.startswith(("skipped", "NOTE", "DRAFT")):
        return [(line, DIM, False)]
    if line.startswith("FAILED") or re.search(r"\d+ failed", line):
        return [(line, RED, False)]
    if re.match(r"0 finding", line) or re.match(r"\d+ passed", line):
        return [(line, GREEN, True)]
    if re.match(r"\d+ finding", line):
        return [(line, RED, True)]
    if line.startswith("by rule:"):
        return [(line, YELLOW, False)]
    if line.startswith("+") and not line.startswith("+++"):
        return [(line, GREEN, False)]
    if line.startswith("-") and not line.startswith("---"):
        return [(line, RED, False)]
    if line.startswith(("@@", "diff", "index", "---", "+++")):
        return [(line, CYAN, False)]
    if line.startswith(("created", "wrote")):
        return [(line, BLUE, False)]
    return [(line, FG, False)]


def wrap(line_spans):
    """Split coloured spans into screen rows of COLS characters."""
    rows, cur, n = [], [], 0
    for text, col, b in line_spans:
        while text:
            take = text[: COLS - n]
            cur.append((take, col, b))
            n += len(take)
            text = text[len(take):]
            if n == COLS:
                rows.append(cur)
                cur, n = [], 0
    if cur or not rows:
        rows.append(cur)
    return rows


def draw(screen, title, cursor):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, BAR], fill="#161b22")
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        d.ellipse([PAD + i * 20, 11, PAD + i * 20 + 12, 23], fill=c)
    d.text((W // 2, BAR // 2), title, font=FONT, fill=DIM, anchor="mm")
    visible = screen[-ROWS:]
    for r, row in enumerate(visible):
        x, y = PAD, BAR + PAD + r * LH
        for text, col, b in row:
            d.text((x, y), text, font=BOLD if b else FONT, fill=col)
            x += CW * len(text)
        if cursor and r == len(visible) - 1:
            d.rectangle([x, y + 2, x + CW - 1, y + LH - 3], fill=FG)
    return im


def render(steps, title, out):
    screen, frames, durations = [], [], []

    def snap(ms, cursor=True):
        frames.append(draw(screen, title, cursor))
        durations.append(ms)

    for kind, val in steps:
        if kind in ("cmd", "comment"):
            prefix = "$ " if kind == "cmd" else "# "
            screen.append([])
            for i in range(0, len(val) + 1, 3):
                screen[-1:] = wrap(spans(prefix + val[:i]))
                snap(40)
            screen[-1:] = wrap(spans(prefix + val))
            snap(450)
        elif kind == "out":
            lines = Path(val).read_text().rstrip("\n").split("\n")
            batch = max(1, len(lines) // 12)
            for i, line in enumerate(lines):
                screen.extend(wrap(spans(line)))
                if i % batch == batch - 1:
                    snap(60, cursor=False)
            snap(60)
        elif kind == "pause":
            durations[-1] += val
        elif kind == "clear":
            screen.clear()
    screen.append([])
    snap(3000)
    sample = frames[:: max(1, len(frames) // 8)] + [frames[-1]]
    strip = Image.new("RGB", (W, H * len(sample)))
    for i, f in enumerate(sample):
        strip.paste(f, (0, H * i))
    pal = strip.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    q[0].save(out, save_all=True, append_images=q[1:], duration=durations, loop=0, optimize=True, disposal=1)


if __name__ == "__main__":
    HERE = Path(__file__).parent
    T = HERE / "tapes"
    render([
        ("comment", "Breathe-Triage example. An off-by-one slips into the fast-breathing threshold:"),
        ("cmd", "git diff -U0"), ("out", T / "a1.txt"), ("pause", 1500),
        ("cmd", "pytest -q --tb=no --junitxml=junit.xml"), ("out", T / "a2.txt"), ("pause", 1200),
        ("cmd", "threadline check --junit junit.xml --trust-root $ROOT"), ("out", T / "a3.txt"), ("pause", 4500),
        ("clear", None),
        ("comment", "Threadline names the requirements and the risk control that lost their evidence. Fix it:"),
        ("cmd", "git checkout src/breathe_triage/triage.py"),
        ("cmd", "pytest -q --tb=no --junitxml=junit.xml"), ("out", T / "a4.txt"), ("pause", 800),
        ("cmd", "threadline check --junit junit.xml --trust-root $ROOT"), ("out", T / "a5.txt"),
    ], "examples/breathe-triage", HERE / "demo-catch-a-bug.gif")
    render([
        ("cmd", "threadline init my-qms"), ("out", T / "b1.txt"), ("pause", 800),
        ("cmd", "cd my-qms && git init -q && git add -A && git commit -qm 'Start the QMS'"), ("pause", 600),
        ("cmd", "pytest -q --junitxml=junit.xml"), ("out", T / "b3.txt"), ("pause", 800),
        ("cmd", "threadline check --junit junit.xml"), ("out", T / "b4.txt"), ("pause", 2500),
        ("comment", "Red on day one, on purpose: every finding names its clause. "
                    "Fill in the design file until it is green."),
    ], "~/my-qms", HERE / "demo-init.gif")
