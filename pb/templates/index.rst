==
pb
==

pb is a lightweight pastebin (and url shortener) built using flask.

contents
--------

.. contents:: \

abstract
--------

Create a new paste from the output of ``cmd``:

.. code:: sh

    cmd | curl -F c=@- {{ url('.post') }}

A `HTML form </f>`_ is also provided for convenience paste and
file-uploads from web browsers.

The `pb_cli <https://github.com/ptpb/pb_cli>`_ is also available for maximum
convenience pastes from your terminal.

api spec
--------

Implementers can read the complete API specification `here <https://ptpb.pw/a>`_.

examples
--------

No really, how in the name of Gandalf's beard does this actually work?
Show me!

creating pastes
^^^^^^^^^^^^^^^

Create a paste from the output of 'dmesg':

.. code:: console

    $ dmesg | curl -F c=@- {{ url('.post') }}
    long: AGhkV6JANmmQRVssSUzFWa_0VNyq
    sha1: 686457a240366990455b2c494cc559aff454dcaa
    short: VNyq
    url: {{ url('.get', label='VNyq') }}
    uuid: 17c5829d-81a0-4eb6-8681-ba72f83ffbf3

Or, if you only care about getting the url back:

.. code:: console

    $ dmesg | curl -F c=@- {{ url('.post') }}?u=1
    {{ url('.get', label='VNyq') }}

updating pastes
^^^^^^^^^^^^^^^

Take that paste, and replace it with a picture of a baby skunk:

.. code:: console

    $ curl -X PUT -F c=@- {{ url('.put', uuid='17c5829d-81a0-4eb6-8681-ba72f83ffbf3') }} < baby-skunk.jpg
    {{ url('.get', label='ullp') }} updated.

using mimetypes
^^^^^^^^^^^^^^^

Append '.jpg' to hint at browsers that they should probably display a
jpeg image:

.. code:: text

    {{ url('.get', label='ullp.jpg') }}

deleting pastes
^^^^^^^^^^^^^^^

Actually, that picture is already on imgur; let's delete that paste
and make a shorturl instead:

.. code:: console

    $ curl -X DELETE {{ url('.delete', uuid='17c5829d-81a0-4eb6-8681-ba72f83ffbf3') }}
    {{ url('.get', label='ullp') }} deleted.

shortening URLs
^^^^^^^^^^^^^^^

.. code:: console

    $ curl -F c=@- {{ url('.url') }} <<< https://i.imgur.com/CT7DWCA.jpg
    {{ url('.get', label='qYTr') }}

Well, it *is*  shorter..

syntax highlighting
^^^^^^^^^^^^^^^^^^^

Put my latest 'hax.py' script on pb:

.. code:: console

    $ curl -F c=@- {{ url('.post') }} < hax.py
    long: AEnOPO7bF9Qyyt_WUltBlYWHs_-G
    sha1: 49ce3ceedb17d432cadfd6525b41958587b3ff86
    short: s_-G
    url: {{ url('.get', label='2AcJ') }}
    uuid: bfd41875-dcac-4b6b-92e9-97a55d4f8d89

Now I want to syntax highlight and draw attention to one particular
line:

.. code:: text

    {{ url('.get', label='2AcJ/py#L-7') }}

private pastes
^^^^^^^^^^^^^^

Perhaps we have some super sekrit thing that we don't want be be
guessable by base66 id:

.. code:: console

    $ curl -F c=@- -F p=1 {{ url('.post') }} < SEKRIT_hax.py
    long: ACCzjDcun9TqySwSUjy_yRpGxWIK
    sha1: 20b38c372e9fd4eac92c12523cbfc91a46c5620a
    short: xWIK
    url: {{ url('.get', label='ACCzjDcun9TqySwSUjy_yRpGxWIK') }}
    uuid: 876e09b5-09d4-454c-8570-b627af54abd1

vanity pastes
^^^^^^^^^^^^^

Witness the gloriousness:

.. code:: console

    $ curl -F c=@- {{ url('.post', label='~polyzen') }} <<< "boats and hoes"
    long: AEz1_jLk-awIvq73RxQq_n1aQ46a
    sha1: 4cf5fe32e4f9ac08beaef747142afe7d5a438e9a
    short: Q46a
    url: {{ url('.get', label='~polyzen') }}
    uuid: ab505051-0766-41dd-85d9-e739e62de58d
    $ curl {{ url('.get', label='~polyzen') }}
    boats and hoes

sunsetting pastes
^^^^^^^^^^^^^^^^^

Create a paste that self destructs in 2 minutes:

.. code:: console

    $ echo "This message will self-destruct in two minutes" | curl -F sunset=120 -F c=@- {{ url('.post') }}
    date: 2016-03-22T17:15:50.396279+00:00
    digest: 3a9c705adf9a941b175631a5e6f11eb575f067e6
    long: ADqccFrfmpQbF1YxpebxHrV18Gfm
    short: 8Gfm
    size: 46
    status: created
    sunset: 2016-03-22T17:17:50.395045+00:00
    url: {{ url('.get', label='8Gfm') }}
    uuid: 751f7e0b-7ce1-4b81-852b-57c5844e8d3a
    $ curl {{ url('.get', label='8Gfm') }}
    This message will self-destruct in two minutes
    $ sleep 2m
    $ curl {{ url('.get', label='8Gfm') }}
    date: 2016-03-22T17:15:50.396000+00:00
    digest: 3a9c705adf9a941b175631a5e6f11eb575f067e6
    long: ADqccFrfmpQbF1YxpebxHrV18Gfm
    short: 8Gfm
    size: 46
    status: expired
    sunset: 2016-03-22T17:17:50.395000+00:00
    url: {{ url('.get', label='8Gfm') }}

terminal recording
^^^^^^^^^^^^^^^^^^

Create and upload a recording using `asciinema <https://asciinema.org/docs/installation>`_:

.. code:: console

    $ asciinema rec term.json
    ~ Asciicast recording started.
    ~ Hit Ctrl-D or type "exit" to finish.
    $ echo tralalalala
    tralalalala
    $ exit
    ~ Asciicast recording finished.
    $ curl -F c=@term.json {{ url('.post') }}
    digest: f9704e9ae63bb5f5aad145a871f260557673d185
    long: APlwTprmO7X1qtFFqHHyYFV2c9GF
    short: c9GF
    status: created
    url: {{ url('.get', label='c9GF') }}
    uuid: 9dffb318-04f5-437c-9899-6e7c7eed04af

Then watch the playback with the ``t`` handler ({{ url('.get', label='c9GF', handler='t') }} in this case).


shell functions
---------------

Like it? Try the `pb_cli <https://github.com/ptpb/pb_cli>`_ for maximum
convenience:

.. code:: bash

    command | pb
    pb < /path/to/file


You could further extend this by creating more shell functions around it; here's
one for asciinema:

.. code:: bash

    pb_rec () {
      asciinema rec /tmp/$$.json
      pb < /tmp/$$.json
    }


native clients
--------------

There are some native clients for interacting with pb, below are the ones we know of:

- `ptpb/pb_cli <https://github.com/ptpb/pb_cli>`_
- `HalosGhost/pbpst <https://github.com/HalosGhost/pbpst.git>`_

duck sauce
----------

`https://github.com/ptpb/pb <https://github.com/ptpb/pb>`_
