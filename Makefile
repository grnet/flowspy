flowspytag = $(shell git describe --abbrev=0)
flowspyver = $(shell git describe --abbrev=0 | egrep -o '([0-9]+\.){1,10}[0-9]+' | sed -e 's/\./_/g')
name   	   = $(shell basename $(shell pwd))

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = doc/build

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) doc/source

.PHONY: help dist distclean docclean html latex text

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  html      to make standalone HTML files"
	@echo "  latex     to make LaTeX files, you can set PAPER=a4 or PAPER=letter"
	@echo "  text      to make standalone txt files"

dist: 
	git archive --format tar --prefix $(name)-$(flowspyver)/ -o $(name)-$(flowspyver).tar $(flowspytag)
	gzip -f $(name)-$(flowspyver).tar

distclean:
	@rm -f *tar.gz

docclean:
	-rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

latex:
	$(SPHINXBUILD) -b latex $(ALLSPHINXOPTS) $(BUILDDIR)/latex
	@echo
	@echo "Build finished; the LaTeX files are in $(BUILDDIR)/latex."
	@echo "Run \`make all-pdf' or \`make all-ps' in that directory to" \
	      "run these through (pdf)latex."

text:
	$(SPHINXBUILD) -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Done"	

