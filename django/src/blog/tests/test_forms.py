from django.test import TestCase
from django.db import IntegrityError, transaction
from registration.tests.factories import UserFactory
from blog.tests.factories import TagFactory, PostFactory
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

    def test_valid_form(self):
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
