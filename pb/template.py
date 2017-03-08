# -*- coding: utf-8 -*-
"""
    template
    ~~~~~~~~

    adds template context processors

    :copyright: Copyright (C) 2016 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""


from flask import current_app


def inject_cdn():
    cdn_prefix = current_app.config.get('CDN_PREFIX', '')
    return dict(cdn_prefix=cdn_prefix)


def inject_style():
    return dict(style='default')


def init_template(app):
    app.context_processor(inject_cdn)
    app.context_processor(inject_style)
