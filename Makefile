PREFIX = /usr
BINDIR = $(PREFIX)/bin
MANDIR = $(PREFIX)/share/man/man1

INSTALL = install

all:	README

install:
	$(INSTALL) -m 755 barg.py $(BINDIR)/barg
	$(INSTALL) -m 644 doc/barg.1 $(MANDIR)/barg.1

uninstall:
	rm $(BINDIR)/barg
	rm $(MANDIR)/barg.1

README:	doc/barg.1
	# readme is the manpage
	MANWIDTH="76" man -P cat -l doc/barg.1 > README
