# -*- coding: utf-8 -*-
"""
    cdn
    ~~~

    adds cdn prefix to template context

    :copyright: Copyright (C) 2016 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""


from flask import current_app


def inject_cdn():
    cdn_prefix = current_app.config.get('CDN_PREFIX', '')
    return dict(cdn_prefix=cdn_prefix)


def init_cdn(app):
    app.context_processor(inject_cdn)
