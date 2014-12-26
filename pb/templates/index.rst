====
ptpb
====

ptpb is a lightweight pastebin (and url shortener) built using flask.

contents
--------

.. contents:: \

abstract
--------

Create a new paste from the output of ``cmd``:

.. code:: sh

    cmd | curl -F c=@- https://ptpb.pw

A  `HTML form </f>`_  is also provided for convenience paste and file-uploads
from web browsers.

terminology
-----------

id
^^

One of:

- a four character base66 paste id
- a four character base66 paste id, followed by a period-delimiter and a
  mimetype extension
- a 40 character sha1 hexdigest
- a 40 character sha1 hexdigest, followed by a period-delimiter and a
  mimetype extension
- a three character base66 url redirect id

A mimetype extension, when specified, is first matched with a matching mimetype
known to the system, then returned in the HTTP response headers.

lexer
^^^^^

A 'lexer' is an alias of a pygments lexer; used for syntax highlighting.

uuid
^^^^

The string representation of a RFC 4122 UUID. These are used as a weak form of
'shared secret' that, if known, allow the user to modify the pastes.

handler
^^^^^^^

A one-character handler identifier.

handlers
--------

r
^

**render**: This expects reStructuredText in the paste content and gives HTML
output.

routes
------

``GET /<id>``
^^^^^^^^^^^^^

Retrieves paste or url redirect.

If a paste: returns the matching paste, verbatim and unmolested.

If a url redirect: returns HTTP code 301 with the location of the redirect.

``GET /<id>/<lexer>``
^^^^^^^^^^^^^^^^^^^^^

Like the above, but decodes and applies syntax highlighting to pastes via
HTML/CSS.

Line numbering and fragments are included, and can be used to link to
individual lines within the paste.

``GET /<handler>/<id>``
^^^^^^^^^^^^^^^^^^^^^^^

Like the above, but paste content is mangled by said handler before being
returned.

``POST /``
^^^^^^^^^^

Creates a new paste; returns GET URL and secret UUID.

Only multipart/form-data is supported; other content types are not tested.

At least one 'name' disposition extension parameter must be present, and its
value must be 'c'.

If the 'p' form parameter exists and its value evaluates to true, the paste
will be a private paste where the paste can only be retrieved by knowledge of
its sha1 hexdigest.

Unless the 'filename' disposition extension parameter is specified, the form
data is decoded. The value of the 'filename' parameter is split by
period-delimited extension, and appended to the location in the response.

``PUT /<uuid>``
^^^^^^^^^^^^^^^

Replaces the content of the paste that matches the provided UUID.

Form submission is otherwise identical to ``POST``.

``DELETE /<uuid>``
^^^^^^^^^^^^^^^^^^

Deletes the paste that matches the provided UUID.

``POST /u``
^^^^^^^^^^^

Creates a new url redirect (short url).

The form content will be decoded, and truncated at the first newline or EOF,
whichever comes first. The result of that is then returned in a HTTP 301
response with the form content in the Location header.

``GET /f``
^^^^^^^^^^

Returns `HTML form </f>`_ that can be used for in-browser paste creation and
file uploads.

``GET /s``
^^^^^^^^^^

Returns `paste statistics </s>`_; currently paste count and total size.

``GET /l``
^^^^^^^^^^

Returns `available lexers </l>`_, newline-delimited, with space-delimited
aliases.

examples
--------

No really, how in the name of Gandalf's beard does this actually work? Show me!

normal paste
^^^^^^^^^^^^

Create a paste from the output of 'dmesg':

.. code:: console

    $ dmesg | curl -F c=@- https://ptpb.pw
    https://ptpb.pw/QQQP
    uuid: 17c5829d-81a0-4eb6-8681-ba72f83ffbf3

updating pastes
^^^^^^^^^^^^^^^

Take that paste, and replace it with a picture of a baby skunk:

.. code:: console

    $ curl -X PUT -F c=@- https://ptpb.pw/17c5829d-81a0-4eb6-8681-ba72f83ffbf3 < baby-skunk.jpg
    https://ptpb.pw/QQQP updated.

using mimetypes
^^^^^^^^^^^^^^^

Append '.jpg' to hint at browsers that they should probably display a jpeg
image:

::

    https://ptpb.pw/QQQP.jpg

deleting pastes
^^^^^^^^^^^^^^^

Actually, that picture is already on imgur; let's delete that paste and make a
shorturl instead:

.. code:: console

    $ curl -X DELETE https://ptpb.pw/17c5829d-81a0-4eb6-8681-ba72f83ffbf3
    https://ptpb.pw/QQQP deleted.

shortening URLs
^^^^^^^^^^^^^^^

.. code:: console

    $ curl -F c=@- https://ptpb.pw/u <<< https://i.imgur.com/CT7DWCA.jpg
    https://ptpb.pw/QQ0

Well, it *is*  shorter..

syntax highlighting
^^^^^^^^^^^^^^^^^^^

Put my latest 'hax.py' script on ptpb:

.. code:: console

    $ curl -F c=@- https://ptpb.pw < hax.py
    https://ptpb.pw/QQx8
    uuid: [redacted]

Now I want to syntax highlight and draw attention to one particular
line:

::

    https://ptpb.pw/QQQ_/py#L-7

private pastes
^^^^^^^^^^^^^^

Perhaps we have some super sekrit thing that we don't want be be guessable by
base66 id:

.. code:: console

    $ curl -F c=@- -F p=1 https://ptpb.pw < SEKRIT_hax.py
    url: http://localhost:10002/1c5dd062b6a3359cf60989d0e1c8746944608304
    uuid: e5860f7a-b074-4e5d-88d4-747cfacc1fcd

shell functions
---------------

Like it? Here's some convenience shell functions:

.. code:: bash

    pb () { curl -F "c=@${1:--}" https://ptpb.pw }

This uploads paste content stdin unless an argument is provided, otherwise
uploading the specified file.

Now just:

.. code:: console

    $ command | pb
    $ pb filename

A slightly more elaborate variant:

.. code:: bash

   pbx () { curl -sF "c=@${1:--}" -w "%{redirect_url}" https://ptpb.pw -o /dev/stderr | xsel -l /dev/null -b }

This uses xsel to set the ``CLIPBOARD`` selection with the url of the uploaded
paste for immediate regurgitation elsewhere.

authors
-------

`Joe Pettit <https://github.com/silverp1>`_

`Zack Buhman <https://buhman.org>`_

duck sauce
----------

`https://github.com/silverp1/pb <https://github.com/silverp1/pb>`_
