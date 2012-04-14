Permascroll
===========
:created: 2010-01-01
:updated: 2010-12-03


.. epigraph::

   For any medium has the power of imposing its own assumption on the unwary.
   Prediction and control consist in avoiding this subliminal state of Narcissus
   trance. But the greatest aid to this end is simply in knowing that the spell
   can occur immediately upon contact, as in the first bars of a melody.

   --Marshall McLuhan, Understanding Media


.. rubric:: This project describes a `permascroll` implementation for `Google App Engine`.

.. note:: 

   What follows is a short introduction that needs to be straightened
   out. Related experimental projects are mentioned and then components specific
   to this project are discussed.


- Let each publication be a set of symbols.
- Let each symbol node have *a size of 1*.

The interpretation of each node is left to the client?
XXX: or does permascrip incorporate muxdems?

- Let there additionally be *zero-width* nodes, 'virtual points' that only store a pointer to a range of symbols elsewhere. 
- Now a single link enables transclusion: virtual duplication and transpositioning of pieces of existing publications.
- Multi-way links enable a great deal of forms, overlaying structure on the sets of symbols.

The interpretation of these links again being left to the client.

This, at a minimum, is the essence of the Xanalogical system (of hypertext, hyperstructure) that Ted Nelson describes.

The goal is to support an Xanalogical addressing space. 

The end objective is an Xanalogical Edit Decision format/protocol that overlays
or can be incorporated into Web (WWW, as in HTTP/(X)HTML) applications.

PS and other projects
---------------------
- permascroll supports permanent addressing of content
- gate supports HTTP entity handling and messaging
- scrow supports format (de)muxing, and generic document session handling.
- translit is an Open Source transliterature demonstration, above projects may
  want to be compatible.

Technicalities
--------------
1. The first requirement is a permanent address space. 
2. The second a set of meaningful or useful rules for linking. 

The first implies a choice of encoding.
The easy way is to shout 'unicode!' and have a solution to map many known scripts to and from a multibyte encoding. 
But ofcourse then there's are various other forms of publication, 
many of which (hopefully) have new, non-sequential presentations to contrast
with the perception of media as being linear.

Secondly, only if a client knows the document structure is it going to handle 
that structure in any specific, non-generic way. This is a part that is going to
hinge more on convention.

Overview
--------
A publication consists of data and links.

There may be different types of data, with different types of address spaces.

Addresses start with three components in the form of local tumbler addresses,
one for the identity of the host, one for the owner, 
and one for the publication itself. These threes are organized in several HTTP
access points, such as:

- /node/1.1/1.2/5.3.1

This identifies a publication, a container for content.
The first digit of the first tumbler is the ur-digit, it indicates the
docuverse. 

Each node may be given a title to use for convenience as label in outlining.
But only the last node holds links to content. 

Content can be deleted, but nodes cannot. 
Each node has an append-only policy.
This means at any time the entire docuverse has a certain width,
but since this width is expressed in a difference tumbler, the exact number of
virtual positions will not be recorded in this tree.

The tumbler-component approach gives a node-address two forms of hierarchical relationship. 
One is intrinsical to tumblers: each component has sub-address lies in between parent + 1.
The other is the linking of several addresses as components of a larger address in a hierarchical way.

Each node has a width that is a count of the sub-nodes its links to.
Each node as a length of positions that is a count of is 

These tumbler adresses are local, meaning they are not in any way distributed.

TODO: implement Entry to link to append-only unicode literal and link space.

Development
------------
GIT branches
    master 
        Main development through 2010, 2011.


HTTP service
------------

Node
______________________________________________________________________________

**node** is the main structural resource, it organizes metadata to describe
the tumbler tree and what is at its leafs.
Tumblers are organized into addresses of 3 components, plus one component for
the virtual streams.

Allows application/x-www-form-urlencoded posts to add and update nodes.

The metadata indicates the number of subdigits called positions, and
subcomponents called sub-adresses.

/node/*
  :mediatype: application/x-mpe-permascroll
  :access: anonymous, group, user or sysadmin
  :allow: GET, POST
  :POST: depends on POST entity. Without 'update' key, create new node by incrementing position below tumbler,
    and return new node description. With 'update' key, replaces node properties
    where possible with values from POST entity, but only if update key matches
    entity tag. (both are typical for /node/).  XXX: could also allow POSTing to
    /node/ (without address) but with update/ETag key?
  :GET: 
  :params: 
    --update
    --title  The title of the node.

/node/[0-9]+
  :type: Docuverse
  :access: sysadmin
  :POST: increment tumbler, create Docuverse and return node description (\*typical)
  :GET: ::

    $ curl http://permascroll.appspot.com/node/1 -F title="My Docuverse" 
    [My Docuverse, with 0 positions at 1.1, and 0 sub-adresses]

/node/1.1
  :type: Node
  :access: sysadmin

/node/1.1/1
  :type: Directory
  :access: group or user

  ::

    $ curl http://permascroll.appspot.com/node/1.1/ -F title="My directory" 
    [My Directory, with 0 positions at 1.1.0.1, and 0 sub-adresses]

/node/1.1/1/1
  :type: Entry
  :params:
    --data  Literal string to use as content.

  ::

    $ curl http://permascroll.appspot.com/node/1.1/1/1.1 -X POST
    [Untitled Entry, with 0 positions at 1.1.0.1.0.1, and 0 sub-adresses]

  Which is not very useful, but can be appropiate given a title and allows
  grouping of entry sequences. Normally, ``/upload/`` is used however for
  creating `Entry` nodes.

/node/1.1~0.1
  :type: Node/Directory/Entry query
  :GET: returns a list of node descriptions

Content
______________________________________________________________________________

The media type here should be adjusted to the content, but each will need a
muxdem implementation to and from any of the standardized content streams.

/content/1.1/1/1
  :type: Entry

/content/1.1/1/1/1
  :type: LiteralContent

  Character addresses. Valid range 1.1 - 1.n

/content/1.1/1/1/2
  :type: LinkContent

  Link addresses. Valid range 2.1 - 2.n

/content/1.1/1/1/3
  :type: Audio..

/content/1.1/1/1/4
  :type: Video..

Upload
______________________________________________________________________________

/upload/1.1/1/1/1
  :POST: accept and store content, increment tumbler, create Entry and 
    acknowledge new node if successful 

  ::

    $ curl http://permascroll.appspot.com/node/1.1/ -F title="My directory" 
    [My Directory, with 0 positions at 1.1.0.1, and 0 sub-adresses]

/content/1.1/1/1/1~0.1
  :GET: returns contents or range


PEDL
----
- PEL, PEDL: Permanent Edit Lists?
- PDEF: Permanent Edit Definition File?

This is an preliminary version of an import/export format for Permascroll data.

* Each entry consists of two extendable data spaces.

* Each file holds content/links for one or more entries.
* Each line is a comment, others are part of an PEDL statement.
* PEDL statements are strings, prefixed by a leader character sequence.
  By default the leader is '@'?
* The following expressions are recognized, statements starting with:

  content
    the following arguments are HEREDOC strings, and/or location
    indicators for external content.

    The ``at`` keyword may indicate the intended location of the content,
    and may serve to make the insert conditional.
    If the given location is not available, the statement fails.
    
  link
    The expression consists a keyword from ``type, from, to`` and ``at``,
    follewed by one or more location indicators.

    The keywords may appear in any sequence,
    and indicate the part of the link the locator belongs to.
    ``type`` is a special part, that recognizes built-in locators.

    The ``at`` keyword works the same for links as it does for contents.

    This is the default statement, meaning any leader without subsequent statement keyword is interpreted as a link.

  prefix/bind
    bind address space to a prefix using the ``at`` keyword.

* Contents are loaded from locator, or given in HEREDOC style multiline strings.
* Locators come in URL form, in tumbler address or span form or in
  a regular expression/search-string form?
* Tumbler locators may be abbreviated by binding an address to a prefix.

  - This prefix-notation borrows some from Notation3.
  - A prefix is a ID followed by ':'.
  - The ':' prefix is by default bound to the current document (the entry node),
    any tumbler following it addresses a dataspace/virtual stream of that node.

    Content by default is inserted into that node.

* The type part of a link usually refers to another link that provides an
  discription of a class of links.

* The Permascroll Link document describes the built-in link types.
  The root of all link types is 'type', the first linkdoc link at
  ``1.1.0.1.0.2.0.2.1`` or ``linkdoc:type``.

  Type is built-in and at that address whatever the linkdoc says.

* New link-types are made by linking from :type to any new description.  

  The text in the to set should be a single word and will be converted to 
  link type ID. 
  The link should only contain these parts.

Protocol Layering
__________________
* The PEDF receiver is bound to a document.
  There is a generic receiver and a per-entry receiver.


----

For each publication there is a numbered directory, with
a numbered entry. Each entry links to a measure of data. Having an append-only 
policy, an immutable, permanent adress is kept for this data.\ [*]_

These numbers form the components of an address, one for each node or virtual location.
The key point is permanent addressing, thus enabling reuse of content by other systems.
A permascroll realizes this by an append-only policy. 

This may enable use of some xanalogical constructs, but there are no enfiladics
involved. In a Xanalogical system, linked trees perform a mapping of virtual
addresses to possibly highly rearranged source data. And in addition enable 
transclusion and effecient link or endset queries.

For the Web however, proxies may be convenient to rewrite content for use in such a system.
Using EDL and the Transliterature algorithms, Web content can be annotated.
Changes in the source will invalidate any referring EDL, only manual annotation
can track for versions--Docuspheres as submarines on the web.

Adressing is done for discrete characters, and Xanalogical links. 
These are stored in virtual space 1 and 2, resp.
Encoding of math formulae and diagrams is not entirely clear.
Beside literal data, other multimedia data could be adressed.

.. Nodes, Directories and Entries server as a curious, tumbler-addressed
   phenomenon in the address. These really imply some distributed network
   addressing scheme. 

   Why, a permascroll node might only serve virtual spaces, 
   as if the local filesystem. 

Details
-------
Tumblers allow hierarchical structures. 

The docuverse starts at 1, and remains 1?
There is no registry for (distributed) docuverses.
1.1 is the first address in the docuverse. 

To address each directory, entry, and virtual position, an address with multiple
components is needed.::

  <node> <directory> <entry> <virtual .. >

Each address is stored as a node, having one super- and a number of sub-nodes,
and any number of leafs or sub-components.

Xu88.1 span notation applies. Ie. 1~0.1 corresponds to range 1 to 1+1.
(0-prefixed tumblers denote offset for preceding address, Xu88.1 notation)

Any number of virtual component types may be supported, by specific 
Directory and Entry types?

.. [*] Deleting content could be accomplished by blanking data on the virtual
       addresses (with the propert effect of serving blanks, storage could be truncated). 
       
       A host should probably ignore address ranges, ie. serve everything under its own
       Node address and only certain, cached or proxied, address ranges for 
       other nodes. 

Virtual streams
---------------
Literal content has a simple virtual address range: ``1.0.1~0.1``.

Links shall need to be kept, space 2. Links have no size.
Images need an 2D address beneath 3. ``3.0.x-pixels.0.y-pixels``..

Uses datastore for unicode entries.
Uses blobstore for large unicode, and image entries.

At each moment, a v-stream has a total width, or length, which is the result of
its total occumulated content. Thus **an entry has one or more lengths**, one for each
of its content streams (3, hardcoded?).

Since in permascroll an entry cannot change, its length and thus its address
space is fixed. 
(Entry's may always be inserted in a Channel, though this operation is not
entirly clear yet and the normal mode would be to append entries to an directory)

Sources
-------
Mailinglists
	Entries have text only but often in either some quotable plain text standard or HTML. Prime example of quotation in daily usage.
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
- ``1.2.432.0.1.0.1.0.1`` first character in that message



