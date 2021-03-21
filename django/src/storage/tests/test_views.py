from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse, resolve
from django.core.files import File
from registration.tests.factories import UserFactory, UserModel
from storage.tests.factories import FileStorageFactory
from storage import views, models
from freezegun import freeze_time

class StorageView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.model = models.FileStorage
        cls.password = 'password'
        cls.users = UserFactory.create_batch(6)

        patterns = [
            (cls.users[0], 'user0_file.txt', 'temp.md'),
            (cls.users[1], 'user1_file.txt', 'file.pdf'),
            (cls.users[2], 'user2_file.txt', ''),
            (cls.users[3], '', 'user3.pdf'),
            (cls.users[4], '', ''),
        ]

        cls.files = []
        for (user, filename, extname) in patterns:
            tmp_files = [FileStorageFactory(user=user)]

            if filename:
                tmp_files.append(FileStorageFactory(user=user, filename=filename))
            if extname:
                tmp_files.append(FileStorageFactory(user=user, filename=extname, file__filename=extname))

            cls.files.append(tuple(tmp_files))

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class StorageListViewTests(StorageView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('storage:index')

    def test_resolve_url(self):
        resolver = resolve('/storage/')
        self.chk_class(resolver, views.StorageListView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_listed_files(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('storage/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('files' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _files = response.context.get('files')
        _paginator = response.context.get('paginator')
        self.assertEqual(_files.count(), 3)
        self.assertEqual(_paginator.page_range[-1], 1)

    @override_settings(AXES_ENABLED=False)
    def test_no_uploaded_files(self):
        self.client.logout()
        self.client.login(username=self.users[5].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('files' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _files = response.context.get('files')
        _paginator = response.context.get('paginator')
        self.assertEqual(_files.count(), 0)
        self.assertEqual(_paginator.page_range[-1], 1)

    def test_valid_search_word_pattern1(self):
        data = {
            'search_word': 'file',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('files' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _files = response.context.get('files')
        _paginator = response.context.get('paginator')
        self.assertEqual(_files.count(), 2)
        self.assertEqual(_paginator.page_range[-1], 1)

    def test_valid_search_word_pattern2(self):
        data = {
            'search_word': '.md',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('files' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _files = response.context.get('files')
        _paginator = response.context.get('paginator')
        self.assertEqual(_files.count(), 1)
        self.assertEqual(_paginator.page_range[-1], 1)

    def test_chk_post_request(self):
        data = {
            'search_word': '.md',
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 405)

class FileUploadViewTests(StorageView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('storage:upload')

    def __create_request_data(self, filename, filesize):
        file_mock = mock.MagicMock(spec=File)
        file_mock.name = filename
        file_mock.size = filesize
        data = {
            'file': file_mock,
        }

        return data

    def test_resolve_url(self):
        resolver = resolve('/storage/upload/')
        self.chk_class(resolver, views.FileUploadView)

    def test_no_login_access(self):
        self.client.logout()
        data = self.__create_request_data('target_file.txt', 1)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @freeze_time('2021-01-01')
    def __get_filepath(self, user, filename):
        class DummyFieldFile:
            def __init__(self, user):
                self.user = user
        return models.get_filepath(DummyFieldFile(user), filename)

    @override_settings(MEDIA_URL='/')
    @mock.patch('django.core.files.storage.FileSystemStorage.save')
    def test_creating_file(self, mock_save):
        filename = 'target_file.txt'
        filesize = 123
        # create hashed filename
        hashed_filename = self.__get_filepath(self.users[0], filename)
        mock_save.return_value = hashed_filename
        # create data
        data = self.__create_request_data(filename, filesize)
        # request
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('files', response.context.keys())
        # compare
        _files = response.context['files'].all()
        self.assertEqual(_files.count(), 4)
        max_pk = max([file_.pk for file_ in _files]) # get last record from queryset
        _file = self.model.objects.get(pk=max_pk)
        self.assertEqual(_file.user, self.users[0])
        self.assertEqual(_file.filename, filename)
        self.assertEqual(_file.file.name, hashed_filename)
        self.assertEqual(_file.file.url, '/{}'.format(hashed_filename))
        mock_save.assert_called_once()

    def test_invalid_request_data(self):
        filename = 'target_file.txt'
        filesize = 123
        data = self.__create_request_data(filename, filesize)
        data = {key: '' for key in data.keys()}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('storage/index.html')
        self.assertTrue('upload_form' in response.context.keys())
        _upload_form = response.context['upload_form']
        self.assertTrue('file' in _upload_form.errors.keys())
        self.assertEqual(self.model.objects.filter(user=self.users[0]).count(), 3)
        self.assertEqual(self.model.objects.filter(filename=filename).count(), 0)
        self.assertTrue('files' in response.context.keys())
        _files = response.context['files']
        self.assertEqual(len(list(_files.all())), 3)

class FilenameUpdateViewTests(StorageView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.target = FileStorageFactory(user=self.users[0])

    def test_resolve_url(self):
        resolver = resolve('/storage/update/filename/123')
        self.chk_class(resolver, views.FilenameUpdateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target.pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        data = {
            'filename': 'new_filename',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        data = {
            'pk': self.target.pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_updating_filename(self):
        target_pk = self.target.pk
        data = {
            'pk': target_pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        filename = 'new_filename'
        data = {
            'filename': filename,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _file = self.model.objects.get(pk=target_pk)
        self.assertEqual(_file.filename, filename)

    def test_empty_filename(self):
        target_pk = self.target.pk
        data = {
            'pk': target_pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        filename = ''
        data = {
            'filename': filename,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _file = self.model.objects.get(pk=target_pk)
        self.assertEqual(_file.filename, self.target.filename)

    def test_blank_filename(self):
        target_pk = self.target.pk
        data = {
            'pk': target_pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        filename = ' '
        data = {
            'filename': filename,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _file = self.model.objects.get(pk=target_pk)
        self.assertEqual(_file.filename, self.target.filename)

    def test_updating_other_user_file(self):
        target = self.files[-1][0]
        data = {
            'pk': target.pk,
        }
        url = reverse('storage:update_filename', kwargs=data)
        filename = 'new_filename'
        data = {
            'filename': filename,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 403)
        _file = self.model.objects.get(pk=target.pk)
        self.assertEqual(_file.filename, target.filename)

    def test_not_exist_file(self):
        data = {
            'pk': self.model.objects.count() + 1,
        }
        url = reverse('storage:update_filename', kwargs=data)
        filename = ' '
        data = {
            'filename': filename,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)

class FileDeleteViewTests(StorageView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.target = FileStorageFactory(user=self.users[0])

    def test_resolve_url(self):
        resolver = resolve('/storage/delete/123')
        self.chk_class(resolver, views.FileDeleteView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target.pk,
        }
        url = reverse('storage:delete', kwargs=data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        data = {
            'pk': self.target.pk,
        }
        url = reverse('storage:delete', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_deleting_own_file(self):
        data = {
            'pk': self.target.pk,
        }
        url = reverse('storage:delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(self.model.DoesNotExist):
            _ = self.model.objects.get(pk=self.target.pk)

    def test_deleting_other_user_file(self):
        target_pk = self.files[-1][0].pk
        data = {
            'pk': target_pk,
        }
        url = reverse('storage:delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = self.model.objects.get(pk=target_pk)

    def test_not_exist_file(self):
        data = {
            'pk': self.model.objects.count() + 1,
        }
        url = reverse('storage:delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
