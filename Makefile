.PHONY: default srv lib/link clean 

ADDRESS := iris.dennenweg
#$(shell hostname)

APP_ENGINE := $(shell echo /src/google-appengine/google_appengine_*/|grep -v '\*'|sort -g|tr ' ' '\n'|tail -1)
default: lib.zip

srv: ADDRESS ?= 
srv:
	GAE_DEV=True \
	PYTHONPATH=lib/:$$PYTHONPATH \
	$(APP_ENGINE)/dev_appserver.py ./ \
		--address $(ADDRESS) \
		--port 8083 \
		--blobstore_path .tmp/blobstore \
		--datastore_path .tmp/datastore \
		--debug_imports

test:
	tools/test.sh

XMLRPCSERVER := xmlrpcserver-0.99.2

lib/link:
	cd lib;\
	if test ! -e $(XMLRPCSERVER); then \
        if test ! -f $(XMLRPCSERVER).tar.gz; then \
            wget http://www.julien-oster.de/projects/xmlrpcserver/dist/$(XMLRPCSERVER); \
        fi; \
        tar xzvf $(XMLRPCSERVER).tar.gz; fi;
	-cd lib;ln -s xmlrpcserver/xmlrpcserver.py 
	@echo "These may need to be resolved manually:"
	-cd lib;ln -s /home/berend/src/python-breve/latest/breve
	-cd lib;ln -s /home/berend/src/nabu/working/lib/python/nabu
	-cd lib;ln -s /home/berend/src/python-docutils/docutils.svn/trunk/docutils/docutils
	-cd lib;ln -s /usr/share/pyshared/roman.py
	-cd lib;ln -s ../../docutils/dotmpe
	-cd lib;ln -s ../../vestige
	-cd lib;ln -s ~/src/python-gae-sessions/latest/gaesessions
	-cd lib;ln -s /home/berend/projects/gate-vc/src/gate
	-cd lib;ln -s /usr/lib/python2.5/site-packages/zope

lib.zip: Makefile
	cd lib;zip $@ -r breve nabu zope \
		-x '*/.svn*' -x '*/.bzr*' -x '*.pyc'; mv $@ ..

clean: 
	find -L ./ -iname '*.pyc'|while read f; do sudo rm $$f;done

clean-user:: clean-db clean-blobs
	@echo "Removed local datastore and blobstore. "

clean-db:: 
	rm .tmp/datastore

clean-blobs:: 
	rm .tmp/blobstore


# vim:noet
