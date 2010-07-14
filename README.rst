Permascroll
===========
:created: 2010-01-01
:updated: 2010-07-11


For each publication there is a numbered channel or directory, with
a numbered entry. Each entry contains a measure of data. Having an append-only 
policy, an immutable, permanent adress is kept for this data.\ [*]_

Tumbler addressing becomes a prospect. 
The key point is permanent addressing, thus enabling reuse of content by other
systems.
With that, enfiladics and Xanalogical structure may become interesting.

But for regular 'web' content, algorithms will be needed to include their content into such a system.

Adressing is done on discrete characters.
Encoding of math formulae and diagrams is not entirely clear.
Beside literal data, other multimedia data could be adressed.

Tumblers allow hierarchical structures. 

The docuverse starts at 1, and remains 1.
There is no registry for (distributed) docuverses.

1.1 is the first address in the docuverse. 
To address each channel, entry, and virtual position, an address with multiple
components is needed.

Starting bottom-up, there is a specific entry type with its own address.
Beneath it are the virtual address spaces within the content.
The entry itself has a certain position in a container, a container specific to
the type of the entries. In turn, for specific container types it is possible to
have different entry address, ie. parallel streams.
This container is then grouped under a generic node.

Which gives::

  <node> <directory> <entry> <virtual .. >

Each address is stored as a node, having one super- and a number of sub-nodes.


.. [*] Deleting content could be accomplished by blanking data on the virtual
       addresses (with the propert effect of serving blanks, storage could be truncated). 
       
       Also a host may ignore address ranges, ie. need not to store everything. 
       Distributed dereferencing of tumblers is left out of consideration here.

Literal content
---------------
Has a simple virtual address range: ``1~0.1``.
(0-prefixed tumblers denote offset for preceding address, Xu88.1 notation)

Uses datastore for unicode entries.
Uses blobstore for large unicode, and image entries.

Sources
-------
Mailinglists
	Entries have text only but often in either some quotable plain text standard or HTML. 
	Sometimes binaries may be present. 
	Not all lists may be available in an indexed form? 
Blogs and other sites with articles
	Many CMS's base their identification on the automatic record numbering in the relational database. 

But besides listing external content, creating new corpora is far more interesting. 
Think of bookmarks, replies, quotes. 
Having permanent adresses: inclusion and edition of previous entries--see Transclusion.
Also usefulness in rote-learning, collecting knowledge, keeping journals, to-do or
shopping lists.

..
  .. paradox, include all virtual positions in the docuverse
  .. trans:: 1~0.1



HTTP API
---------

Node 
   - tumbler
   - base
   - length
   - label  

ScrollNode
    
EntryNode
   - blob id
   - digests  
   - size
   - type  

   char-length
   pixel-size
   audio-sampling-rate
   video-size-duration
    

- ``1`` first docuverse
- ``1.1`` first scroll (ie. my bookmarks)
- ``1.1.0.1`` my first bookmark (three space node type)
  ``1.1.0.1.0.1~0.23`` title
  ``1.1.0.1.0.2~0.41`` descr
  ``1.1.0.1.0.3~0.5`` tags (reference nodes?)
- ``1.2`` mailing lists 
- ``1.2.432`` some mailing list
- ``1.2.432.0.1.0.1.543`` some character in some mailing list?
- ``1.2.432.0.1`` first mailing list message
- ``1.2.432.0.1.0.1.1`` first character in that message

::

   <space>.0.<item>.0.<content>

So the first component counts the permascrolls and the second the items, and
the third the virtual positions. 
Since the space is strucutured hierarchically using tumbers it may be
ordered, but it could be difficult or unnecesary to construct virtual streams for the 
upper spaces. 
For example ``1.0.1~0.1`` addresses all virtual contents of the entire current space. 
Perhaps usefull in queries, but we will seldom dereference all of that and stream it 
to the client.


I don't know if this hierarchical, ordered interpretation is present in Xanadu
anywhere. Permascroll is, but I wonder what e.g. Xu88.1 can do for queries like
that. (Also for example link endsets in sets of documents.)::

  <node>.0.<account>.0.<document>.0.<vaddr>

- ``feed`` all feeds
- ``feed/4321/entry/5432`` database IDs for entry


