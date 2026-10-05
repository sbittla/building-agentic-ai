// Build the course Word document from md/*.md (a small markdown dialect) + code/*.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow,
  TableCell, WidthType, ShadingType, BorderStyle, LevelFormat, TableOfContents, Footer,
  Header, PageNumber, PageBreak, TabStopType, ImageRun, Bookmark, InternalHyperlink, ExternalHyperlink,
  SectionType, NumberFormat, CharacterSet, SimpleField,
} = require("docx");
const crypto = require("crypto");
const { execFileSync } = require("child_process");

const ROOT = __dirname;
const FONT = "Cambria";                         // body (metric twin in LibreOffice: Caladea)
const HFONT = "Calibri";                        // headings (metric twin: Carlito)
const MONO = "DejaVu Sans Mono";                // code; embedded in the .docx
const ACCENT = "000000";                               // black-and-white print: no colour in the interior
// 7" x 10" trade technical book, mirrored margins: inside 0.875", outside 0.625"
const PAGE_W = 10080, PAGE_H = 14400, M_IN = 1260, M_OUT = 900, M_TOP = 1080, M_BOT = 1008;
const MARGIN = M_IN;
const CONTENT_W = PAGE_W - M_IN - M_OUT;         // 7920 DXA = 5.5"
const BOOK = "Building Agentic AI Systems";
// "Table: Title {#t:label}" before a table; "Figure: Caption {#f:label}" and "Alt: ..." after a diagram
const CAPTION_RE = /^(Table|Figure): (.+)$/;
const LABEL_RE = /^(.*?)(?:\s*\{#([tf]:[\w-]+)\})?\s*$/;
const CAPTION_WARNINGS = [];

const LEVEL_COLORS = { Concept: "262626", Simple: "262626", Medium: "262626", Complex: "262626" };   // the level is spelled out on the badge
const LEVEL_FILL = { Concept: "F2F2F2", Simple: "F2F2F2", Medium: "F2F2F2", Complex: "F2F2F2" };

// ---------- inline markdown: **bold**, *italic*, `code` ----------
function inline(text, base = {}) {
  const runs = [];
  // bold may contain `code` (even code with asterisks, like `fn(**args)`)
  const re = /(\[[^\]]+\]\([^)\s]+\)|\*\*(?:`[^`]*`|[^*`])+\*\*|`[^`]+`|\*[^*\s][^*]*\*)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) runs.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    const tok = m[0];
    if (tok.startsWith("[")) {
      const lm = tok.match(/^\[([^\]]+)\]\(([^)\s]+)\)$/);
      runs.push(new ExternalHyperlink({ link: lm[2], children: [new TextRun({ text: lm[1], ...base, color: "000000", underline: {} })] }));
    }
    else if (tok.startsWith("**")) runs.push(...inline(tok.slice(2, -2), { ...base, bold: true }));
    else if (tok.startsWith("`")) runs.push(new TextRun({ text: tok.slice(1, -1), ...base, font: MONO, size: (base.size || 20) - 3, color: "000000" }));
    else runs.push(new TextRun({ text: tok.slice(1, -1), ...base, italics: true }));
    last = m.index + tok.length;
  }
  if (last < text.length) runs.push(new TextRun({ text: text.slice(last), ...base }));
  return runs;
}

// ---------- block builders ----------
const para = (text, opts = {}) => new Paragraph({ children: inline(text, opts.run || {}), spacing: { after: 110, line: 264 }, ...opts.p });

// ---------- captions: "Table 4.2 Title", "Figure 4.1 Caption", "Listing 4.3 file.py" ----------
// The number is a Word SEQ field (reset at each chapter's first item), with the number the build
// computed as its cached result, so the printed book is right and Word can still update it.
// A caption is bookmarked and recorded in HEADINGS (cap: kind) for the List of Figures and Tables.
function captionRuns(kind, num) {
  if (!num) return [];
  const [prefix, k] = [num.slice(0, num.lastIndexOf(".")), num.slice(num.lastIndexOf(".") + 1)];
  return [new TextRun({ text: `${kind} ${prefix}.`, bold: true }),
          new SimpleField(`SEQ ${kind} ${k === "1" ? "\\r 1 " : ""}\\* ARABIC`, k),
          new TextRun({ text: "  ", bold: true })];
}
function captionPara(kind, num, title, opts = {}) {
  const plainTitle = title.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*`]/g, "");
  const runs = [...captionRuns(kind, num), ...(opts.titleRuns || inline(title, { bold: !num ? true : false }))];
  let children = runs;
  if (num) {
    const id = `cap_${HEADINGS.length}`;
    HEADINGS.push({ id, level: 9, cap: kind, text: `${kind} ${num}  ${plainTitle}`, find: `${kind} ${num} ${plainTitle}`, noToc: false });
    children = [new Bookmark({ id, children: runs })];
  }
  return new Paragraph({ style: "Caption", keepNext: !!opts.keepNext, keepLines: true,
                         spacing: opts.spacing, children });
}

function codeBlock(lines, caption, num) {
  const out = [];
  if (caption) out.push(captionPara("Listing", num, caption, { keepNext: true, spacing: { before: 160, after: 40 },
    titleRuns: [new TextRun({ text: num ? "" : "Listing  ", bold: true }), new TextRun({ text: caption, font: MONO, size: 17, bold: false })] }));
  const border = { style: BorderStyle.SINGLE, size: 12, color: "A6A6A6", space: 6 };
  lines.forEach((line, i) => {
    out.push(new Paragraph({
      spacing: { before: i === 0 && !caption ? 120 : 0, after: i === lines.length - 1 ? 160 : 0, line: 240 },
      shading: { type: ShadingType.CLEAR, color: "auto", fill: "F2F2F2" },
      border: { left: border },
      indent: { left: 120 },
      children: [new TextRun({ text: line.length ? line : " ", font: MONO, size: 14, color: "000000" })],
    }));
  });
  return out;
}

function boxParas(lines, fill, color, header) {
  const border = { style: BorderStyle.SINGLE, size: 24, color, space: 8 };
  const base = { shading: { type: ShadingType.CLEAR, color: "auto", fill }, border: { left: border }, indent: { left: 200, right: 120 } };
  const out = [];
  if (header) out.push(new Paragraph({ ...base, keepNext: true, spacing: { before: 200, after: 60 }, children: header }));
  lines.forEach((l, i) => {
    const last = i === lines.length - 1;
    let children;
    const hm = l.match(/^\*\*(Hint|Done when|Run):\*\*\s*(.*)$/);
    if (hm) children = [new TextRun({ text: hm[1] + ": ", bold: true, color }), ...inline(hm[2])];
    else children = inline(l);
    out.push(new Paragraph({ ...base, keepNext: !last, spacing: { before: 0, after: last ? 200 : 80, line: 264 }, children }));
  });
  return out;
}

function table(rows) {
  const ncol = rows[0].length;
  // column widths proportional to content length (clamped), summing to CONTENT_W
  const shown = t => (t || "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").split("<br>").reduce((a, x) => Math.max(a, x.length), 0);
  const plain = t => (t || "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[*`]/g, "");
  const longestWord = t => plain(t).split(/<br>|\s+/).reduce((a, w) => Math.max(a, w.length), 0);
  const lens = Array.from({ length: ncol }, (_, c) =>
    Math.max(Math.min(60, Math.max(rows[0][c].trim() === "Level" ? 15 : 10, ...rows.map(r => shown(r[c])))),
             Math.min(30, 2 + Math.max(longestWord(rows[0][c]) * 1.45,   // bold header words
                                        ...rows.slice(1).map(r => longestWord(r[c]) * 1.2)))));
  const total = lens.reduce((a, b) => a + b, 0);
  const widths = lens.map(l => Math.floor(CONTENT_W * l / total));
  widths[ncol - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const cellBorder = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
  const borders = { top: cellBorder, bottom: cellBorder, left: cellBorder, right: cellBorder };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0,
      cantSplit: true,
      children: r.map((cell, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA },
        borders,
        shading: ri === 0 ? { type: ShadingType.CLEAR, color: "auto", fill: "D9D9D9" } : undefined,
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: cell.trim().split("<br>").map((part, pi) => new Paragraph({ spacing: { after: 0, line: 252 },
          children: inline(part.trim(), ri === 0 ? { bold: true, size: 17, color: "000000", font: HFONT }
                                                 : { size: pi && cell.trim().startsWith("**") ? 14 : 17 }) })),
      })),
    })),
  });
}


// ---------- mermaid diagrams -> PNG (cached by content hash) ----------
const DIAGRAMS = path.join(ROOT, "diagrams");
// which model each exercise needs (also read by the kit: ./course.sh list, ./course.sh ex)
const MODEL_NEEDS = JSON.parse(fs.readFileSync(path.join(ROOT, "model_needs.json"), "utf8"));
const KIT = path.dirname(path.dirname(fs.realpathSync(path.join(ROOT, "code"))));   // kit/course/code -> kit
const SOLUTIONS = JSON.parse(fs.readFileSync(path.join(KIT, "solutions", "index.json"), "utf8"));
function solutionFile(id) {           // the one file worth naming in the box
  const files = (SOLUTIONS[id] || []).filter(f => !/^tests\/test_ch\d/.test(f));
  const code = files.find(f => /\.(py|sh|jsonl?)$/.test(f));
  return code ? path.basename(code) : "ANSWERS.md";
}
const MODEL_LABEL = { none: "none (free)", any: "qwen3.5:9b or Claude", "claude-rec": "Claude recommended (runs on qwen3.5:9b)",
                      claude: "Claude only", desktop: "Claude only" };
const DIAGRAM_REPORT = [];
function renderMermaid(src, alt) {
  fs.mkdirSync(DIAGRAMS, { recursive: true });
  // grayscale theme for black-and-white print; the config is part of the cache key
  const cfg = path.join(DIAGRAMS, "mermaid.json");
  const hash = crypto.createHash("sha1").update(src + fs.readFileSync(cfg, "utf8")).digest("hex").slice(0, 12);
  const png = path.join(DIAGRAMS, `d-${hash}.png`);
  if (!fs.existsSync(png)) {
    const mmd = path.join(DIAGRAMS, `d-${hash}.mmd`);
    fs.writeFileSync(mmd, src);
    // MERMAID_PUPPETEER points at a machine-specific browser config, if this machine needs one
    execFileSync("mmdc", ["-p", process.env.MERMAID_PUPPETEER || path.join(DIAGRAMS, "puppeteer.json"), "-c", cfg, "-i", mmd, "-o", png,
                          "-b", "white", "-s", "3"], { stdio: "ignore" });
  }
  return imagePara(png, hash, alt);
}
// a diagram kept as a PNG in diagrams/ (its Mermaid source isn't in the manuscript): "@@image d-<hash>.png"
function imagePara(png, hash, alt) {
  const buf = fs.readFileSync(png);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  // docx-js sizes are CSS pixels (96 per inch); the text block is 5.5" wide
  const maxW = 528, maxH = 640;
  const scale = Math.min(maxW / (w / 3), maxH / (h / 3), 0.85);   // 0.85 ≈ 10 pt text, like the body
  const width = Math.round((w / 3) * scale), height = Math.round((h / 3) * scale);
  const fontPt = 12 * scale;                           // 16px diagram text at this scale, in points
  DIAGRAM_REPORT.push({ hash, width, height, fontPt: +fontPt.toFixed(1) });
  if (fontPt < 8.5) console.error(`SMALL DIAGRAM TEXT d-${hash}: ${fontPt.toFixed(1)} pt`);
  const a = alt || {};
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 160, after: a.caption ? 60 : 200 }, keepNext: !!a.caption,
    children: [new ImageRun({ type: "png", data: buf, transformation: { width, height },
                              altText: { title: a.caption || "Diagram", description: a.alt || a.caption || "Diagram", name: `d-${hash}` } })] });
}

// ---------- markdown file -> blocks ----------
let numInstance = 0;
const NUMBER_STARTS = new Set();          // ordered lists that start above 1
// ---------- static table of contents (page numbers from a first render; see make_toc.py) ----------
const HEADINGS = [];
const CURRENT = { title: "", short: "" };
const SKIP_TOC = /^(Learn more|Learning objectives|Real-world connection|Common mistakes|Summary|Exercises|Solutions for this chapter|Checkpoint)/;
const TOC_PAGES_FILE = path.join(__dirname, "toc_pages.json");
const TOC_PAGES = fs.existsSync(TOC_PAGES_FILE) ? JSON.parse(fs.readFileSync(TOC_PAGES_FILE, "utf8")) : {};
function tocEntries() {
  const style = {
    0: { size: 21, bold: true, color: ACCENT, before: 200, after: 40, indent: 0, font: HFONT },
    1: { size: 19, bold: true, color: "262626", before: 70, after: 10, indent: 0 },
    2: { size: 17, bold: false, color: "404040", before: 0, after: 0, indent: 300 },
  };
  return HEADINGS.filter(h => !h.noToc && !h.cap).map(({ id, level, text }) => {
    const st = style[level];
    return new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W, leader: level === 0 ? "none" : "dot" }],
      indent: { left: st.indent },
      spacing: { before: st.before, after: st.after, line: 240 },
      keepNext: level < 2,
      children: [new InternalHyperlink({ anchor: id, children: [
        new TextRun({ text, bold: st.bold, size: st.size, color: st.color, font: st.font }),
        new TextRun({ text: `\t${TOC_PAGES[id] ?? "000"}`, bold: st.bold, size: st.size, font: st.font }),
      ] })],
    });
  });
}

// ---------- chapter and part openers ----------
function chapterOpener(text) {
  let label = null, title = text, m;
  if ((m = text.match(/^Chapter (\d+): (.+)$/))) { label = `CHAPTER ${m[1]}`; title = m[2]; }
  else if ((m = text.match(/^Interlude: (.+)$/))) { label = "INTERLUDE"; title = m[1]; }
  const id = `toc_${HEADINGS.length}`;
  HEADINGS.push({ id, level: 1, text, find: title, noToc: title === "Contents" });
  CURRENT.title = text; CURRENT.short = label ? `${label.charAt(0) + label.slice(1).toLowerCase()} \u00b7 ${title}`.replace("Interlude \u00b7", "Interlude:") : title;
  if (label && label.startsWith("CHAPTER")) CURRENT.short = `Chapter ${m[1]}: ${title}`;
  const out = [new Paragraph({ spacing: { before: label ? 1100 : 900, after: 60 },
    children: label ? [new TextRun({ text: label, font: HFONT, size: 22, bold: true, color: "595959", characterSpacing: 40 })] : [] })];
  out.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new Bookmark({ id, children: [new TextRun(title)] })] }));
  return out;
}

function partOpener(part) {
  const id = `toc_${HEADINGS.length}`;
  const text = `Part ${part.num}: ${part.title}`;
  HEADINGS.push({ id, level: 0, text, find: part.title });
  return [
    new Paragraph({ spacing: { before: 3000, after: 120 }, alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: `PART ${part.num}`, font: HFONT, size: 30, bold: true, color: "595959", characterSpacing: 60 })] }),
    new Paragraph({ alignment: AlignmentType.RIGHT, spacing: { after: 360 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 8 } },
      children: [new Bookmark({ id, children: [new TextRun({ text: part.title, font: HFONT, size: 52, bold: true, color: ACCENT })] })] }),
    new Paragraph({ spacing: { after: part.stages ? 120 : 240, line: 300 }, children: [new TextRun({ text: part.blurb, italics: true, size: 21, color: "404040" })] }),
    // which stages of the agent lifecycle (section 1.10) this part builds
    ...(part.stages ? [new Paragraph({ spacing: { after: 240 }, children: [
      new TextRun({ text: "Lifecycle stages: ", bold: true, size: 19, color: "404040" }),
      new TextRun({ text: `${part.stages} (section 1.10)`, size: 19, color: "404040" })] })] : []),
    ...part.contents.map(c => new Paragraph({ spacing: { after: 60 }, indent: { left: 360 },
      children: [new TextRun({ text: c, size: 20, color: "404040" })] })),
  ];
}

// what follows an image or Mermaid block: "Figure: caption {#f:label}" and "Alt: description"
function figureLines(lines, i) {
  const r = { next: i };
  let j = i;
  while (j < lines.length && !lines[j].trim()) j++;
  let m = (lines[j] || "").match(CAPTION_RE);
  if (m && m[1] === "Figure") { r.caption = m[2]; j++; r.next = j; while (j < lines.length && !lines[j].trim()) j++; }
  m = (lines[j] || "").match(/^Alt: (.+)$/);
  if (m) { r.alt = m[1].trim(); r.next = j + 1; }
  return r;
}
function convert(md, file) {
  const out = [];
  const lines = md.split("\n");
  const plan = PLAN[file] || { prefix: null };
  const seen = { Table: 0, Figure: 0, Listing: 0 };
  const nextNum = kind => { seen[kind]++; return plan.prefix ? `${plan.prefix}.${seen[kind]}` : null; };
  let pendingTable = null, inLearnMore = false;
  let i = 0, paraBuf = [];
  const flush = () => { if (paraBuf.length) { out.push(para(paraBuf.join(" "))); paraBuf = []; } };
  while (i < lines.length) {
    const line = lines[i];
    if (!line.trim()) { flush(); i++; continue; }
    let m;
    if ((m = line.match(/^(#{1,3}) (.*)$/))) {
      flush();
      const level = m[1].length;
      if (level <= 2) inLearnMore = m[2].trim() === "Learn more";
      const h = [HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3][level - 1];
      let text = m[2].trim();
      const api = / \{api\}$/.test(text);            // "## 4.8 Thinking {api}": fast-changing section
      text = text.replace(/ \{api\}$/, "");
      if (level === 1) {
        out.push(...chapterOpener(text));
      } else if (level === 2 && !SKIP_TOC.test(text)) {
        const id = `toc_${HEADINGS.length}`;
        HEADINGS.push({ id, level, text, find: text });
        out.push(new Paragraph({ heading: h, children: [new Bookmark({ id, children: [new TextRun(text)] })] }));
      } else {
        out.push(new Paragraph({ heading: h, children: [new TextRun(text)] }));
      }
      if (api) out.push(new Paragraph({ spacing: { before: 0, after: 120 }, keepNext: true, children: [
        new TextRun({ text: "API-dependent. ", bold: true, size: 17, color: "595959" }),
        new TextRun({ text: "The concept is durable; the names, parameters and prices here change often. "
                          + "Check the current documentation.", italics: true, size: 17, color: "595959" })] }));
      i++; continue;
    }
    if ((m = line.match(/^@@code (.+)$/))) {
      flush();
      // "@@code file.py" shows the whole file; "@@code file.py::a,b" shows only those functions,
      // classes (or Class.method) and assignments: the full file is in the course kit.
      const [file, names] = m[1].trim().split("::");
      let src, caption;

      // Handle chapter-based and interlude file structures
      let codePath = path.join(ROOT, "code", file);
      if (!fs.existsSync(codePath)) {
        // Try chapter-based path: ch00_python_tour.py → ch00/ch00_python_tour.py
        let match = file.match(/^(ch\d+)_/);
        if (match) {
          const chapter = match[1];
          const chapterPath = path.join(ROOT, "code", chapter, file);
          if (fs.existsSync(chapterPath)) {
            codePath = chapterPath;
          }
        }
        // Try interlude paths: i_*.py, test_i_*.py → interlude_*/
        if (!fs.existsSync(codePath)) {
          match = file.match(/^(test_)?i_/);
          if (match) {
            const interludes = ["python", "regex", "sql", "testing", "measure"];
            for (const iname of interludes) {
              const interloudePath = path.join(ROOT, "code", `interlude_${iname}`, file);
              if (fs.existsSync(interloudePath)) {
                codePath = interloudePath;
                break;
              }
            }
          }
        }
        // Try capstone files: c*.py → capstones/c*/
        if (!fs.existsSync(codePath)) {
          match = file.match(/^(test_)?c\d_/);
          if (match) {
            const capDir = file.match(/^(test_)?c(\d)/)[2];
            const capstonePath = path.join(ROOT, "code", `capstone_C${capDir}`, file);
            if (fs.existsSync(capstonePath)) {
              codePath = capstonePath;
            }
          }
        }
      }

      if (names) {
        src = execFileSync("python3", [path.join(ROOT, "excerpt.py"), codePath, names],
                           { encoding: "utf8" }).replace(/\s+$/, "");
        caption = `${file} (excerpt; full file in the course kit)`;
      } else {
        src = fs.readFileSync(codePath, "utf8").replace(/\s+$/, "");
        caption = file;
      }
      out.push(...codeBlock(src.split("\n"), caption, nextNum("Listing")));
      i++; continue;
    }
    if ((m = line.match(/^@@image (\S+)$/))) {
      flush();
      const fig = figureLines(lines, i + 1);
      out.push(...figure(imagePara(path.join(DIAGRAMS, m[1]), m[1].replace(/\.png$/, "").replace(/^d-/, ""), fig), fig, m[1]));
      i = fig.next; continue;
    }
    if ((m = line.match(CAPTION_RE)) && m[1] === "Table") {
      flush();
      pendingTable = m[2];
      i++; continue;
    }
    if (line.startsWith("```mermaid")) {
      flush();
      const buf = []; i++;
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
      i++;
      const fig = figureLines(lines, i);
      out.push(...figure(renderMermaid(buf.join("\n"), fig), fig, "a Mermaid diagram"));
      i = fig.next;
      continue;
    }
    if (line.startsWith("```")) {
      flush();
      const buf = []; i++;
      while (i < lines.length && !lines[i].startsWith("```")) buf.push(lines[i++]);
      i++;
      out.push(...codeBlock(buf));
      continue;
    }
    if ((m = line.match(/^:::note (.*)$/))) {              // a titled box without "Tip:"
      flush();
      const buf = []; i++;
      while (i < lines.length && lines[i].trim() !== ":::") { if (lines[i].trim()) buf.push(lines[i]); i++; }
      i++;
      out.push(...boxParas(buf, "F2F2F2", "404040", [new TextRun({ text: m[1], bold: true, color: "404040" })]));
      continue;
    }
    if ((m = line.match(/^:::(tip|warn) (.*)$/))) {
      flush();
      const buf = []; i++;
      while (i < lines.length && lines[i].trim() !== ":::") { if (lines[i].trim()) buf.push(lines[i]); i++; }
      i++;
      const warn = m[1] === "warn";
      const color = warn ? "000000" : "404040";
      out.push(...boxParas(buf, warn ? "E6E6E6" : "F2F2F2", color,
        [new TextRun({ text: (warn ? "Caution: " : "Tip: ") + m[2], bold: true, color })]));
      continue;
    }
    if ((m = line.match(/^:::ex (\w+) \| ([\w.]+) \| (.*)$/))) {
      flush();
      const [lvl, id, title] = [m[1], m[2], m[3]];
      const buf = []; i++;
      while (i < lines.length && lines[i].trim() !== ":::") { if (lines[i].trim()) buf.push(lines[i]); i++; }
      i++;
      const color = LEVEL_COLORS[lvl];
      const need = MODEL_NEEDS[id];
      if (!need) throw new Error(`exercise ${id} is missing from model_needs.json`);
      buf.push(`**Model:** ${MODEL_LABEL[need.model]}${need.note ? `. ${need.note}` : ""}`);
      buf.push(`**Run:** \`./course.sh ex ${id}\`     **Solution:** \`./course.sh solution ${id}\` (\`${solutionFile(id)}\`)`);
      out.push(...boxParas(buf, LEVEL_FILL[lvl], color, [
        new TextRun({ text: `Exercise ${id}`, bold: true, color }),
        new TextRun({ text: `   ${lvl.toUpperCase()}   `, bold: true, color: "FFFFFF", shading: { type: ShadingType.CLEAR, color: "auto", fill: color }, size: 16 }),
        new TextRun({ text: `   ${title}`, bold: true }),
      ]));
      continue;
    }
    if (line.startsWith("|")) {
      flush();
      const rows = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        const cells = lines[i].trim().replace(/^\||\|$/g, "").replace(/\\\|/g, "\u0000")
          .split("|").map(c => c.replace(/\u0000/g, "|"));     // "\|" is a literal pipe
        if (!cells.every(c => /^\s*:?-+:?\s*$/.test(c))) rows.push(cells);
        i++;
      }
      if (pendingTable) {
        const t = pendingTable.match(LABEL_RE);
        out.push(captionPara("Table", nextNum("Table"), t[1], { keepNext: true, spacing: { before: 200, after: 80 } }));
      } else if (!inLearnMore && plan.prefix) CAPTION_WARNINGS.push(`${file}: table without a title ("${rows[0].join(" | ").slice(0, 60)}")`);
      pendingTable = null;
      out.push(table(rows));
      out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
      continue;
    }
    if ((m = line.match(/^(\s*)(- \[ \] |- |\d+\. )(.*)$/))) {
      flush();
      const ordered = /\d+\./.test(m[2]);
      if (ordered) numInstance++;
      const inst = numInstance;
      // a numbered list keeps the number it starts with ("4. Build ..." after a code block)
      const first = ordered ? parseInt(m[2], 10) : 1;
      const numRef = first > 1 ? `numbers_from_${first}` : "numbers";
      if (first > 1) NUMBER_STARTS.add(first);
      const LIST_RE = /^(\s*)(- \[ \] |- |\d+\. )(.*)$/;
      // items separated by blank lines are still one list, so "1. ... 2. ... 3." never restarts at 1
      const nextItem = () => { let j = i; while (j < lines.length && !lines[j].trim()) j++; return j; };
      while (i < lines.length && ((m = lines[i].match(LIST_RE)) ||
             (!lines[i].trim() && ordered && LIST_RE.test(lines[nextItem()] || "") && /^\s*\d+\. /.test(lines[nextItem()])))) {
        if (!m) { i = nextItem(); continue; }
        const lvl = m[1].length >= 4 ? 1 : 0;
        const isNum = /\d+\./.test(m[2]);
        const check = m[2].startsWith("- [ ]");
        const children = check ? [new TextRun({ text: "☐  " }), ...inline(m[3])] : inline(m[3]);
        out.push(new Paragraph({
          numbering: check ? undefined : (isNum ? { reference: numRef, level: lvl, instance: inst } : { reference: "bullets", level: lvl }),
          indent: check ? { left: 360 } : undefined,
          spacing: { after: 60, line: 264 }, children,
        }));
        i++;
      }
      out.push(new Paragraph({ spacing: { after: 60 }, children: [] }));
      continue;
    }
    paraBuf.push(line.trim());
    i++;
  }
  flush();
  if (pendingTable) throw new Error(`${file}: "Table: ${pendingTable}" isn't followed by a table`);
  for (const k of ["Table", "Figure", "Listing"])
    if (plan.prefix && seen[k] !== plan[k]) throw new Error(`${file}: ${seen[k]} ${k}s rendered, ${plan[k]} planned`);
  return out;

  function figure(img, fig, what) {
    if (!fig.caption) { if (plan.prefix) CAPTION_WARNINGS.push(`${file}: ${what} without a caption`); return [img]; }
    if (!fig.alt) CAPTION_WARNINGS.push(`${file}: figure "${fig.caption.slice(0, 40)}" has no Alt: text`);
    const t = fig.caption.match(LABEL_RE);
    return [img, captionPara("Figure", nextNum("Figure"), t[1], { spacing: { before: 0, after: 220 } })];
  }
}

// ---------- front-matter pages ----------
const small = (text, run = {}, after = 100, align) => new Paragraph({ alignment: align, spacing: { after, line: 252 },
  children: [new TextRun({ text, size: 16, color: "404040", ...run })] });
const center = (text, run, after = 200) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after },
  children: [new TextRun({ text, ...run })] });

function halfTitle() {
  return [new Paragraph({ spacing: { before: 3600 }, children: [] }),
          center("Building Agentic AI Systems", { size: 44, bold: true, color: ACCENT, font: HFONT }, 0)];
}
function alsoBy() {
  const books = [
    ["AI Performance Engineering: From GPU Kernels to LLM Inference", "2026"],
    ["The Last Invention: How Artificial Superintelligence Will Redefine Life", "revised edition, 2026"],
    ["AI-Driven Software Testing: Transforming Software Testing with AI and Machine Learning", "Apress, 2025"],
  ];
  return [new Paragraph({ spacing: { before: 2400, after: 240 }, alignment: AlignmentType.CENTER,
            children: [new TextRun({ text: "ALSO BY SRINIVASA RAO BITTLA", font: HFONT, size: 18, bold: true, color: "595959", characterSpacing: 30 })] }),
          ...books.map(([t, d]) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 },
            children: [new TextRun({ text: t, italics: true, size: 19, color: "404040" }),
                       new TextRun({ text: `  (${d})`, size: 17, color: "595959" })] }))];
}
function bookStats() {                 // counted from the manuscript, so it never goes stale
  const files = PARTS.flatMap(p => p.files);
  const chapters = files.filter(f => /^# Chapter \d+/m.test(read(f))).length;
  const interludes = files.filter(f => /^# Interlude/m.test(read(f))).length;
  const exercises = files.reduce((n, f) => n + (read(f).match(/^:::ex /gm) || []).length, 0);
  const capstones = (read("90_capstones.md").match(/^## Capstone \d+/gm) || []).length;
  return `${chapters} chapters · ${interludes} interludes · ${exercises} exercises with solutions · ${capstones} capstone projects`;
}
function titlePage() {
  return [
    new Paragraph({ spacing: { before: 2200 }, children: [] }),
    center("BUILDING AGENTIC AI SYSTEMS", { size: 48, bold: true, color: ACCENT, font: HFONT }, 240),
    center("From First Agent to MCP, Multi-Agent Orchestration,", { size: 28, color: "404040", font: HFONT }, 40),
    center("and Production", { size: 28, color: "404040", font: HFONT }, 480),
    new Paragraph({ alignment: AlignmentType.CENTER, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: ACCENT, space: 1 } }, spacing: { after: 480 }, children: [] }),
    center("A hands-on guide with Python and the Model Context Protocol", { size: 22, color: "404040" }, 100),
    center(bookStats(), { size: 19, color: "404040" }, 2400),
    center("Srinivasa Rao Bittla", { size: 28, bold: true, font: HFONT }, 80),
  ];
}
function copyrightPage() {
  const L = (t, r) => small(t, r, 110);
  return [
    new Paragraph({ spacing: { before: 5200 }, children: [] }),
    L("Building Agentic AI Systems: From First Agent to MCP, Multi-Agent Orchestration, and Production", { bold: true }),
    L("Copyright © 2026 Srinivasa Rao Bittla. All rights reserved."),
    L("No part of this book may be reproduced, stored in a retrieval system or transmitted in any form or by any means without the prior written permission of the author, except for brief quotations in reviews and articles."),
    L("Companion code, exercises and solutions: github.com/sbittla/building-agentic-ai"),
    L("First edition: September 2026. Second printing, corrected: October 2026. Companion code: tag edition-1.1 of the repository. Corrections to this printing are listed in ERRATA.md in the repository."),
    L("Trademarks: Claude is a trademark of Anthropic PBC. Python is a registered trademark of the Python Software Foundation. Docker is a trademark of Docker, Inc. Other product and company names mentioned may be trademarks of their respective owners. They are used in an editorial fashion only, with no intention of infringement."),
    L("While every precaution has been taken in preparing this book, the author assumes no responsibility for errors or omissions, or for damages resulting from the use of the information or code it contains. AI models, APIs, prices and libraries change often; check current documentation before relying on any detail in production. Running the examples uses a paid API; you are responsible for your own usage and costs."),
    L("The code, data and solutions in the companion repository are released under the MIT License: you may use, copy and adapt them in your own projects, including commercial ones, provided the copyright and license notice are kept. The license applies to the code only; the text of this book remains all rights reserved."),
  ];
}

// ---------- book structure ----------
const PARTS = [
  { num: 0, title: "Foundations", files: ["00z_ch00.md", "00zz_python.md"],
    blurb: "Before you build an agent, you need a few basics: the terminal, Python, JSON, web APIs, secrets and Docker. This part teaches exactly those, and nothing more. If you already write Python and have called a web API, skim it and do the checkpoint." },
  { num: 1, title: "Your First Agent", files: ["01.md", "01z_testing.md", "02.md", "03.md", "04.md"],
    stages: "Decide, Build, Evaluate",
    blurb: "An agent is a model plus tools plus a loop. You make your first model call, give the model tools, teach it to choose between them, even among dozens, and write the loop that lets it work step by step until the job is done." },
  { num: 2, title: "State and Environment", files: ["05.md", "05z_regex.md", "06.md"],
    stages: "Build",
    blurb: "Agents become useful when they remember and look around. You give an agent state that survives a restart and let it explore a folder of notes safely, answering questions with citations." },
  { num: 3, title: "Real-World Tools", files: ["07.md", "07z_sql.md", "08.md", "08z_measure.md", "09.md"],
    stages: "Build, Evaluate, Release",
    blurb: "Real tools fail, return too much data and can do damage. You connect agents to a live web API and a database, teach them to correct their own mistakes and put a human approval gate in front of every risky action." },
  { num: 4, title: "Autonomy and Multi-Agent Systems", files: ["10.md", "10z_async.md", "11.md"],
    stages: "Build, Evaluate",
    blurb: "With a feedback loop, an agent can check its own work. You build an agent that fixes code until the tests pass, inside firm guardrails. Then you build your first teams: a lead with parallel researchers, a router, a handoff pipeline, a writer with a critic and a vote." },
  { num: 5, title: "MCP and Interoperability", files: ["12.md", "13.md", "14.md", "15.md"],
    stages: "Build, Release",
    blurb: "The Model Context Protocol lets you package tools once and use them from any agent. You build servers and a client, publish an agent as a server, adopt servers you didn't write safely, and see what the 2026 protocol changes on the wire." },
  { num: 6, title: "Context, Memory and Knowledge", files: ["16.md", "17.md", "18.md"],
    stages: "Build, Improve",
    blurb: "What an agent knows at each step decides what it can do. You engineer the context of every call, give agents memory with clear rules about what to keep and for how long, and build knowledge systems in which the agent decides what to look up, where, and whether to trust it." },
  { num: 7, title: "Advanced Agent Architectures", files: ["19.md", "20.md", "21.md", "22.md", "23.md", "24.md"],
    stages: "Design, Build",
    blurb: "Real work takes hours, crosses teams and touches systems that must not break. You build agents that checkpoint and recover, plan and pick the right model for each step, orchestrate other agents, run inside deterministic guardrails, operate a browser, and you see what frameworks and agent runtimes provide." },
  { num: 8, title: "Trust, Security and Identity", files: ["25.md", "26.md"],
    stages: "Design, Release",
    blurb: "Autonomy is only as good as the trust behind it. You defend agents against the attacks aimed at them, from poisoned tools to poisoned memory, and give every agent an identity, least-privilege permissions and an audit trail." },
  { num: 9, title: "Production Engineering", files: ["27.md", "28.md", "29.md", "30.md"],
    stages: "Evaluate, Release, Operate, Improve, Retire",
    blurb: "Production agents are measured, observed, economical and deployed. You evaluate whole trajectories continuously, trace every decision, engineer cost per successful task, ship your agent as a secure service and run MCP at company scale behind a gateway." },
];
const PART_EXISTS = f => fs.existsSync(path.join(ROOT, "md", f));
for (const p of PARTS) p.files = p.files.filter(PART_EXISTS);   // chapters are added part by part
const FRONT = ["fm_preface.md", "fm_acknowledgments.md", "fm_author.md", "00_front.md"];
const BACK = ["89_case_study.md", "90_capstones.md", "90z_afterword.md", "91_appendix.md"];
const readRaw = f => fs.readFileSync(path.join(ROOT, "md", f), "utf8");
// "{{exercises:none}}" and friends: counted from the manuscript and model_needs.json, so they never go stale.
// Kinds: all, none, any, claude-rec, claude-only; "{{exercises-word:claude-only}}" spells the number out.
function exerciseCounts() {
  const all = [...FRONT, ...PARTS.flatMap(p => p.files), ...BACK].filter(PART_EXISTS);
  const ids = all.flatMap(f => [...readRaw(f).matchAll(/^:::ex \w+ \| ([\w.]+) \|/gm)].map(m => m[1]));
  const kind = id => { const k = MODEL_NEEDS[id].model; return k === "claude" || k === "desktop" ? "claude-only" : k; };
  const counts = { all: ids.length };
  for (const id of ids) counts[kind(id)] = (counts[kind(id)] || 0) + 1;
  return counts;
}
const WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"];
let COUNTS = null;
// "@@exercise-model-table": the Appendix H table of every exercise by the model it needs,
// one row per chapter and interlude, generated so it can't drift from model_needs.json.
function exerciseModelTable() {
  const rows = ["| Chapter | No model | qwen3.5:9b or Claude | Claude |", "| --- | --- | --- | --- |"];
  for (const f of PARTS.flatMap(p => p.files)) {
    const md = readRaw(f);
    const ids = [...md.matchAll(/^:::ex \w+ \| ([\w.]+) \|/gm)].map(m => m[1]);
    if (!ids.length) continue;
    const col = k => ids.filter(id => k.includes(MODEL_NEEDS[id].model));
    const claude = ids.filter(id => ["claude-rec", "claude", "desktop"].includes(MODEL_NEEDS[id].model))
      .map(id => `${id} (${MODEL_NEEDS[id].model === "claude-rec" ? "recommended" : "only"})`);
    const cell = a => a.length ? a.join(", ") : "—";
    rows.push(`| ${md.match(/^# (.+)$/m)[1].trim()} | ${cell(col(["none"]))} | ${cell(col(["any"]))} | ${cell(claude)} |`);
  }
  return rows.join("\n");
}
// "@@all-links-table": Appendix G's "every link, by chapter", built from each Learn more table in book order.
function allLinksTable() {
  const rows = ["| Chapter | Resources |", "| --- | --- |"];
  for (const f of ["00_front.md", ...PARTS.flatMap(p => p.files), "90_capstones.md"].filter(PART_EXISTS)) {
    const md = readRaw(f);
    const sec = md.match(/^## Learn more\n([\s\S]*?)(?=^## |(?![\s\S]))/m);
    if (!sec) continue;
    const links = [...sec[1].matchAll(/^\| \*\*(.+?)\*\*<br>\[[^\]]*\]\(([^)]+)\)/gm)].map(m => `[${m[1]}](${m[2]})`);
    if (links.length) rows.push(`| ${md.match(/^# (.+)$/m)[1].trim()} | ${links.join("<br>")} |`);
  }
  return rows.join("\n");
}
const read = f => readRaw(f).replace(/^@@exercise-model-table$/m, () => exerciseModelTable()).replace(/^@@all-links-table$/m, () => allLinksTable()).replace(/\{\{exercises(-word)?:([\w-]+)\}\}/g, (_, word, k) => {
  COUNTS = COUNTS || exerciseCounts();
  const n = COUNTS[k] || 0;
  return word ? (WORDS[n] || String(n)) : String(n);
});
const h1 = f => read(f).match(/^# (.+)$/m)[1].trim();

// ---------- numbering plan for tables, figures and listings ----------
// Chapters number their own (Table 4.1); interludes use their letter (Table S.1, as their sections
// and exercises do). Front matter, capstones, the Afterword and the appendices get titles only.
const INTERLUDE_LETTER = { "00zz_python.md": "P", "01z_testing.md": "T", "05z_regex.md": "R",
                           "07z_sql.md": "S", "08z_measure.md": "M", "10z_async.md": "A" };
const PLAN = {}, LABELS = {};
function planCaptions() {
  for (const f of [...FRONT, ...PARTS.flatMap(p => p.files), ...BACK].filter(PART_EXISTS)) {
    const text = read(f), ch = text.match(/^# Chapter (\d+):/m);
    const plan = PLAN[f] = { prefix: ch ? ch[1] : (INTERLUDE_LETTER[f] || null), Table: 0, Figure: 0, Listing: 0 };
    const lines = text.split("\n");
    for (let i = 0; i < lines.length; i++) {        // the same blocks convert() skips are skipped here
      const l = lines[i];
      if (l.startsWith("```")) { i++; while (i < lines.length && !lines[i].startsWith("```")) i++; continue; }
      if (/^:::(note|tip|warn|ex) /.test(l)) { while (i < lines.length && lines[i].trim() !== ":::") i++; continue; }
      if (/^@@code /.test(l)) { plan.Listing++; continue; }
      const m = l.match(CAPTION_RE);
      if (!m) continue;
      const n = ++plan[m[1]];
      const label = m[2].match(LABEL_RE)[2];
      if (!label) continue;
      if (label in LABELS) throw new Error(`label ${label} is used twice (${f})`);
      LABELS[label] = plan.prefix ? `${m[1]} ${plan.prefix}.${n}` : null;
    }
  }
}
// "{{t:label}}" -> "Table 4.1", "{{f:label}}" -> "Figure 4.1"
const md = f => read(f).replace(/\{\{([tf]:[\w-]+)\}\}/g, (_, l) => {
  if (!(l in LABELS)) throw new Error(`${f}: {{${l}}} refers to a label that doesn't exist`);
  if (!LABELS[l]) throw new Error(`${f}: {{${l}}} refers to a table or figure that isn't numbered`);
  return LABELS[l];
});
planCaptions();

// ---------- headers and footers ----------
const HDR = { size: 16, color: "595959", font: HFONT };
const rule = { bottom: { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF", space: 4 } };
const empty = () => ({ headers: { default: new Header({ children: [new Paragraph({ children: [] })] }),
                                  even: new Header({ children: [new Paragraph({ children: [] })] }),
                                  first: new Header({ children: [new Paragraph({ children: [] })] }) },
                       footers: { default: new Footer({ children: [new Paragraph({ children: [] })] }),
                                  even: new Footer({ children: [new Paragraph({ children: [] })] }),
                                  first: new Footer({ children: [new Paragraph({ children: [] })] }) } });
function running(title) {
  const odd = new Paragraph({ border: rule, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    children: [new TextRun({ text: `\t${title}     `, ...HDR }), new TextRun({ children: [PageNumber.CURRENT], ...HDR, bold: true, color: "404040" })] });
  const even = new Paragraph({ border: rule,
    children: [new TextRun({ children: [PageNumber.CURRENT], ...HDR, bold: true, color: "404040" }), new TextRun({ text: `     ${BOOK}`, ...HDR })] });
  const firstFooter = new Paragraph({ alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], ...HDR })] });
  return { headers: { default: new Header({ children: [odd] }), even: new Header({ children: [even] }),
                      first: new Header({ children: [new Paragraph({ children: [] })] }) },
           footers: { default: new Footer({ children: [new Paragraph({ children: [] })] }),
                      even: new Footer({ children: [new Paragraph({ children: [] })] }),
                      first: new Footer({ children: [firstFooter] }) } };
}
let NUMFMT = NumberFormat.LOWER_ROMAN;
const pageProps = (extra = {}) => ({
  titlePage: true,
  page: { size: { width: PAGE_W, height: PAGE_H },
          margin: { top: M_TOP, bottom: M_BOT, left: M_IN, right: M_OUT, header: 600, footer: 560, gutter: 0 },
          pageNumbers: { formatType: NUMFMT, ...((extra.page || {}).pageNumbers || {}) } },
  type: extra.type ?? SectionType.NEXT_PAGE,          // no blank pages except before a part
});

// ---------- assemble ----------
const sections = [];
const addSection = (children, hf, extra) => sections.push({ properties: pageProps(extra), ...hf, children });

// front matter (roman numerals)
addSection(halfTitle(), empty(), { type: SectionType.NEXT_PAGE, page: { pageNumbers: { start: 1 } } });
addSection(alsoBy(), empty());                         // the back of the half-title page
addSection(titlePage(), empty());
addSection(copyrightPage(), empty());
addSection([new Paragraph({ spacing: { before: 3600 }, alignment: AlignmentType.CENTER, children: [] }),
            ...read("fm_dedication.md").split("\n").filter(l => l.trim() && !l.startsWith("#"))
              .map(l => new Paragraph({ alignment: AlignmentType.CENTER, children: inline(l, { italics: true }) }))], empty());
const tocIndex = sections.length;
sections.push(null);                                   // Contents, filled in after the body is converted
sections.push(null);                                   // List of Figures and Tables, filled in at the end
for (const f of FRONT) addSection(convert(md(f), f), running(h1(f)));

// main matter (arabic numerals from Part 0)
let firstMain = true;
NUMFMT = NumberFormat.DECIMAL;
for (const part of PARTS) {
  if (!part.files.length) continue;                     // a part whose chapters aren't written yet
  part.contents = part.files.map(h1);
  addSection(partOpener(part), empty(),
             firstMain ? { type: SectionType.ODD_PAGE, page: { pageNumbers: { start: 1 } } }
                       : { type: SectionType.NEXT_PAGE });       // no blank page before a part
  firstMain = false;
  for (const f of part.files) addSection(convert(md(f), f), running(h1(f)));
}
for (const f of BACK) addSection(convert(md(f), f), running(h1(f)));

// contents
const contentsChildren = [
  new Paragraph({ spacing: { before: 900, after: 360 }, children: [new TextRun({ text: "Contents", font: HFONT, size: 44, bold: true, color: ACCENT })] }),
  ...tocEntries(),
];
NUMFMT = NumberFormat.LOWER_ROMAN;
sections[tocIndex] = { properties: pageProps(), ...running("Contents"), children: contentsChildren };
// List of Figures and List of Tables: one entry per numbered caption, page numbers as in the Contents
function captionList(kind, heading) {
  const entries = HEADINGS.filter(h => h.cap === kind);
  return [
    new Paragraph({ spacing: { before: 900, after: 360 }, pageBreakBefore: kind === "Table",
                    children: [new TextRun({ text: heading, font: HFONT, size: 44, bold: true, color: ACCENT })] }),
    ...entries.map(({ id, text }) => new Paragraph({
      tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W, leader: "dot" }],
      indent: { left: 1100, hanging: 1100 }, spacing: { after: 30, line: 240 },
      children: [new InternalHyperlink({ anchor: id, children: [
        new TextRun({ text: text.replace(/^(\S+ \S+)\s+/, "$1\t"), size: 17 }),
        new TextRun({ text: `\t${TOC_PAGES[id] ?? "000"}`, size: 17 })] })] })),
  ];
}
sections[tocIndex + 1] = { properties: pageProps(), ...running("List of Figures and Tables"),
                           children: [...captionList("Figure", "List of Figures"), ...captionList("Table", "List of Tables")] };

const monoFont = fs.readFileSync("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf");
const doc = new Document({
  creator: "Srinivasa Rao Bittla",
  title: "Building Agentic AI Systems",
  subject: "From First Agent to MCP, Multi-Agent Orchestration, and Production",
  evenAndOddHeaderAndFooters: true,
  fonts: [{ name: MONO, data: monoFont, characterSet: CharacterSet.ANSI }],
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 48, bold: true, color: ACCENT, font: HFONT },
        paragraph: { spacing: { before: 0, after: 480 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 8 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: ACCENT, font: HFONT },
        paragraph: { spacing: { before: 300, after: 110 }, outlineLevel: 1, keepNext: true } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, color: "000000", font: HFONT },
        paragraph: { spacing: { before: 220, after: 90 }, outlineLevel: 2, keepNext: true } },
      { id: "Caption", name: "caption", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 18, color: "262626", font: HFONT, bold: true },   // the number is a field: it takes the style's bold
        paragraph: { spacing: { before: 120, after: 120, line: 252 } } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 240 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 240 } } } } ] },
      ...[1, ...NUMBER_STARTS].map(start => ({ reference: start === 1 ? "numbers" : `numbers_from_${start}`, levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", start, alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 300 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 240 } } } } ] })),
    ],
  },
  sections,
});

const outPath = process.argv[2] || path.join(ROOT, "Building_Agentic_AI_Systems.docx");
fs.writeFileSync(path.join(__dirname, "toc_headings.json"), JSON.stringify(HEADINGS, null, 1));
fs.writeFileSync(path.join(DIAGRAMS, "report.json"), JSON.stringify(DIAGRAM_REPORT, null, 1));
if (CAPTION_WARNINGS.length) {
  console.error(`${CAPTION_WARNINGS.length} caption warnings:`);
  for (const w of CAPTION_WARNINGS) console.error("  " + w);
}
// docx gives every picture the same drawing id; Word wants them unique, so renumber them
const JSZip = require(require.resolve("jszip", { paths: [path.dirname(require.resolve("docx"))] }));
Packer.toBuffer(doc).then(async buf => {
  const zip = await JSZip.loadAsync(buf);
  let n = 0;
  for (const name of Object.keys(zip.files).filter(f => /^word\/(document|header\d*|footer\d*)\.xml$/.test(f))) {
    const xml = await zip.file(name).async("string");
    zip.file(name, xml.replace(/<wp:docPr id="\d+"/g, () => `<wp:docPr id="${++n}"`));
  }
  buf = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
  fs.writeFileSync(outPath, buf); console.log("wrote", outPath, buf.length, "bytes;", n, "pictures");
});
