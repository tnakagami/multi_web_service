from django.test import TestCase, RequestFactory
from custom_templatetags import pagination

class PaginationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def test_pagination(self):
        request = self.factory.get('/', {'page': 3})
        ret = pagination.url_replace(request, 'page', 2)
        self.assertEqual(ret, 'page=2')

    def test_no_existing_field(self):
        request = self.factory.get('/', {'page': 3})
        ret = pagination.url_replace(request, 'pages', 2)
        self.assertEqual(ret, 'page=3&pages=2')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
