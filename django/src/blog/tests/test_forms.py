from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.db import IntegrityError, transaction
from registration.tests.factories import UserFactory
from blog.tests.factories import TagFactory, PostFactory
from django.core.files.base import ContentFile
from blog import models, forms

class BlogForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.users = UserFactory.create_batch(6)
        cls.tags = [
            (TagFactory.create(user=cls.users[0]                 ), TagFactory.create(user=cls.users[0], name='sample_a'), ),
            (TagFactory.create(user=cls.users[1]                 ), TagFactory.create(user=cls.users[1], name='sample_b'), ),
            (TagFactory.create(user=cls.users[2]                 ), TagFactory.create(user=cls.users[2], name='sample_c'), ),
            (TagFactory.create(user=cls.users[3], name='info_d'  ), TagFactory.create(user=cls.users[3], name='code_d'  ), TagFactory.create(user=cls.users[3], name='seed_d'  ), ),
            (TagFactory.create(user=cls.users[4], name='data_e'  ), TagFactory.create(user=cls.users[4], name='model_e' ), TagFactory.create(user=cls.users[4], name='type_e'  ), ),
        ]
        posts = [
            (PostFactory(user=cls.users[0], title='post1_user0' ), PostFactory(user=cls.users[0], title='title2_user0' ), PostFactory(user=cls.users[0], title='case3_user0'), ),
            (PostFactory(user=cls.users[1], title='post1_user1' ), PostFactory(user=cls.users[1], title='title2_user1' ), PostFactory(user=cls.users[1], title='case3_user1'), ),
            (PostFactory(user=cls.users[2], title='post1_user2' ), PostFactory(user=cls.users[2], title='title2_user2' ), PostFactory(user=cls.users[2], title='case3_user2'), ),
            (PostFactory(user=cls.users[3], title='bot1_user3'  ), PostFactory(user=cls.users[3], title='bot2_user3'  ), ),
            (PostFactory(user=cls.users[5], title='shape1_user5'), PostFactory(user=cls.users[5], title='shape2_user5'), ),
        ]
        user_tag_post_combination = [
            (cls.users[0], (cls.tags[0][0],), (posts[0][0], posts[0][1])),
            (cls.users[0], cls.tags[0],       posts[0]),
            (cls.users[1], (cls.tags[1][1],), (posts[1][1],)),
            (cls.users[1], cls.tags[1],       posts[1]),
            (cls.users[2], (cls.tags[2][0],), (posts[2][0], posts[2][2])),
            (cls.users[2], cls.tags[2],       posts[2]),
            (cls.users[3], cls.tags[3],       posts[3]),
            (cls.users[4], cls.tags[4],       tuple()),
            (cls.users[5], tuple(),           posts[4]),
        ]
        cls.posts = [
            PostFactory.create(
                user=_user,
                tags=(_tag.pk for _tag in _tags),
                relation_posts=(_post.pk for _post in _posts),
            ) for _user, _tags, _posts in user_tag_post_combination
        ]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class PostSearchFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Post
        cls.form = forms.PostSearchForm

    def test_form(self):
        search_word = 'abc'
        data = {
            'search_word': search_word,
            'tags': models.Tag.objects.filter(user=self.users[0]),
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_chk_returned_queryset_for_search_word_pattern1(self):
        search_word = 'post1'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern2(self):
        search_word = 'post1 user2'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_tags(self):
        data = {
            'tags': models.Tag.objects.filter(name='sample_a'),
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_specific_user(self):
        data = {}
        form = self.form(data, user=self.users[0])
        tags = form.fields['tags']
        _qs = tags.queryset
        self.assertEqual(_qs.count(), 2)
        self.assertEqual(_qs.filter(name='sample_a').count(), 1)

class TagSearchFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Tag
        cls.form = forms.TagSearchForm

    def test_form(self):
        search_word = 'abc'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_chk_returned_queryset_for_search_word_pattern1(self):
        search_word = 'sample'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern2(self):
        search_word = '_d'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 3)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

    def test_chk_returned_queryset_for_search_word_pattern3(self):
        search_word = '_e model'
        data = {
            'search_word': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())
        form.clean()
        _queryset = form.filtered_queryset(self.model.objects.all())
        self.assertEqual(_queryset.count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[0]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[1]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[2]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[3]).count(), 0)
        self.assertEqual(_queryset.filter(user=self.users[4]).count(), 1)
        self.assertEqual(_queryset.filter(user=self.users[5]).count(), 0)

class TagFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Tag
        cls.form = forms.TagForm

    def test_form(self):
        search_word = 'sample'
        data = {
            'name': search_word,
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_search_word_is_empty(self):
        search_word = ''
        data = {
            'name': search_word,
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())

    def test_chk_queryset_for_user(self):
        data = {}
        form = self.form(data, user=self.users[3])
        self.assertEqual(form.fields['name'].queryset.count(), 3)
        self.assertEqual(form.fields['name'].queryset.filter(name__icontains='_d').count(), 3)

class PostFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Post
        cls.form = forms.PostForm
        cls.targets = ('title', 'text', 'tags', 'relation_posts', 'is_public', 'description', 'keywords')

    def test_form(self):
        data = {key: '{}1'.format(key) for key in self.targets}
        data['tags'] = 0
        data['relation_posts'] = 0
        data['is_public'] = False
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_form_with_private(self):
        targets = [key for key in self.targets if key != 'is_public']
        data = {key: '{}1'.format(key) for key in self.targets}
        data['tags'] = 0
        data['relation_posts'] = 0
        data['is_public'] = False

        for key in targets:
            tmp_data = {_key: data[_key] for _key in self.targets}

            if key in ['tags', 'relation_posts']:
                tmp_data[key] = '{}1'.format(key)
            else:
                tmp_data[key] = ''

            form = self.form(tmp_data)
            self.assertFalse(form.is_valid())

    def test_chk_specific_user(self):
        data = {}
        form = self.form(data, user=self.users[3])
        self.assertEqual(form.fields['tags'].queryset.count(), 3)
        self.assertEqual(form.fields['tags'].queryset.filter(name__icontains='_d').count(), 3)
        self.assertEqual(form.fields['relation_posts'].queryset.count(), 3)
        self.assertEqual(form.fields['relation_posts'].queryset.filter(title__icontains='_user3').count(), 2)

    def test_chk_specific_user_with_pk(self):
        data = {}
        form = self.form(data, user=self.users[3], pk=self.posts[-3].pk)
        self.assertEqual(form.fields['tags'].queryset.count(), 3)
        self.assertEqual(form.fields['tags'].queryset.filter(name__icontains='_d').count(), 3)
        self.assertEqual(form.fields['relation_posts'].queryset.count(), 2)
        self.assertEqual(form.fields['relation_posts'].queryset.filter(title__icontains='_user3').count(), 2)

class CommentFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Comment
        cls.form = forms.CommentForm

    def test_form(self):
        data = {
            'name': 'no name',
            'text': 'comment',
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_text_is_empty(self):
        data = {
            'name': 'no name',
            'text': '',
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())

    def test_name_is_empty(self):
        data = {
            'name': '',
            'text': 'comment',
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())

class ReplyFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Reply
        cls.form = forms.ReplyForm

    def test_form(self):
        data = {
            'name': 'no name',
            'text': 'reply',
        }
        form = self.form(data)
        self.assertTrue(form.is_valid())

    def test_text_is_empty(self):
        data = {
            'name': 'no name',
            'text': '',
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())

    def test_name_is_empty(self):
        data = {
            'name': '',
            'text': 'reply',
        }
        form = self.form(data)
        self.assertFalse(form.is_valid())

class FileUploadFormTests(BlogForm):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form = forms.FileUploadForm

    def test_form(self):
        file_data = {
            'upload_file': ContentFile(b'some dummy bcode data: \x00\x01', 'test_file.dat'),
        }
        form = self.form({}, file_data)
        self.assertTrue(form.is_valid())

    @override_settings(MEDIA_URL='/')
    @mock.patch('django.core.files.storage.default_storage.save', return_value='test_file.dat')
    def test_save(self, _):
        file_data = {
            'upload_file': ContentFile(b'some dummy bcode data: \x80\x01', 'test_file.dat'),
        }
        form = self.form({}, file_data)
        self.assertTrue(form.is_valid())
        ret_url = form.save()
        self.assertEqual(ret_url, '/test_file.dat')

    def test_invalid_form(self):
        data = {
            'upload_file': '',
        }
        form = self.form({}, data)
        self.assertFalse(form.is_valid())
