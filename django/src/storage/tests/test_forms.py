from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.forms import ValidationError
from django.core.files import File
from registration.tests.factories import UserFactory
from storage.tests.factories import FileStorageFactory
from storage import models, forms
from freezegun import freeze_time

class StorageForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.users = UserFactory.create_batch(6)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class UploadFileFormTests(StorageForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.FileStorage
        cls.form = forms.UploadFileForm

    def __create_form_data(self, filename, filesize):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = filename
        file_mock.size = filesize
        data = {
            'file': file_mock,
        }

        return data

    def test_form(self):
        filename = 'test_file.txt'
        form = self.form({}, self.__create_form_data(filename, 1))
        self.assertTrue(form.is_valid())

    def test_chk_allowed_extensions(self):
        for extension in ['pdf', 'jpg', 'png', 'txt', 'md', 'zip']:
            filename = 'test_file.{}'.format(extension)
            form = self.form({}, self.__create_form_data(filename, 1))
            self.assertTrue(form.is_valid())

    def test_invalid_extension(self):
        filename = 'test_file.dat'
        form = self.form({}, self.__create_form_data(filename, 1))
        self.assertFalse(form.is_valid())

    def test_chk_allowed_filesize(self):
        filename = 'test_file.txt'
        filesize = 30 * 1024 * 1024
        form = self.form({}, self.__create_form_data(filename, filesize))
        self.assertTrue(form.is_valid())

    def test_invalid_filesize(self):
        filename = 'test_file.txt'
        filesize = 30 * 1024 * 1024 + 1
        form = self.form({}, self.__create_form_data(filename, filesize))
        self.assertFalse(form.is_valid())
        with self.assertRaises(ValidationError):
            form.clean()

    @freeze_time('2021-01-01')
    def __get_filepath(self, user, filename):
        class DummyFieldFile:
            def __init__(self, user):
                self.user = user
        return models.get_filepath(DummyFieldFile(user), filename)

    @override_settings(MEDIA_URL='/')
    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_save(self, mock_save):
        user = self.users[0]
        filename = 'test_file.txt'
        # create hashed filename
        hashed_filename = self.__get_filepath(user, filename)
        mock_save.return_value = hashed_filename
        # create form
        form = self.form({}, self.__create_form_data(filename, 1))
        self.assertTrue(form.is_valid())
        # set user information
        file_storage = form.save(commit=False)
        file_storage.user = user
        file_storage.save()
        # compare
        self.assertEqual(file_storage.user, user)
        self.assertEqual(file_storage.filename, filename)
        self.assertEqual(file_storage.file.name, hashed_filename)
        self.assertEqual(file_storage.file.url, '/{}'.format(hashed_filename))

class FileSearchFormTests(StorageForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.FileStorage
        cls.form = forms.FileSearchForm

        patterns = [
            (cls.users[0], 'user0_cccc.txt', 'temp.md'),
            (cls.users[1], 'user1_file.txt', 'file.pdf'),
            (cls.users[2], 'user2_file.txt', 'file.pdf'),
            (cls.users[3], 'user3_file.txt', 'user3.pdf'),
            (cls.users[4], 'user4_file.txt', 'file.zip'),
        ]

        cls.files = [
            (
                FileStorageFactory(user=user),
                FileStorageFactory(user=user, filename=filename),
                FileStorageFactory(user=user, filename=extname, file__filename=extname),
            )
            for (user, filename, extname) in patterns
        ]

    def test_form(self):
        data = {
            'search_word': 'filename',
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {}
        form = self.form(data)
        self.assertFalse(form.is_valid())

    def test_chk_returned_queryset_for_search_word_pattern1(self):
        search_word = 'filename'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 5)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern2(self):
        search_word = 'user3'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 2)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 2)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern3(self):
        search_word = '.pdf'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern4(self):
        search_word = 'file'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 12)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 2)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

class FilenameUpdateFormTests(StorageForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form = forms.FilenameUpdateForm

    def test_form(self):
        data = {
            'filename': 'filename',
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_no_filename(self):
        data = {}
        form = self.form(data)
        self.assertFalse(form.is_valid())

    def test_empty_filename(self):
        data = {
            'filename': '',
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())
