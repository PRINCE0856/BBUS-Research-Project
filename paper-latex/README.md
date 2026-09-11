# LaTeX source that regenerates the Chou et al. (2025) simulator paper

A complete LaTeX project that rebuilds the published article

> Chou, K.-Y., Paulsen, M., Møller, M., & Fjendbo Jensen, A. (2025).
> Cyclists' mobility and subjective safety in shared urban spaces – a simulator
> study. *Transportation Research Part F: Psychology and Behaviour, 115*,
> Article 103321. <https://doi.org/10.1016/j.trf.2025.07.031>

— full text, all 3 equations, all 14 tables and all 10 figures — as a
21-page PDF in Elsevier's single-column journal layout, the same length as the
published article and with floats landing on much the same pages.

The article is open access under the
[CC BY 4.0 licence](http://creativecommons.org/licenses/by/4.0/), which permits
reproduction with attribution. The text, tables and figures here are
transcribed from the published version and remain the authors' work; the LaTeX
implementation of the layout is an approximation of Elsevier's production
template. **If you are reusing this as a template for your own manuscript,
replace the content — do not submit someone else's text.**

## Build

```bash
make            # three pdflatex passes -> main.pdf
make clean      # remove auxiliary files
```

Or directly:

```bash
pdflatex main.tex && pdflatex main.tex && pdflatex main.tex
# or: latexmk -pdf main.tex
```

No BibTeX run is needed by default. Requirements: a TeX distribution with
`elsarticle` (TeX Live package `texlive-publishers`), plus `booktabs`,
`longtable`, `threeparttable`, `makecell`, `multirow`, `caption`, `fancyhdr`,
`bm`, `microtype`, `mathptmx` and `hyperref` — all in a standard TeX Live
install. Verified with TeX Live 2023 / pdfTeX.

## Files

| File | Contents |
|---|---|
| `main.tex` | Preamble, front matter, Sections 1–6, CRediT and data-availability statements |
| `appendix.tex` | Appendix A (literature-review tables A.8–A.9), B (Figs B.9–B.10), C (full model tables C.10–C.14) |
| `references.tex` | Reference list as a hand-formatted `thebibliography` (55 entries) |
| `refs.bib` | The same 55 references in BibTeX form, for the BibTeX route below |
| `figures/*.pdf` | The 10 figures, cropped as vector PDFs from the published article |
| `Makefile` | Build targets |

## How the reproduction is put together

**Class, page size and type size.** `\documentclass[3p,authoryear]{elsarticle}`
gives the journal's single-column final layout. `\geometry{...}` sets the trim
size of the published article (544.25 × 742.68 bp ≈ 192 × 262 mm) with a 39 bp
side margin; a commented `\geometry{a4paper,margin=25mm}` line switches to A4.
`\usepackage[fontsize=9pt]{fontsize}` drops the body from elsarticle's 10 pt to
the journal's 9 pt, which is what makes the output come out at the same 21
pages. Switch `3p` to `5p` for two columns, or `preprint` for a submission
draft.

**Front matter.** Three small tweaks align elsarticle with the published first
page: the title block is set flush left (`\elsarticletitlealign`), the abstract
is headed `A B S T R A C T` (`\abstracttitle`), and `\ps@pprintTitle` is
redefined so page one carries the journal line and a page number instead of
elsarticle's "Preprint submitted to …" footer.

**Citations.** natbib in author-year mode. Because the labels in
`references.tex` carry both a short and a long form, `\citep` yields
`(Buehler & Pucher, 2021)` and `\citet*` yields `Buehler and Pucher (2021)`,
matching the journal's use of `&` inside parentheses and `and` in running text.
Use `\citet*` for narrative citations of two-author works and `\citet` for
everything else.

**Numbering.** Appendix tables and figures continue the main sequence
(Table 7 → Table A.8, Fig. 8 → Fig. B.9), so `appendix.tex` sets the counters
explicitly (`\setcounter{table}{7}`, `\setcounter{figure}{8}`,
`\setcounter{table}{9}`) and prefixes them with `\Alph{section}`.

**Tables.** booktabs rules throughout; `threeparttable` carries the
significance-star note under each model table; the two literature-review
tables are `longtable`s with ragged-right `p{}` columns so they break across
pages with a repeated header.

**Figures.** Each figure was cropped from the published PDF and kept as vector
artwork (`figures/*.pdf`), so plots and diagrams stay sharp at any zoom. The
panel labels of Figs 2 and 3 are part of the graphics.

## Using BibTeX instead of the hand-formatted list

`references.tex` exists so that the printed reference list matches the
published one exactly, down to the DOIs and trailing URLs. To drive the
bibliography from `refs.bib` instead, replace `\input{references}` near the end
of `main.tex` with

```latex
\bibliographystyle{elsarticle-harv}
\bibliography{refs}
```

and run `make bibtex`. Note that `elsarticle-harv` is Elsevier's own
author-year style, not APA: it prints `Buehler, R., Pucher, J., 2021.` rather
than `Buehler, R., & Pucher, J. (2021).`, and writes "and" instead of "&" in
citations.

## Known differences from the published PDF

The content is complete; these are layout and production details:

- **Float placement.** The length matches (21 pages) but individual figures and
  tables sometimes sit a page earlier or later than in the published version,
  and the appendix longtables break at different rows.
- **Publisher artwork is absent**: the ScienceDirect masthead, the journal
  logo, the "Check for updates" badge, the ORCID marks beside author names, and
  the first-page block with the DOI, submission dates and CC BY statement.
- **Link colour**: the published article colours only the year inside a
  citation; here citations are black and cross-references use the journal's
  blue.
- The published article carries no keywords block, so none is included.
- Fonts are the Times-compatible `mathptmx` rather than Elsevier's licensed
  Univers/Times cuts, so line breaks differ slightly.

## Provenance and checks

Text, table values and figures were transcribed from the published PDF; figures
were cropped from it directly. Nothing was re-estimated or re-drawn and no
value was inferred.

Two automated checks were run against the published PDF's text layer:

- **Tables.** All 330 numbers in the ten model tables (3–7 and C.10–C.14) were
  extracted from both PDFs and compared in order — every value matches.
- **Body text.** Of 262 prose sentences in the published text (abstract through
  the conclusion, equations excluded), 235 appear verbatim in the
  reproduction. The 27 that did not match exactly were each inspected: they are
  artefacts of comparing text layers — sentences interrupted by a float or page
  break, the first-page copyright block that is not reproduced, and places where
  the published text layer drops the space after a hyperlinked number
  ("Fig. 5shows", "Table A.8in Appendix A"). A word-frequency comparison of the
  whole body found no content word added, dropped or altered.

Neither check can substitute for your own reading: before reusing any number or
citation from here, verify it against the published article at
<https://doi.org/10.1016/j.trf.2025.07.031>.
