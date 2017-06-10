Packaging
---------

**Arch Linux**

``pb-git`` is available in the `AUR
<https://aur.archlinux.org/packages/pb-git>`_. This package provides
``pb.service`` which starts a uwsgi server on port ``8080`` by
default.

.. code:: console

    $ cower -d pb-git
    $ cd pb-git
    $ makepkg -si

Next, start ``pb`` with:

.. code:: console

    # systemctl start pb

You can play with pb's uwsgi configuration in ``/etc/uwsgi/pb.ini``.
