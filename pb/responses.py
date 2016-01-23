import yaml
import json
from uuid import UUID

from datetime import timedelta, datetime
from pytz import utc

from werkzeug.wrappers import Response
from werkzeug.http import parse_list_header
from flask import request, current_app

from pb.converters import SIDConverter
from pb.util import absolute_url

def json_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

def any_url(paste, filename=None):
    idu = lambda k,v: absolute_url('.get', **{k: (paste[v], filename)})
    if paste.get('namespace'):
        return idu('label', 'label')
    if paste.get('private'):
        return idu('sha1', 'digest')
    if paste.get('label'):
        return idu('label', 'label')
    return idu('sid', 'digest')

def redirect(location, rv, code=302, **kwargs):
    response = current_app.response_class(rv, code, **kwargs)
    response.headers['Location'] = location
    return response

class BaseResponse(Response):
    _etag = True
    default_mimetype = 'text/html'

class DictResponse(BaseResponse):
    def __init__(self, obj, *args, **kwargs):
        response = self._dump(obj)
        super().__init__(response, *args, **kwargs)
        self.headers['Vary'] = 'Accept'

    @property
    def default_mimetype(self):
        accept = parse_list_header(request.headers.get('Accept',''))
        if accept and 'application/json' in accept:
            return 'application/json'
        return 'text/plain' # yaml

    def _dump_json(obj):
        return json.dumps(obj, default=json_datetime)

    def _dump_yaml(obj):
        return yaml.safe_dump(obj, default_flow_style=False)

    def _dump(self, obj):
        return self._mimetypes[self.default_mimetype](obj)

    _mimetypes = {
        'application/json': _dump_json,
        'text/plain': _dump_yaml
    }

class StatusResponse(DictResponse):
    _etag = False

    def __init__(self, status, code=None, *args, **kwargs):
        obj = dict(
            status = status
        )
        super().__init__(obj, status=code, *args, **kwargs)

class NamespaceResponse(DictResponse):
    _etag = False

    def __init__(self, namespace, status, code=None, *args, **kwargs):
        uuid = str(UUID(hex=namespace['_id']))
        namespace.update(dict(
            uuid = uuid,
            status = status
        ))
        del namespace['_id']
        if status != 'created':
            del namespace['uuid']

        super().__init__(namespace, status=code, *args, **kwargs)

class PasteResponse(DictResponse):
    _etag = False
    _conv = SIDConverter

    def __init__(self, paste, status=None, filename=None, uuid=None, code=None):
        self._paste = paste
        paste['status'] = status # hack
        self.uuid = uuid
        self.url = any_url(paste, filename)

        code = code or (302 if request.args.get('r') else 200)
        super().__init__(dict(self), code)

        self.headers['Location'] = self.url

    def _dump(self, obj):
        if request.args.get('u'):
            return '{}\n'.format(self.url)
        return super()._dump(obj)

    def __dir__(self):
        return ['url', 'long', 'short',
                'uuid', 'status', 'label', 'sunset',
                'redirect', 'digest', 'namespace', 'date']

    def __getattr__(self, name):
        if name in dir(self):
            try:
                return self._paste[name]
            except KeyError:
                pass
        raise AttributeError

    def __iter__(self):
        for key in self.__dir__():
            value = getattr(self, key, None)
            if value != None:
                yield key, value

    def _sid(self, length):
        return self._conv.to_url(None, self._paste['digest'], length)

    @property
    def long(self):
        if 'namespace' not in self._paste:
            return self._sid(42)

    @property
    def short(self):
        if all(i not in self._paste for i in ['namespace', 'private']):
            return self._sid(6)

    @property
    def date(self):
        if 'date' in self._paste:
            return utc.localize(self._paste['date'])

    @property
    def sunset(self):
        if 'sunset' in self._paste:
            return utc.localize(self._paste['sunset'])
