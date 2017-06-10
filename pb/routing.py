from flask.ctx import RequestContext as BaseRequestContext
from werkzeug import routing
from werkzeug.exceptions import HTTPException
from werkzeug.routing import MapAdapter as BaseMapAdapter
from werkzeug.routing import Rule as BaseRule
from werkzeug.routing import (MethodNotAllowed, NotFound, RequestAliasRedirect,
                              RequestRedirect, RequestSlash)

from pb.config import config
from pb.util import get_host_name


class Rule(BaseRule):
    def __init__(self, *args, namespace_only=False, **kwargs):
        self.namespace_only = namespace_only

        super().__init__(*args, **kwargs)

    def match(self, path, request):
        if not self.namespace_only:
            return super().match(path)

        default = config.get('DEFAULT_NAMESPACE')
        host = get_host_name(request)

        if default and host != default:
            return super().match(path)

    def match_compare_key(self):
        return not bool(self.namespace_only), bool(self.arguments), -len(self._weights), self._weights


class RequestContext(BaseRequestContext):
    def match_request(self):
        try:
            url_rule, self.request.view_args = \
                self.url_adapter.match(return_rule=True,
                                       request=self.request)
            self.request.url_rule = url_rule
        except HTTPException as e:
            self.request.routing_exception = e


# welp, time to write my own framework
class MapAdapter(BaseMapAdapter):
    def match(self, path_info=None, method=None, return_rule=False,
              query_args=None, request=None):
        self.map.update()
        if path_info is None:
            path_info = self.path_info
        else:
            path_info = to_unicode(path_info, self.map.charset)
        if query_args is None:
            query_args = self.query_args
        method = (method or self.default_method).upper()

        path = u'%s|%s' % (
            self.map.host_matching and self.server_name or self.subdomain,
            path_info and '/%s' % path_info.lstrip('/')
        )

        have_match_for = set()
        for rule in self.map._rules:
            try:
                rv = rule.match(path, request)
            except RequestSlash:
                raise RequestRedirect(self.make_redirect_url(
                    url_quote(path_info, self.map.charset,
                              safe='/:|+') + '/', query_args))
            except RequestAliasRedirect as e:
                raise RequestRedirect(self.make_alias_redirect_url(
                    path, rule.endpoint, e.matched_values, method, query_args))
            if rv is None:
                continue
            if rule.methods is not None and method not in rule.methods:
                have_match_for.update(rule.methods)
                continue

            if self.map.redirect_defaults:
                redirect_url = self.get_default_redirect(rule, method, rv,
                                                         query_args)
                if redirect_url is not None:
                    raise RequestRedirect(redirect_url)

            if return_rule:
                return rule, rv
            else:
                return rule.endpoint, rv

        if have_match_for:
            raise MethodNotAllowed(valid_methods=list(have_match_for))
        raise NotFound()


routing.MapAdapter = MapAdapter
