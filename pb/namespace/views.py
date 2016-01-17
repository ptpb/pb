# -*- coding: utf-8 -*-
"""
    namespace.views
    ~~~~~~~~~~~~~~~

    namespace url routes and views

    :copyright: Copyright (C) 2015 by the respective authors; see AUTHORS.
    :license: GPLv3, see LICENSE for details.
"""

from flask import Blueprint
from pymongo.errors import DuplicateKeyError

from pb.namespace import model
from pb.responses import NamespaceResponse, StatusResponse

namespace = Blueprint('namespace', __name__)

@namespace.route('/n/<string:namespace>')
def get(namespace):
    cur = model.get(namespace)

    try:
        namespace = next(cur)
    except StopIteration:
        return StatusResponse('not found', code=404)

    return NamespaceResponse(namespace, 'exists', code=200)

@namespace.route('/n/<string:namespace>', methods=['POST'])
def post(namespace):
    try:
        namespace = model.create(namespace)
    except DuplicateKeyError:
        return StatusResponse('duplicate', code=409)

    return NamespaceResponse(namespace, 'created', code=201)
