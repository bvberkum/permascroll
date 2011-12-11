#!/usr/bin/env
"""Permascroll client.

HTTP operations (GET/PUT/POST/DELETE) on application/x-www-form-urlencoded entities.

This client is like a blog client in that it manages remote entities with a
metadata struct that most syndication feeds and blogs have in common.

Other than that the permascroll is a continious, adressable space of the virtual
positions in these documents. Addressing is accomplished by tumblers.

Metadata::

    author/agent/contact/mailbox
    organisation
    publication
    modification
    status: private|experimental|draft|published

% publish 
% prepare 
% update
% unpublish
% clear


Permascroll data entities and URL space
---------------------------------------
The resources of concern are those with virtual positions, lets call these the entities.

For these entities we like tumbler addressing, yet to manage the server we use
a REST API for which we think in URL paths and server-side handlers.

Tumblers
~~~~~~~~
Permascroll tumblers are modelled after Xu88.1 which keeps:

    - Space and Node
    - Account
    - Document
    - Virtual spaces

E.g. these are the hierarchy roots::

  1.1               First space, first node
  1.1.0.1           First Account
  1.1.0.1.0.1       First Document
  1.1.0.1.0.1.0.1   First Virtual Space

The virtual space is modelled after Xu88.1 too. A document may have multiple
spaces for addressing literal, bitmap, video or other data.
Permascroll uses the first space for addressing characters, and the second 
for the unique address for each xanalogical link. E.g.::

  1.1.0.1.0.1.0.1.123   Some character in the first document
  1.1.0.1.0.1.0.2.21    Some link in the first document

UANA is only an idea yet, there are no public tumbler spaces for nodes,
documents or users. 

XXX
 - So permascroll does not claim a host address but uses HTTP URLs for permanent identity?
 - After a user/group system has been devised it may be usefull to assign
   tumbler addresses to these.

URLs
~~~~~
URLs are mapped to a RESTful component hooked to an URL endpoint. 
These may operate on one or more resources trough parameters.

Other records are kept by the server like user, mailinglists, any domain specific info.
In addition some of these have public URL endpoints?


 feed/1/entry/1


Data
----
To get an idea of the datastore bootstrapping and URL handlers, the document
tumbler is also shown::

 / 								    Permascroll (localhost address [*]_)
  user/             	      	    Homepage (root of all accounts on this node)
  user/1                            Homepage user=berend.van.berkum@gmail.com
  frontpage  			1 		    Frontpage (the default document)
  feed/ 				2     	    Feedhandler
       123/         	2.123 		Feedhandler (Space)
           entry/ 		2.123 		Feedhandler
                 543  	2.123.543 	Feedhandler (Item -> MIMEMessage)
  /feed/.*.html         2.1         Feedbrowser

  frontpage	            1     	    Feedhandler (kind=document)
  frontpage?v=123       1.123     	Current Frontpage

  statistics            1     	    Feedhandler (kind=report)
  statistics?v=123      1.123     	Statistics for some period

  feed/ 				2     	    Feedhandler (kind=mailinglist)
                    	2.1 		Yahoo Mailinglist
       1            	2.1.1 	    teslasflyingmachine
        entry/543 	    2.1.1.543   Feedhandler (Item -> MIMEMessage)
                    	2.2 	    google?
                        3           feeds (atom/rss/..)
                        3.1         uwstopia
                        3.1.1       blog
Nodes::

	key          	parent   	kind 	node_id
	1
	1.3 						Web     
	1.5          	1 					/

	1.4.0.1 	 	1.4 		Group  	/usr/
	1.4.0.1.1 		1.4.0.1		"		/usr/1 or public@permascroll.appspot.com
	1.4.0.1.2 		1.4.0.1		"		/usr/2 or berend@dotmpe.com or berend.van.berkum@gmail.com
	1.4.0.2 	 	1.3 	  	Group 	http://yahoo.com/
	1.4.0.2.1 		1.4.0.2     User	http://del.icio.us/mpe
	1.4.0.3 	 	   			Group  	http://google.com/accounts/
	1.4.0.3.1 		1.4.0.1.1 	User	berend.van.berkum@gmail.com

	1.4.0.1.1.0.2.4       		BMFeed	http://del.icio.us/mpe/
	1.4.0.1.0.1  	1.4 		Item	/frontpage
	1.4.0.1.0.2  	 			Space 	/feed/
	1.4.0.1.0.2.1 						http://groups.yahoo.com/
	1.4.0.1.0.2.1.1 			ML 		http://tech.groups.yahoo.com/group/joecellfreeenergydevice/
	1.4.0.1.0.2.1.1 			 		http://tech.groups.yahoo.com/group/joecellfreeenergydevice/1234
	1.4.0.1.0.2.1.2 			ML		http://tech.groups.yahoo.com/group/teslasflyingmachine/
	1.4.0.1.0.2.2 				RSS 	/rss/
	1.4.0.1.0.2.2.1 			RSS 	http://


.. [*]_ so this cannot be a valid global tumbler address.

"""
from urllib import urlopen, urlencode # has no PUT?


url = 'http://permascroll.appspot.com/feed/'
url = 'http://localhost:8080/feed/'

data = [
	{ 'feed_id': 'http://dotmpe.com/blog/', 'apapter': 'RSS' },
	{ 'feed_id': 'http://delicious.com/mpe/', 'adapter': 'Delicious' }, # delicious does not number entries
	# mailinglists: large and posts may be delete but usually intact
	{ 'feed_id': 'http://tech.groups.yahoo.com/group/joecellfreeenergydevice/',
		'adapter': 'Mailinglist' },
	{ 'feed_id': 'http://tech.groups.yahoo.com/group/teslasflyingmachine/',
		'adapter': 'Mailinglist' },
	{ 'feed_id': 'http://everything2.org/node/'}, # not all nodes are still there
	{ 'feed_id': 'http://pastebin.ca/'}, # large! old stuff is regulary purged
	{ 'feed_id': 'http://snipplr.com/view/' }, # probably also large
	{ 'feed_id': 'http://fusionanomaly.net/', 'adapter': 'Site'}, # not a feed actually, just site of articles
	{ 'feed_id': 'http://uwstopia.com/blog/', 'apapter': 'RSS' },
]

for feed in data:
	# post
	fl = urlopen(url, urlencode(feed))
	print fl.read()
	print
	print feed, 'done'


