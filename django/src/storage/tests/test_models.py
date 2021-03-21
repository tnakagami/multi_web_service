from unittest import mock
from django.test import TestCase
from django.core.files import File
from registration.tests.factories import UserFactory
from storage import models
from freezegun import freeze_time

class StorageModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = UserFactory()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class FileStorageTests(StorageModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.FileStorage

    def test_filestorage_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    @freeze_time('2021-01-01')
    def __get_filepath(self, user, filename):
        class DummyFieldFile:
            def __init__(self, user):
                self.user = user
        return models.get_filepath(DummyFieldFile(user), filename)

    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_create_filestorage(self, mock_save):
        # calculate hash value
        filename = 'test_file.dat'
        hashed_filename = self.__get_filepath(self.user, filename)
        mock_save.return_value = hashed_filename
        # create FileStorage instance
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = filename
        file_storage = self.model(user=self.user, filename=filename, file=file_mock)
        file_storage.save()
        # compare
        self.assertEqual(self.model.objects.count(), 1)
        file_storage = self.model.objects.get(pk=file_storage.pk)
        self.assertEqual(file_storage.user, self.user)
        self.assertEqual(file_storage.filename, filename)
        self.assertEqual(file_storage.file.name, hashed_filename)
        self.assertEqual(str(file_storage), filename)
        mock_save.assert_called_once()
