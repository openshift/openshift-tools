#!/usr/bin/env python2
# vim: expandtab:tabstop=4:shiftwidth=4


import requests
import json
from metricmanager import UniqueMetric
from metricmanager import MetricEncoder

class RestApi(object):
    """
    A base connection class to derive from.
    """
    proto = 'http'
    host = '127.0.0.1'
    port = 443
    username = None
    password = None
    token = None
    headers = None
    response = None
    base_uri = None
    verbose = False
    debug = False

    def __init__(self, host=None, port=443, username=username, password=password,
                token=None, debug=False, verbose=False, proto=None, headers=None):
        if proto is not None:
            self.proto = proto

        if host is not None:
            self.host = host

        if username:
            self.username = username

        if password:
            self.password = password

        if token:
            self.token = token

        if headers:
            self.headers = headers

        if verbose:
            self.verbose = verbose

        self.debug = debug
        self.base_uri = self.proto + "://" + host + "/"

    @property
    def _auth(self):
        #if self.token:
        #    return BearerAuth(self.token)

        #if self.username and self.password:
        #    return requests.auth.HTTPBasicAuth(self.username, self.password)
        return None

    def request(self, url, method, headers=None, params=None, data=None):
        """
        wrapper method for Requests' methods
        """
        if url.startswith("https://") or url.startswith("http://"):
            self.url = url  # self.base_uri + url
        else:
            self.url = self.base_uri + url
        #log.debug("URL: %s" % self.url)
        _headers = self.headers or {}
        if headers:
            _headers.update(headers)
        #if 'OPENSHIFT_REST_API' in os.environ:
        #    user_specified_api_version = os.environ['OPENSHIFT_REST_API']
        #    api_version = "application/json;version=%s" % user_specified_api_version

        #    _headers['Accept'] = api_version

        self.response = requests.request(
            auth=None if self._auth is None else self._auth,
            method=method, url=self.url, params=params, data=data,
            headers=_headers, timeout=130, verify=False
        )

        #try:
        #    raw_response = self.response.raw
        #except Exception as e:
        #    print("-"*80, file=sys.stderr)
        #    traceback.print_exc(file=sys.stderr)
        #    print("-"*80, file=sys.stderr)
        #    raise e

        self.data = self.response.json()
        # see https://github.com/kennethreitz/requests/blob/master/requests/status_codes.py
        #if self.response.status_code == requests.codes.internal_server_error:
        #    raise OpenShift500Exception('Internal Server Error: %s' % self.data)

        #if self.response.status_code == (200 or 201):
        #    log.debug("status:  %s" % self.response.status_code)
        return (self.response.status_code, self.data)

class MetricRest(object):
    """
    wrappers class around REST API so use can use it with python
    """
    rest = None
    user = None
    passwd = None

    def __init__(self, host, user=None, passwd=None, token=None, debug=False,
                 verbose=False, logger=None, proto=None, headers=None):

        self.rest = RestApi(host=host, username=user, password=passwd,
                            token=token, debug=debug, verbose=verbose,
                            proto=proto, headers=headers)

    def add_metric(self, unique_metric_list):
        """
        Add a list of UniqueMetrics (unique_metric_list) via rest
        """
        #metric_list = []
        #for metric in unique_metric_list:
        #    metric_list.append(metric)

        headers = { 'content-type': 'application/json; charset=utf8' }

        status, raw_response = self.rest.request(method='POST', url='metric', data=json.dumps(unique_metric_list, cls=MetricEncoder), headers=headers)

        return (status, raw_response)



if __name__ == "__main__":

    ml = []
    new_metric = UniqueMetric('a','b','c')
    ml.append(new_metric)
    new_metric = UniqueMetric('d','e','f')
    ml.append(new_metric)

    mr = MetricRest(host='172.17.0.27:8000')
    print mr.add_metric(ml)
