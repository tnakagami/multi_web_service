from unittest import mock
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import Permission
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory, UserModel
from blog.tests.factories import TagFactory, PostFactory
from blog import views, models

class BlogView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        cls.password = 'password'
        cls.users = UserFactory.create_batch(7)
        view_user = Permission.objects.get(codename='view_user')
        view_perm = Permission.objects.get(codename='view_permission')
        for user in cls.users:
            user.user_permissions.add(view_user, view_perm)

        cls.tags = [
            (TagFactory.create(user=cls.users[0]               ), TagFactory.create(user=cls.users[0], name='sample_a'), ),
            (TagFactory.create(user=cls.users[1]               ), TagFactory.create(user=cls.users[1], name='sample_b'), ),
            (TagFactory.create(user=cls.users[2]               ), TagFactory.create(user=cls.users[2], name='sample_c'), ),
            (TagFactory.create(user=cls.users[3], name='info_d'), TagFactory.create(user=cls.users[3], name='sample_d'), TagFactory.create(user=cls.users[3], name='seed_d'), ),
            (TagFactory.create(user=cls.users[4], name='data_e'), TagFactory.create(user=cls.users[4], name='sample_e'), TagFactory.create(user=cls.users[4], name='type_e'), ),
        ]
        posts = [
            (PostFactory(user=cls.users[0], title='post10' ), PostFactory(user=cls.users[0], title='title20' ), PostFactory(user=cls.users[0], title='case30'), ),
            (PostFactory(user=cls.users[1], title='post11' ), PostFactory(user=cls.users[1], title='title21' ), PostFactory(user=cls.users[1], title='case31'), ),
            (PostFactory(user=cls.users[2], title='post12' ), PostFactory(user=cls.users[2], title='title22' ), PostFactory(user=cls.users[2], title='case32'), ),
            (PostFactory(user=cls.users[3], title='bot13'  ), PostFactory(user=cls.users[3], title='bot23'  ),  PostFactory(user=cls.users[3], title='private', is_public=False)),
            (PostFactory(user=cls.users[5], title='shape15'), PostFactory(user=cls.users[5], title='shape25'), ),
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

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class PostListViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('blog:index')

    def test_resolve_url(self):
        resolver = resolve('/blog/')
        self.chk_class(resolver, views.PostListView)

    def test_valid_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_valid_listed_posts(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('blog/index.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        self.assertTrue('paginator' in response.context.keys())
        _posts = response.context.get('posts')
        _paginator = response.context.get('paginator')
        self.assertEqual(_posts.count(), 10)
        self.assertEqual(_paginator.page_range[-1], 3)

    @override_settings(AXES_ENABLED=False)
    def test_valid_listed_posts_with_private(self):
        user = self.users[3]
        self.client.logout()
        self.client.login(username=user.username, password=self.password)
        data = {
            'page': 3,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 3) # 23 % 10: total_posts_count % paginate_by

    def test_valid_chk_pagination(self):
        data = {
            'page': 3,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 2) # (23 - 1) % 10: (total_posts_count - private_post_count) % paginate_by

    @override_settings(AXES_ENABLED=False)
    def test_valid_no_posts(self):
        user = self.users[-1]
        self.client.logout()
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(len([post for post in _posts if post.user == user]), 0)

    def test_valid_filtered_posts(self):
        data = {
            'search_word': 'case',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 3)

    def test_valid_filtered_tags(self):
        data = {
            'tags': [self.tags[0][0].pk],
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 2)

        data = {
            'tags': [self.tags[0][1].pk],
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 1)

class OwnPostListViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        data = {
            'pk': self.users[0].pk
        }
        self.url = reverse('blog:own_post', kwargs=data)

    def test_resolve_url(self):
        resolver = resolve('/blog/own/post/123')
        self.chk_class(resolver, views.OwnPostListView)

    def test_valid_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_valid_own_page(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('blog/own_post.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 5)

    @override_settings(AXES_ENABLED=False)
    def test_valid_own_page_with_private_post(self):
        self.client.logout()
        self.client.login(username=self.users[3].username, password=self.password)
        data = {
            'pk': self.users[3].pk,
        }
        url = reverse('blog:own_post', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 4)

    def test_valid_filtered_posts(self):
        data = {
            'search_word': 'case',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 1)

    def test_valid_filtered_tags(self):
        data = {
            'tags': [self.tags[0][0].pk],
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 2)

        data = {
            'tags': [self.tags[0][1].pk],
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 1)

    @override_settings(AXES_ENABLED=False)
    def test_invalid_other_user_page(self):
        self.client.logout()
        self.client.login(username=self.users[3].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
