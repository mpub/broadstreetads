"""A Broadstreet Ads API wrapper.

This is a thin layer over the python requests library to simplify
access to the Broadstreet Ads API. It provides the functionality:

    * Serialization and deserialization of data
    * Convert API errors into python exceptions
    * Re-trying requests if possible on various errors (TODO)
"""
import requests

_missing = object()

class APIError(Exception):
    """An error response from the broadstreet API."""

    def __init__(self,
            response):
        self.response = response
        self.status_code = response.status_code
        message = '{response.status_code} {response.content}'.format(response=response)
        Exception.__init__(self, message)

class APIServerError(APIError):
    pass

class APIConnection(object):

    API_VERSION = None

    def __init__(self,
            access_token,
            host='api.broadstreetads.com'):
        self._host = host
        self._access_token = access_token

    def _url(self, path):
        assert path.startswith('/')
        subs = dict(
                access_token=self._access_token,
                host=self._host,
                version=self.API_VERSION,
                path=path)
        return 'https://{host}/api/{version}{path}'.format(**subs)

    def _get_result(self, response, raw):
        if raw:
            return response
        if response.status_code >= 500 and response.status_code < 600:
            raise APIServerError(response)
        if response.status_code == 204:
            return None
        if response.status_code >= 200 and response.status_code < 300:
            return response.json()
        raise APIError(response)

    def get(self, path, _raw=False):
        url = self._url(path)
        params = {'access_token': self._access_token}
        r = requests.get(
                url,
                verify=True,
                params=params)
        return self._get_result(r, _raw)

    def post(self, path, data, _raw=False):
        url = self._url(path)
        d = {'access_token': self._access_token}
        d.update(data)
        r = requests.post(
                url,
                verify=True,
                data=d)
        return self._get_result(r, _raw)

    def delete(self, path, _raw=False):
        url = self._url(path)
        params = {'access_token': self._access_token}
        r = requests.delete(
                url,
                verify=True,
                params=params)
        return self._get_result(r, _raw)

    def patch(self, path, data, _raw=False):
        url = self._url(path)
        d = {'access_token': self._access_token}
        d.update(data)
        r = requests.patch(
                url,
                verify=True,
                data=d)
        return self._get_result(r, _raw)


class APIv0(APIConnection):
    """Connection to version 0 of the breadstreet API"""

    API_VERSION = 0

    def get_networks(self):
        resp = self.get('/networks')
        return resp['networks']

    def get_zones(self, network):
        url = '/networks/{network}/zones'.format(network=network)
        resp = self.get(url)
        return resp['zones']

    def create_zone(self, network, name, alias=None):
        url = '/networks/{network}/zones'.format(network=network)
        data = dict(name=name)
        if alias is not None:
            data['alias'] = alias
        resp = self.post(url, data)
        return resp['zone']

    def delete_zone(self, network, zone):
        url = '/networks/{network}/zones/{zone}'.format(
                network=network,
                zone=zone)
        resp = self.delete(url)
        return resp

    def update_zone(self, network, zone, name=_missing, alias=_missing):
        params = [
                ('name', name),
                ('alias', alias)]
        params = dict([(k, v) for k, v in params if v is not _missing])
        assert params
        url = '/networks/{network}/zones/{zone}'.format(
                network=network,
                zone=zone)
        resp = self.patch(url, params)
        return resp

def sync_zones(conn, namespace, network, zones):
    """Synchronize a local set of zones with one in broadstreet.

    `namespace` should be something very unique. A UUID or identifer of a
    product. it will be pre-pended to the alias of all zones with a dot (.).

    `zones` is a dictionary keyed by the zone alias. The values are
    dictionaries of the zone attributes.

    `network` integer id of the network to modify.

    `conn` is a broadstreet API connection.
    """
    created = []
    fixed = []
    deleted = []
    unchanged = []
    ignored = []
    have_zones = {}
    seen = set([])
    for zone in conn.get_zones(network):
        alias = zone.get('alias')
        if not alias or not alias.startswith(namespace + '.'):
            ignored.append(zone['id'])
            # only consider zones in our namespace
            continue
        ign, alias = alias.split(namespace + '.', 1)
        assert not ign, ign
        if alias in seen:
            # DUPLICATE, let's delete to remove any abiguities
            deleted.append(zone)
            conn.delete_zone(network, zone['id'])
            continue
        seen.add(alias)
        have_zones[alias] = zone
        wanted = zones.get(alias, None)
        if wanted is None:
            deleted.append(zone)
            conn.delete_zone(network, zone['id'])
        else:
            if wanted['name'] != zone['name']:
                conn.update_zone(
                        network,
                        zone['id'],
                        name=wanted['name'])
                fixed.append(zone['id'])
            else:
                unchanged.append(zone['id'])
    for alias, wanted in zones.items():
        if alias in have_zones:
            continue
        ns_alias = namespace + '.' + alias
        created.append(ns_alias)
        conn.create_zone(network, wanted['name'], alias=ns_alias)
    return dict(
            created=created,
            unchanged=unchanged,
            deleted=deleted,
            fixed=fixed,
            ignored=ignored)

if __name__ == '__main__':
    # UN-comment for very verbose logging
    #import logging
    #logging.basicConfig(level=logging.DEBUG)
    #import httplib
    #httplib.HTTPConnection.debuglevel = 1
    from pprint import pprint
    conn = APIv0('XXXXXXX')
    namespace = 'testing123'
    network = 0
    wanted = {
            'alias_zone_1': dict(name='Zone 1'),
            'alias_zone_2': dict(name='Zone 2')}
    r = conn.get_zones(network)
    pprint(r)
    r = sync_zones(conn, namespace, network, wanted)
    pprint(r)
    r = conn.get_zones(network)
    pprint(r)
