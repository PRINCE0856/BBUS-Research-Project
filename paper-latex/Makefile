# Build the paper.
#
#   make          -> main.pdf (three pdflatex passes; no BibTeX needed, the
#                    reference list is a thebibliography in references.tex)
#   make bibtex   -> build using refs.bib + BibTeX instead (see README.md)
#   make clean    -> remove auxiliary files
#   make distclean-> also remove main.pdf

LATEX   = pdflatex -interaction=nonstopmode -file-line-error
MAIN    = main
SOURCES = $(MAIN).tex appendix.tex references.tex
FIGURES = $(wildcard figures/*.pdf)

.PHONY: all bibtex clean distclean

all: $(MAIN).pdf

$(MAIN).pdf: $(SOURCES) $(FIGURES)
	$(LATEX) $(MAIN).tex
	$(LATEX) $(MAIN).tex
	$(LATEX) $(MAIN).tex

bibtex: $(SOURCES) refs.bib $(FIGURES)
	$(LATEX) $(MAIN).tex
	bibtex $(MAIN)
	$(LATEX) $(MAIN).tex
	$(LATEX) $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.bbl *.blg *.toc *.lof *.lot *.spl *.fls \
	      *.fdb_latexmk

distclean: clean
	rm -f $(MAIN).pdf
