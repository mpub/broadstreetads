from unittest import TestCase
from mock import Mock, patch

class TestAPIConnection(TestCase):

    def setUp(self):
        self._requests_patcher = patch('broadstreetads.requests')
        self.requests = self._requests_patcher.start()

    def tearDown(self):
        self._requests_patcher.stop()

    def one(self, access_token='123', host='api.broadstreetads.com'):
        from broadstreetads import APIConnection
        return APIConnection('123')

    def test_5XX_get(self):
        from broadstreetads import APIServerError
        api = self.one()
        self.requests.get().status_code = 504
        self.assertRaises(APIServerError, api.get, '/whatever')

    def test_5XX_post(self):
        from broadstreetads import APIServerError
        api = self.one()
        self.requests.post().status_code = 504
        self.assertRaises(APIServerError, api.post, '/whatever', {})

    def test_5XX_delete(self):
        from broadstreetads import APIServerError
        api = self.one()
        self.requests.delete().status_code = 504
        self.assertRaises(APIServerError, api.delete, '/whatever')

    def test_5XX_patch(self):
        from broadstreetads import APIServerError
        api = self.one()
        self.requests.patch().status_code = 504
        self.assertRaises(APIServerError, api.patch, '/whatever', {})
