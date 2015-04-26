==
pb
==

``pb`` is a lightweight pastebin (and url shortener) built using
`flask <http://flask.pocoo.org/docs/0.10/quickstart/>`_.

The official instance of ``pb`` can be found at `ptpb.pw
<https://ptpb.pw>`_. Feel free to deploy ``pb`` elsewhere.

Requirements
------------

- python >= 3.4 `requirements.txt <requirements.txt>`_
- mongodb >= 2.6
- varnish >= 4.0 (optional)
- gunicorn >= 19.1 (optional, or `any other WSGI server <http://wsgi.readthedocs.org/en/latest/servers.html>`_)

Deployment
----------

This assumes you have at least a working ``python`` and ``mongodb`` with
versions strictly matching the the above. Consult your distribution's
documentation on how to do that.

Start by `cloning <http://git-scm.com/docs/git-clone>`_ ``pb``:

.. code:: console

    $ git clone https://github.com/silverp1/pb.git --recursive

Next, copy ``pb/config.yaml.example`` to ``~/.config/pb/config.yaml``,
and edit it appropriately. For development, its configuration might
look something like:

.. code:: yaml

    DEBUG: true

    MONGO:
      host: localhost
      port: 27017

    MONGO_DATABASE: pb

You'll also need to build ``pbs``, which requires
``grunt-cli``:

.. code:: console

    # npm install -g grunt-cli
    $ npm install
    $ grunt

A ``pb`` development `environment
<https://virtualenv.pypa.io/en/latest/virtualenv.html#usage>`_ could
be created with something like:

.. code:: console

    $ pip install virtualenv
    $ virtualenv pbenv
    $ source pbenv/bin/activate
    (pbenv)$ pip install -r pb/requirements.txt

You should use ``runonce.py`` to create indexes before you run ``pb``
for the first time on a new database:

.. code:: console

    (pbenv)$ cd pb
    (pbenv)$ ./runonce.py

You can then start a ``pb`` instance via werkzeug's built-in `WSGI
server <http://werkzeug.pocoo.org/docs/0.9/serving/>`_.

.. code:: console

    (pbenv)$ ./run.py

Packaging
---------

**Arch Linux**

``pb-git`` is available in the `AUR
<https://aur.archlinux.org/packages/pb-git>`_. This package provides
``pb.service`` which starts a uwsgi server on port ``8080`` by
default.

For now this requires ``aur/python-flask-git``, until 1.0 is released
upstream:

.. code:: console

    $ cower -dd pb-git
    $ (cd python-flask-git && makepkg -si)
    $ (cd pb-git && makepkg -si)

Next, start ``pb`` with:

.. code:: console

    # systemctl start pb

You can play with pb's uwsgi configuration in ``/etc/uwsgi/pb.ini``.
