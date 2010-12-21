.PHONY: default srv lib/link clean 

default: lib.zip

srv:
	dev_appserver.py ./ --port 8083 --blobstore_path .tmp/blobstore --datastore_path .tmp/datastore 
	#--debug_imports


XMLRPCSERVER := xmlrpcserver-0.99.2.tar.gz

lib/link:
	cd lib;
	if test ! -f $(XMLRPCSERVER); then \
		wget http://www.julien-oster.de/projects/xmlrpcserver/dist/$(XMLRPCSERVER); \
		tar xzvf $(XMLRPCSERVER); fi;
	-ln -s xmlrpcserver/xmlrpcserver.py 
	@echo "These may need to be resolved manually:"
	-ln -s /home/berend/src/python-breve/latest/breve
	-ln -s /home/berend/src/nabu/working/lib/python/nabu
	-ln -s /home/berend/src/python-docutils/docutils.svn/trunk/docutils/docutils
	-ln -s /usr/share/pyshared/roman.py
	-ln -s ../../docutils/dotmpe
	-ln -s ../../vestige
	-ln -s ~/src/python-gae-sessions/latest/gaesessions
	-ln -s /home/berend/projects/gate-vc/src/gate
	-ln -s /usr/lib/python2.5/site-packages/zope

lib.zip:
	cd lib;zip $@ -r zope \
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
