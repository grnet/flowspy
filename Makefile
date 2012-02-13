flowspytag = $(shell git describe --abbrev=0)
flowspyver = $(shell git describe --abbrev=0 | egrep -o '([0-9]\.){1,10}[0-9]')

.PHONY: dist distclean

dist: 
	git archive --format tar --prefix flowspy-$(flowspyver)/ -o flowspy-$(flowspyver).tar $(flowspytag)
	gzip -f flowspy-$(flowspyver).tar
distclean:
	@rm -f *tar.gz

