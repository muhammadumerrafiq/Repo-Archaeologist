# Repo Archaeologist — Frontend Design Brief

## 1. Visual Direction: "The Survey Sheet"
The UI approaches repository analysis as a precision archaeological excavation survey rather than a modern marketing dashboard.
- **Tone:** Dry, technical, precise field notes. No hype, no buzzwords.
- **Form Language:** Clean hairline borders (`1px solid #1D222B`), subtle tick marks at structural boundaries, monospace catalog stamps, and key-value survey sheets.
- **No Banned AI-Template Tropes:** Zero purple/blue gradients, zero neon glassmorphism, zero pill buttons, zero decorative floating blobs, zero emojis as interface icons.

---

## 2. Color System & Meaning
Every color carries specific semantic meaning (color is never used decoratively):

| Token | Hex | Role | Contrast Ratio |
|---|---|---|---|
| `--bg-0` | `#07080A` | Canvas background | Base |
| `--bg-1` | `#0C0E12` | Panel surfaces & tables | > 1.2:1 vs bg-0 |
| `--bg-2` | `#12151B` | Raised cards & input fields | > 1.5:1 vs bg-0 |
| `--line` | `#1D222B` | Hairline separators | Structural |
| `--line-strong`| `#2A313D` | Active / focused borders | Interactive |
| `--text-0` | `#E7EAEE` | Primary headers & essential text | 14.8:1 on bg-0 (AAA) |
| `--text-1` | `#9AA3AF` | Descriptions & secondary metadata | 8.2:1 on bg-0 (AAA) |
| `--text-2` | `#646C78` | Tertiary labels & coordinates | 4.6:1 on bg-0 (AA) |
| `--cyan` | `#4FD8EB` | **CONFIRMED** facts & primary actions | 12.1:1 on bg-0 (AAA) |
| `--violet` | `#9D8CFF` | **HEURISTIC** inferences & conventions | 8.4:1 on bg-0 (AAA) |
| `--amber` | `#E8B964` | Warnings & partial results | 10.9:1 on bg-0 (AAA) |
| `--red` | `#F26B6B` | Critical errors & failed states | 7.2:1 on bg-0 (AAA) |

---

## 3. Typography & Hierarchy
Self-hosted fonts via `@fontsource` packages (Geist Sans + JetBrains Mono).

- **Primary UI Font:** Geist Sans (body, paragraphs, table labels)
- **Code & Metadata Font:** JetBrains Mono (file paths, catalog numbers, provenance stamps, numerical stats, code blocks)
- **Type Scale:**
  - `Display / Hero Title`: 44px (tracking -0.02em, medium)
  - `Section Header (H2)`: 20px (tracking -0.01em, medium)
  - `Artifact Title (H3)`: 14px (font-mono, medium)
  - `Body Text`: 14px (regular, leading 1.6)
  - `Small Data Label`: 12px (font-mono, uppercase, tracking +0.05em)
  - `Stamp / Micro Label`: 11px (font-mono, uppercase, tracking +0.08em, bold)

---

## 4. Signature Elements Specification (Section 8.3)

1. **Strata Grid:**
   - Subtle `1px` grid lines at `40px` increments with coordinate ticks on container borders.
2. **Provenance Stamps:**
   - `CONFIRMED`: Solid 1px cyan outline, small filled dot (`bg-cyan`), uppercase mono text `CONFIRMED`.
   - `HEURISTIC`: Dashed 1px violet outline, hollow dot (`border-violet`), uppercase mono text `HEURISTIC`.
   - Tooltip explains: *"Confirmed: directly observable fact from code or manifest"* vs *"Heuristic: inferred from standard naming convention"*.
3. **Artifact Cards:**
   - Sequential catalog IDs (`ART-001`, `ART-002`, ...).
   - Minimalist row layout separated by hairline borders. Includes label, summary, provenance stamp, and an *"Evidence"* expansion trigger.
4. **Evidence Drawer:**
   - Slide-in side drawer displaying exact file path in monospace, GitHub source hyperlink, and exact evidence reasons.
5. **Honest Excavation Log:**
   - Indeterminate stage indicators showing actual progress stages (*"Connecting to GitHub API"*, *"Inspecting file tree"*, *"Parsing manifests"*). Zero fabricated progress percentages.
6. **File Explorer Depth Rail:**
   - Vertical lines tracing indentation level, distinct file kind badges, search match highlighting, and instant GitHub direct links.
7. **Survey Sheet Overview:**
   - Compact key-value record table (stars, forks, size, branch, license, pushed at) paired with a segmented language bar showing exact percentages.
8. **Architecture Graph:**
   - Dark dotted canvas with solid (import), dashed (config), and dotted (declared dependency) edges, accompanied by a visual legend.

---

## 5. Banned Patterns Checklist (Section 8.9)
- [x] No purple-to-blue gradients or aurora backgrounds
- [x] No glassmorphism or heavy blur filters
- [x] No decorative emojis (using Lucide geometric icons only)
- [x] No hype words ("AI-powered", "revolutionary", "supercharge", "next-gen")
- [x] No `rounded-2xl` pill shapes (radii strictly 2px to 6px)
- [x] No placeholder lorem ipsum
