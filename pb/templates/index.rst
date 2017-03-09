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

namespaces
^^^^^^^^^^

.. warning:: This feature is considered highly experimental, and its API/semantics changed in subtle but signtificant ways in the future

First you'll need a DNS name that points to the pb instance you want
to use namespaces with.

Start by creating a new namespace:

.. code:: console

    $ curl -X POST {{ url('namespace.post', namespace='buh.io') }}
    name: buh.io
    status: created
    uuid: 326117ad-2969-4a0a-a3d7-04eef09127ab

With the namespace uuid, you can modify any paste in that
namespace. Namespace pastes are a little different in that they are
always referenced by label; while ``sids`` and ``uuids`` exist
internally, no route can access namespace'ed pastes that way.

You authorized yourself via the ``X-Namespace-Auth`` header:

.. code:: console

    $ auth=326117ad-2969-4a0a-a3d7-04eef09127ab
    $ curl -H "X-Namespace-Auth: $auth" -F c=@- https://buh.io/foo <<< loltrain
    date: 2016-01-17 02:52:29.179089
    digest: 7bcbab9cb9dbf26c5cdbf02e1f67f93fdb6237ea
    label: foo
    namespace: buh.io
    status: created
    url: http://buh.io/foo
    uuid: 5f9dc40c-35df-4298-977c-6baeeb56bed1

You'll notice we access the namespace via its DNS name instead of the
'real' pb domain name. This is what internally allows you to use the
special ``namespace`` labels, which have relaxed restrictions: they
can be any length (including zero-length), and don't need to start
with a tilde.

``DELETE`` and ``PUT`` work as usual, except you reference the paste
via namespace+label instead of uuid.

shell functions
---------------

Like it? Here's some convenience shell functions:

.. code:: bash

    pb () {
      curl -F "c=@${1:--}" {{ url('.post') }}
    }

This uploads paste content stdin unless an argument is provided,
otherwise uploading the specified file.

Now just:

.. code:: console

    $ command | pb
    $ pb filename

A slightly more elaborate variant:

.. code:: bash

    pbx () {
      curl -sF "c=@${1:--}" -w "%{redirect_url}" '{{ url('.post', r=1) }}' -o /dev/stderr | xsel -l /dev/null -b
    }

This uses xsel to set the ``CLIPBOARD`` selection with the url of the
uploaded paste for immediate regurgitation elsewhere.

How about uploading a screenshot then throwing the URL in your
clipboard?

.. code:: bash

    pbs () {
      gm import -window ${1:-root} /tmp/$$.png
      pbx /tmp/$$.png
    }

Now you can:

.. code:: console

    $ pbs
    $ pbs 0

The second command would allow you to select an individual window
while the first uses the root window.

Perhaps we'd like to do the terminal recording with a single command.

.. code:: bash

    pbs () {
      asciinema rec /tmp/$$.json
      pbx /tmp/$$.json
    }

View the recording by prepending a ``t/`` to the paste id.

native clients
--------------

There are some native clients for interacting with pb, below are the ones we know of:

- `pbpst <https://github.com/HalosGhost/pbpst.git>`_
- `AndroPTPB <https://f-droid.org/repository/browse/?fdfilter=pb&fdid=io.github.phora.androptpb>`_

duck sauce
----------

`https://github.com/ptpb/pb <https://github.com/ptpb/pb>`_
