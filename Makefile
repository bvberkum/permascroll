.PHONY: default srv

default:

srv:
	dev_appserver.py ./ --port 8083 --blobstore_path .tmp/blobstore --datastore_path .tmp/datastore

# vim:noet
