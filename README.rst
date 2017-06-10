==
pb
==

.. image:: https://img.shields.io/circleci/project/github/ptpb/pb.svg
   :target: https://circleci.com/gh/ptpb/pb

.. image:: https://img.shields.io/codecov/c/github/ptpb/pb.svg
   :target: https://codecov.io/gh/ptpb/pb

Overview
--------

``pb`` is a lightweight pastebin and url shortener built using
`flask <http://flask.pocoo.org/>`_.

The official instance of ``pb`` can be found at `ptpb.pw
<https://ptpb.pw/>`_. Feel free deploy ``pb`` elsewhere.

Features
--------

 * full paste and short-url CRUD
 * private pastes
 * tweakable syntax highlighting
 * terminal recording playback
 * markup rendering

Development
-----------

pb comes with a ``Dockerfile`` and ``docker-compose.yml`` to start development
environments easily. Refer to relevant documentation for how to install ``docker``
and ``docker-compose``.

start pb with::

  docker-compose up

pb will be listening on ``http://localhost:10002``
