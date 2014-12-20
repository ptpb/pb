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
- mysqld >= 5.5
- varnish >= 4.0 (optional)
- gunicorn >= 19.1 (optional, or `any other WSGI server <http://wsgi.readthedocs.org/en/latest/servers.html>`_)

Deployment
----------

This assumes you have at least a working ``python`` and ``mysqld`` with
versions strictly matching the the above. Consult your distribution's
documentation on how to do that.

Start by `cloning <http://git-scm.com/docs/git-clone>`_ ``pb``:

.. code:: console

    $ git clone https://github.com/silverp1/pb.git

You should then proceed to `create a database
<https://dev.mysql.com/doc/refman/5.5/en/create-database.html>`_ and
optionally `database user
<https://dev.mysql.com/doc/refman/5.5/en/adding-users.html>`_ for
``pb``:

.. code:: console

    $ mysql -u root <<EOF
    CREATE USER 'pb'@'localhost' IDENTIFIED BY 'green socks and sharp knives';
    CREATE DATABASE pb;
    GRANT ALL PRIVILEGES ON pb.* to 'pb'@'localhost';
    FLUSH PRIVILEGES;
    EOF

The schema also needs to be present:

.. code:: console

    $ mysql -u root pb < pb/schema.sql

Next, copy ``pb/config.yaml.example`` to ``~/.config/pb/config.yaml``, and
edit it appropriately. If you've followed the above steps exactly, its
contents should look something like:

.. code:: yaml

    DEBUG: true

    MYSQL:
      user: pb
      password: green socks and sharp knives
      database: pb

A ``pb`` development `environment
<https://virtualenv.pypa.io/en/latest/virtualenv.html#usage>`_ could
be created with something like:

.. code:: console

    $ pip install virtualenv
    $ virtualenv pbenv
    $ source pbenv/bin/activate
    (pbenv)$ pip install -r pb/requirements.txt

You can then start a ``pb`` instance via werkzeug's built-in `WSGI
server <http://werkzeug.pocoo.org/docs/0.9/serving/>`_.

.. code:: console

    (pbenv)$ (cd pb; ./run.py)

