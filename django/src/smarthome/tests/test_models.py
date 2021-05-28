from django.test import TestCase
from smarthome import models

class SmartHomeModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class AccessTokenTests(SmartHomeModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.AccessToken

    def __chk_instance_data(self, pk, token):
        target = self.model.objects.get(pk=pk)
        self.assertEqual(target.access_token, token)
        self.assertTrue(target.is_valid_access_token(token))

    def __create_and_save(self, token):
        target = self.model()
        target.save()

        return target

    def test_access_token_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_access_token(self):
        token = '123token'
        _access_token = self.__create_and_save(token)
        self.__chk_instance_data(_access_token.pk, token)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(str(_access_token), access_token)
