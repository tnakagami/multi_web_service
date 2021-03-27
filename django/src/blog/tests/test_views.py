from unittest import mock, skipIf
from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import Permission
from django.urls import reverse, resolve
from registration.tests.factories import UserFactory, UserModel
from blog.tests.factories import TagFactory, PostFactory, CommentFactory
from django.core.files.base import ContentFile
from blog import views, models

IgnoreTagTests = {'condition': True, 'reason': 'Tag function is not provided'}

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

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_listed_posts(self):
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
    def test_listed_posts_with_private(self):
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

    def test_chk_pagination(self):
        data = {
            'page': 3,
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 2) # (23 - 1) % 10: (total_posts_count - private_post_count) % paginate_by

    @override_settings(AXES_ENABLED=False)
    def test_no_posts(self):
        user = self.users[-1]
        self.client.logout()
        self.client.login(username=user.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(len([post for post in _posts if post.user == user]), 0)

    def test_filtered_posts(self):
        data = {
            'search_word': 'case',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 3)

    def test_filtered_tags(self):
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

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_own_page(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('blog/own_post.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('posts' in response.context.keys())
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 5)

    @override_settings(AXES_ENABLED=False)
    def test_own_page_with_private_post(self):
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

    def test_filtered_posts(self):
        data = {
            'search_word': 'case',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _posts = response.context.get('posts')
        self.assertEqual(_posts.count(), 1)

    def test_filtered_tags(self):
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
    def test_other_user_page(self):
        self.client.logout()
        self.client.login(username=self.users[3].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

@skipIf(IgnoreTagTests['condition'], IgnoreTagTests['reason'])
class OwnTagListViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        data = {
            'pk': self.users[0].pk
        }
        self.url = reverse('blog:own_tag', kwargs=data)

    def test_resolve_url(self):
        resolver = resolve('/blog/own/tag/123')
        self.chk_class(resolver, views.OwnTagListView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_own_page(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('blog/own_tag.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('tags' in response.context.keys())
        _tags = response.context.get('tags')
        self.assertEqual(_tags.count(), 2)

    def test_filtered_tags(self):
        data = {
            'search_word': 'sample',
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        _tags = response.context.get('tags')
        self.assertEqual(_tags.count(), 1)

@skipIf(IgnoreTagTests['condition'], IgnoreTagTests['reason'])
class TagCreateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('blog:tag_create')

    def test_resolve_url(self):
        resolver = resolve('/blog/tag/create')
        self.chk_class(resolver, views.TagCreateView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_creating_tag(self):
        tag_name = 'added_tag'
        data = {
            'name': tag_name,
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertTemplateUsed('blog/tag_create_form.html')
        self.assertEqual(response.status_code, 200)
        _tag = models.Tag.objects.get(name=tag_name)
        self.assertEqual(_tag.user, self.users[0])

    def test_same_tag(self):
        tag_name = 'sample_a'
        data = {
            'name': tag_name,
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())
        _form = response.context.get('form')
        self.assertTrue('name' in _form.errors.keys())

    def test_same_tag_other_user(self):
        tag_name = 'sample_b'
        data = {
            'name': tag_name,
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())
        _form = response.context.get('form')
        self.assertTrue('name' in _form.errors.keys())

@skipIf(IgnoreTagTests['condition'], IgnoreTagTests['reason'])
class TagUpdateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.tag_name = 'created_tag'
        self.created_tag = TagFactory.create(user=self.users[0], name=self.tag_name)

    def test_resolve_url(self):
        resolver = resolve('/blog/tag/update/123')
        self.chk_class(resolver, views.TagUpdateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.created_tag.pk,
        }
        url = reverse('blog:tag_update', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_updating_tag(self):
        new_tag_name = 'updated_tag'
        data = {
            'pk': self.created_tag.pk,
        }
        url = reverse('blog:tag_update', kwargs=data)
        data = {
            'name': new_tag_name,
        }
        response = self.client.post(url, data, follow=True)
        self.assertTemplateUsed('blog/tag_update_form.html')
        self.assertEqual(response.status_code, 200)
        _tag = models.Tag.objects.get(pk=self.created_tag.pk)
        self.assertEqual(_tag.name, new_tag_name)

    def test_not_exist_tag_pk(self):
        new_tag_name = 'updated_tag'
        data = {
            'pk': models.Tag.objects.count() + 1,
        }
        url = reverse('blog:tag_update', kwargs=data)
        data = {
            'name': new_tag_name,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)
        _tag = models.Tag.objects.get(pk=self.created_tag.pk)
        self.assertEqual(_tag.name, self.tag_name)

    def test_tag_defined_by_other_user(self):
        new_tag_name = 'updated_tag'
        target_tag = self.tags[1][0]
        data = {
            'pk': target_tag.pk,
        }
        url = reverse('blog:tag_update', kwargs=data)
        data = {
            'name': new_tag_name,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 403)
        _tag = models.Tag.objects.get(pk=target_tag.pk)
        self.assertEqual(_tag.name, target_tag.name)

@skipIf(IgnoreTagTests['condition'], IgnoreTagTests['reason'])
class TagDeleteViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.tag_name = 'target_tag'
        self.target_tag = TagFactory.create(user=self.users[0], name=self.tag_name)

    def test_resolve_url(self):
        resolver = resolve('/blog/tag/delete/123')
        self.chk_class(resolver, views.TagDeleteView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target_tag.pk,
        }
        url = reverse('blog:tag_delete', kwargs=data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        data = {
            'pk': self.target_tag.pk,
        }
        url = reverse('blog:tag_delete', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_deleting_target_tag(self):
        data = {
            'pk': self.target_tag.pk,
        }
        url = reverse('blog:tag_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.Tag.DoesNotExist):
            _ = models.Tag.objects.get(pk=self.target_tag.pk)

    def test_not_exist_tag(self):
        data = {
            'pk': models.Tag.objects.count() + 1,
        }
        url = reverse('blog:tag_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        _ = models.Tag.objects.get(pk=self.target_tag.pk)

    def test_tag_defined_by_other_user(self):
        target_tag = self.tags[1][0]
        data = {
            'pk': target_tag.pk,
        }
        url = reverse('blog:tag_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = models.Tag.objects.get(pk=target_tag.pk)

class PostCreateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.url = reverse('blog:post_create')

    def test_resolve_url(self):
        resolver = resolve('/blog/post/create')
        self.chk_class(resolver, views.PostCreateView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_chk_post_form(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed('blog/post_create_form.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())
        _form = response.context.get('form')
        self.assertTrue('relation_posts' in _form.fields.keys())
        _relation_posts = _form.fields['relation_posts'].queryset
        for _post in _relation_posts.all():
            self.assertTrue(_post.is_public)

    @override_settings(AXES_ENABLED=False)
    def test_chk_post_form_with_private_page(self):
        self.client.logout()
        self.client.login(username=self.users[3].username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context.keys())
        _form = response.context.get('form')
        self.assertTrue('relation_posts' in _form.fields.keys())
        _relation_posts = _form.fields['relation_posts'].queryset
        for _post in _relation_posts.all():
            self.assertTrue(_post.is_public)

    def test_creating_post(self):
        data = {
            'title': 'created_post_title',
            'text': 'created_post_text',
            'tags': [self.tags[0][0].pk],
            'relation_posts': [self.posts[0].pk],
            'is_public': True,
            'description': 'created_post_data',
            'keywords': 'created_post_keyword',
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _post = models.Post.objects.all().last()
        _tags = list(_post.tags.all().values_list('pk', flat=True))
        _relation_posts = list(_post.relation_posts.all().values_list('pk', flat=True))
        self.assertEqual(_post.user, self.users[0])
        self.assertEqual(_post.title, data['title'])
        self.assertEqual(_post.text, data['text'])
        self.assertEquals(_tags, data['tags'])
        self.assertEquals(_relation_posts, data['relation_posts'])
        self.assertEqual(_post.is_public, data['is_public'])
        self.assertEqual(_post.description, data['description'])
        self.assertEqual(_post.keywords, data['keywords'])

class PostUpdateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        _tags = tuple(tag.pk for tag in self.tags[0])
        _relation_posts = tuple([self.posts[0]])
        self.created_post = PostFactory.create(user=self.users[0], tags=_tags, relation_posts=_relation_posts)

    def test_resolve_url(self):
        resolver = resolve('/blog/post/update/123')
        self.chk_class(resolver, views.PostUpdateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.created_post.pk,
        }
        url = reverse('blog:post_update', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_updating_post(self):
        data = {
            'pk': self.created_post.pk,
        }
        url = reverse('blog:post_update', kwargs=data)
        data = {
            'title': 'updated_title',
            'text': 'updated_text',
            'tags': [],
            'relation_posts': [],
            'is_public': False,
            'description': 'updated_description',
            'keywords': 'updated_keywords',
        }
        response = self.client.post(url, data, follow=True)
        self.assertTemplateUsed('blog/post_update_form.html')
        self.assertEqual(response.status_code, 200)
        _post = models.Post.objects.get(pk=self.created_post.pk)
        self.assertEqual(_post.user, self.users[0])
        self.assertEqual(_post.title, data['title'])
        self.assertEqual(_post.text, data['text'])
        self.assertEquals(_post.tags.all().count(), 0)
        self.assertEquals(_post.relation_posts.all().count(), 0)
        self.assertEqual(_post.is_public, data['is_public'])
        self.assertEqual(_post.description, data['description'])
        self.assertEqual(_post.keywords, data['keywords'])

    def test_not_exist_post(self):
        data = {
            'pk': models.Post.objects.count() + 1,
        }
        url = reverse('blog:post_update', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_post_defined_by_other_user(self):
        target_post = self.posts[-1]
        data = {
            'pk': target_post.pk,
        }
        url = reverse('blog:post_update', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)

class PostDeleteViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.target_post = PostFactory(user=self.users[0])

    def test_resolve_url(self):
        resolver = resolve('/blog/post/delete/123')
        self.chk_class(resolver, views.PostDeleteView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target_post.pk,
        }
        url = reverse('blog:post_delete', kwargs=data)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_get_access(self):
        data = {
            'pk': self.target_post.pk,
        }
        url = reverse('blog:post_delete', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_deleting_target_post(self):
        data = {
            'pk': self.target_post.pk,
        }
        url = reverse('blog:post_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.Post.DoesNotExist):
            _ = models.Post.objects.get(pk=self.target_post.pk)

    def test_not_exist_tag(self):
        data = {
            'pk': models.Post.objects.count() + 1,
        }
        url = reverse('blog:post_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 404)
        _ = models.Post.objects.get(pk=self.target_post.pk)

    def test_post_defined_by_other_user(self):
        target_post = self.posts[-1]
        data = {
            'pk': target_post.pk,
        }
        url = reverse('blog:post_delete', kwargs=data)
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 403)
        _ = models.Post.objects.get(pk=target_post.pk)

class PostDetailViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.private_user0 = PostFactory(user=self.users[0], title='private_user0', is_public=False)
        self.private_user5 = PostFactory(user=self.users[5], title='private_user5', is_public=False)

    def test_resolve_url(self):
        resolver = resolve('/blog/post/detail/123')
        self.chk_class(resolver, views.PostDetailView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.posts[0].pk,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_detail_own_post(self):
        data = {
            'pk': self.posts[0].pk,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertTemplateUsed('blog/post_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_detail_own_private_post(self):
        data = {
            'pk': self.private_user0.pk,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_other_user_post(self):
        data = {
            'pk': self.posts[-1].pk,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_other_user_private_post(self):
        data = {
            'pk': self.private_user5.pk,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_not_exist_post(self):
        data = {
            'pk': models.Post.objects.count() + 1,
        }
        url = reverse('blog:post_detail', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class CommentCreateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        self.target_pk = self.posts[-1].pk

    def test_resolve_url(self):
        resolver = resolve('/blog/comment/create/123')
        self.chk_class(resolver, views.CommentCreateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:comment_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'comment',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_get_access(self):
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:comment_create', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_creating_comment(self):
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:comment_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'comment',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _comment = models.Comment.objects.get(target__pk=self.target_pk)
        self.assertEqual(_comment.name, data['name'])
        self.assertEqual(_comment.text, data['text'])

    def test_not_exist_post(self):
        data = {
            'pk': models.Post.objects.count() + 1,
        }
        url = reverse('blog:comment_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'comment',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(models.Comment.objects.count(), 0)

class ReplyCreateViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        self.client.login(username=self.users[0].username, password=self.password)
        comment = CommentFactory(target=self.posts[-1])
        self.target_pk = comment.pk

    def test_resolve_url(self):
        resolver = resolve('/blog/reply/create/123')
        self.chk_class(resolver, views.ReplyCreateView)

    def test_no_login_access(self):
        self.client.logout()
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:reply_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'reply',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_get_access(self):
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:reply_create', kwargs=data)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_creating_reply(self):
        data = {
            'pk': self.target_pk,
        }
        url = reverse('blog:reply_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'reply',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        _reply = models.Reply.objects.get(target__pk=self.target_pk)
        self.assertEqual(_reply.name, data['name'])
        self.assertEqual(_reply.text, data['text'])

    def test_not_exist_post(self):
        data = {
            'pk': models.Comment.objects.count() + 1,
        }
        url = reverse('blog:reply_create', kwargs=data)
        data = {
            'name': 'no name',
            'text': 'reply',
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(models.Reply.objects.count(), 0)

class FileUploadViewTests(BlogView):
    @override_settings(AXES_ENABLED=False)
    def setUp(self):
        super().setUp()
        self.client.login(username=self.users[0].username, password=self.password)
        self.file_data = {
            'upload_file': ContentFile(b'some dummy bcode data: \x80\x01', 'test_file.dat'),
        }
        self.url = reverse('blog:file_upload')

    def test_resolve_url(self):
        resolver = resolve('/blog/file/upload/')
        self.chk_class(resolver, views.FileUploadView)

    def test_no_login_access(self):
        self.client.logout()
        response = self.client.post(self.url, self.file_data)
        self.assertEqual(response.status_code, 302)

    def test_get_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @override_settings(MEDIA_URL='/')
    @mock.patch('django.core.files.storage.default_storage.save', return_value='test_file.dat')
    def test_valid_file_upload(self, _):
        import json
        response = self.client.post(self.url, self.file_data)
        self.assertEqual(response.status_code, 200)
        _content = json.loads(response.content)
        self.assertTrue('url' in _content.keys())
        _filename = _content['url'].split('/')[-1]
        self.assertEqual(_filename, 'test_file.dat')

    def test_invalid_file_upload(self):
        data = {
            'upload_file': '',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
