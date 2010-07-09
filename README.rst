Permascroll
===========
:created: 2010-01-01
:updated: 2010-07-10


For each publication there is a numbered channel or directory, for each entry 
therein a number. Each entry contains a measure of data. With an append-only 
policy, an immutable, permanent adress is kept for this data.\ [*]_

Once there, tumbler addressing becomes an prospect. With that, enfiladics and
Xanalogical structure may become interesting.

But for regular 'web' content, algorithms will be needed to include their content into such a system.

Adressing is done on discrete characters. (I've have no idea what that would mean for say, Japanese.)
For convenience, the unicode codec is used.
Encoding of math formulae and diagrams is not entirely clear.

Beside literal data, links could be made to image data. 
These too would by preference have virtual adressing (lets link or include portion x1,y1-x2,y2).
	

.. [*] Deleting content would be accomplished by blanking data on the virtual
       addresses.
	
Sources
-------
Mailinglists
	Entries have text only but often in either some quotable plain text standard or HTML. 
	Sometimes binaries may be present. 
	Not all lists may be available in an indexed form? 
Blogs and other sites with articles
	Many CMS's base their identification on the automatic record numbering in the relational database. 

But besides listing external content, creating new corpora is far more
interesting. 
Think of bookmarks, replies, quotes. 
Also usefulness in rote-learning, collecting knowledge, keeping journals, to-do or
shopping lists.

.. paradox, include all virtual positions in the current
.. trans:: 1.0.1~0.1

.. how would a client solve this?

.. best practice, virtual streams are taken from messages on individual basis.
.. We need to list and index all these messages, they should have a cool
   URI anyway. Even then, identify may be better expressed by URN?


Structure
---------
Feed
	- ``/feed/:index/entry/:index.html``
	- ``/feed/:index/entry/:index``

	Properties
		index
		label
		length

		created
		modified
		updated
	
Entry 
	- ``/feed/:index/entry/:index``
	- ``/feed/:index/entry/by-date/...``

	Properties
		index
		feed
		published
		updated
		length


URL Space
---------

- ``1`` my space
- ``1.1`` my bookmarks
- ``1.1.1`` my first bookmark
- ``1.2`` mailing lists 
- ``1.2.432`` some mailing list
- ``1.2.432.0.1.543`` some character in some mailing list?
- ``1.2.432.1`` first mailing list message
- ``1.2.432.1.0.1.1`` first character in that message

::

   <space>.0.<vaddr>

So the first component counts the permascrolls and the second the virtual positions. 
Since the space is strucutured hierarchically using tumbers it may be
ordered, but it could be difficult or unnecesary to construct virtual streams for the upper spaces. 
For example ``1.0.1~0.1`` addresses all virtual contents of the entire current space. 
Perhaps usefull in queries, but we will seldom dereference all of that and stream it to the client.


I don't know if this hierarchical, ordered interpretation is present in Xanadu
anywhere. Permascroll is, but I wonder what e.g. Xu88.1 can do for queries like
that. (Also for example link endsets in sets of documents.)::

  <node>.0.<account>.0.<document>.0.<vaddr>

- ``feed`` all feeds
- ``feed/4321/entry/5432`` database IDs for entry


