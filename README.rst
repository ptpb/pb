==
pb
==

.. image:: https://img.shields.io/circleci/project/github/ptpb/pb.svg
   :target: https://circleci.com/gh/ptpb/pb

.. image:: https://img.shields.io/codecov/c/github/ptpb/pb.svg
   :target: https://codecov.io/gh/ptpb/pb

.. image:: https://img.shields.io/docker/automated/ptpb/pb.svg
   :target: https://hub.docker.com/r/ptpb/pb

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

pb comes with a ``Dockerfile`` and ``docker-compose.yaml`` to start development
environments easily. Refer to relevant documentation for how to install ``docker``
and ``docker-compose``.

start pb with::

  docker-compose up

pb will be listening on ``http://localhost:10002``

Deployment
----------

ptpb.pw (the reference deployment) uses `ptpb-deploy
<https://github.com/ptpb/ptpb-deploy>`_, which includes TLS termination,
automatic x509 certificate rotation, and response caching.

For a simpler deployment, the included ``Dockerfile`` and
``docker-compose.yaml`` can be used verbatim, and are easy to read/study.

Other best practices include:

- not using a shared/system python, when this is shared with packages other than pb

  - using site-packages is fine/preferred inside a container or isolated
    filesystem, otherwise use `venv
    <https://docs.python.org/3/library/venv.html>`_

  - if you need/want a version of python other than what your distribution
    packages, `pyenv <https://github.com/pyenv/pyenv>`_ is a good option

- not using debian or centos

  - these provide severely outdated packages, and require additional work to
    compensate for this
