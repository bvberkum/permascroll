include                $(MK_SHARE)Core/Main.dirstack.mk
MK_$d               := $/Rules.mk
MK                  += $(MK_$d)
#
#      ------------ --

CLN                 += $(shell find -L $d -iname '*.pyc' )

#      ------------ --

XMLRPCSERVER        := xmlrpcserver-0.99.2.tar.gz
TRGT                += $/lib.zip

$/lib.zip:
	cd lib;zip $@ -r zope \
		-x '*/.svn*' -x '*/.bzr*' -x '*.pyc'; mv $@ ..

$/lib/link:
	@\
	echo "These may need to be resolved manually:"
	cd lib;\
	ln -s /srv/project-mpe/cllct/lib/python cllct;\
	ln -s /srv/project-mpe/gate/src/gate;\
	ln -s /srv/project-mpe/gate/src/gate;\
	ln -s /srv/project-mpe/docutils-ext/dotmpe;\
	ln -s /srv/project-mpe/uriref/src/py/uriref.py;\
	ln -s /src/python-filelike/filelike.git/filelike;\
	ln -s /srv/project-mpe/vestige;\
	ln -s /src/python-breve/latest/breve;\
	ln -s /src/nabu/working/lib/python/nabu;\
	ln -s /src/python-docutils/latest/trunk/docutils/docutils;\
	ln -s /src/python-gae-sessions/latest/gaesessions;\
	ln -s /usr/share/pyshared/roman.py;\
	ln -s /usr/lib/python2.5/site-packages/zope;

.PHONY: $/lib/link

#      ------------ --

APP_ENGINE          := $(shell echo /src/google-appengine/google_appengine_*/|\
                        grep -v '\*'|sort -g|tr ' ' '\n'|tail -1)
ADDRESS             := $(shell hostname -s )

srv:: ADDRESS ?=
srv::
	$(APP_ENGINE)/dev_appserver.py ./ \
		--address $(ADDRESS) \
		--port 8083 \
		--blobstore_path .tmp/blobstore \
		--datastore_path .tmp/datastore
	#--debug_imports
.PHONY: srv

#      ------------ --

PY_TEST_$d          := $/test/main.py
TEST                += test_$d
.PHONY:                test_$d

test_$d:
	@$(call log_line,info,$@,Starting tests..)
	@\
	PYTHONPATH=$$PYTHONPATH:src/py:test/py;\
	TEST_PY=test/py/main.py;TEST_LIB=.;\
    $(test-python)

test:: test_$d

#      ------------ --
#
include                $(MK_SHARE)Core/Main.dirstack-pop.mk
# vim:noet:
