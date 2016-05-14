include                $(MK_SHARE)Core/Main.dirstack.mk
MK_$d               := $/Rules.mk
MK                  += $(MK_$d)
#
#      ------------ --

CLN                 += $(shell find -L $d -iname '*.pyc' ) \
	.tmp/datastore \
	.tmp/blobstore

#      ------------ --

XMLRPCSERVER        := xmlrpcserver-0.99.2
TRGT                += $/lib.zip

$/lib.zip: $/Rules.mk 
	cd lib;zip $@ -r . \
		-x '*/.svn*' -x '*/.bzr*' -x '*.pyc'; mv $@ ..

$/lib/link:
	@\
	echo "These may need to be resolved manually:"
	cd lib;\
	if test ! -e xmlrpcserver; then \
        if test ! -f $(XMLRPCSERVER).tar.gz; then \
            wget http://www.julien-oster.de/projects/xmlrpcserver/dist/$(XMLRPCSERVER).tar.gz; \
        fi; \
        tar xzvf $(XMLRPCSERVER).tar.gz; fi;
	-cd lib;ln -s /srv/project-mpe/cllct/lib/python cllct;
	-cd lib;ln -s /srv/project-mpe/gate/src/gate;
	-cd lib;ln -s /srv/project-mpe/gate/src/gate;
	-cd lib;ln -s /srv/project-mpe/docutils-ext/dotmpe;
	-cd lib;ln -s /srv/project-mpe/uriref/uriref;
	-cd lib;ln -s /src/python-filelike/filelike.git/filelike;
	-cd lib;ln -s /srv/project-mpe/vestige;
	-cd lib;ln -s /src/python-breve/latest/breve;
	-cd lib;ln -s /src/nabu/working/lib/python/nabu;
	-cd lib;ln -s /src/python-docutils/latest/trunk/docutils/docutils;
	-cd lib;ln -s /src/python-gae-sessions/latest/gaesessions;
	-cd lib;ln -s /usr/share/pyshared/roman.py;
	-cd lib;ln -s /usr/lib/python2.5/site-packages/zope;

.PHONY: $/lib/link

#      ------------ --

gae-init::
	$Dtools/init.sh

.PHONY: gae-init

#      ------------ --

APP_ENGINE          := /src/google-appengine/working
#APP_ENGINE          := $(shell echo /src/google-appengine/google_appengine_*/|\
#                        grep -v '\*'|sort -g|tr ' ' '\n'|tail -1)
ifeq ($(APP_ENGINE), )
$(error Need GAE somewhere in /src/google-appengine/google_appengine_*)
else
$(info GAE dir $(shell cd $(APP_ENGINE);pwd -P))
endif
ADDRESS             := $(shell hostname)

srv:: ADDRESS ?=
srv::
	GAE_DEV=True \
	$(APP_ENGINE)/dev_appserver.py ./ \
		--address $(ADDRESS) \
		--port 8083 \
		--blobstore_path .tmp/blobstore \
		--datastore_path .tmp/datastore 
.PHONY: srv

#      ------------ --

PY_TEST_$d          := $/test/main.py
TEST                += test_$d
.PHONY:                test_$d gae-test

test_$d:
	@$(call log_line,info,$@,Starting tests..)
	@\
	PYTHONPATH=$$PYTHONPATH:src/py:test/py;\
	TEST_PY=test/py/main.py;TEST_LIB=.;\
    $(test-python)

gae-test::
	$Dtools/init.sh

test:: test_$d gae-test

#      ------------ --
#
include                $(MK_SHARE)Core/Main.dirstack-pop.mk
# vim:noet:
