from django.test import TestCase
from django.db import IntegrityError, transaction
from registration.tests.factories import UserFactory
from blog import models

class BlogModel(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.users = UserFactory.create_batch(10)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TagTests(BlogModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Tag

    def __chk_instance_data(self, pk, user, name):
        tag = self.model.objects.get(pk=pk)
        self.assertEqual(tag.user, user)
        self.assertEqual(tag.name, name)

    def __create_and_save(self, user, name):
        tag = self.model()
        tag.user = user
        tag.name = name
        tag.save()

        return tag

    def test_tag_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_tag(self):
        tag_name = 'sample_tag'
        _user = self.users[0]
        _tag = self.__create_and_save(_user, tag_name)
        self.__chk_instance_data(_tag.pk, _user, tag_name)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(str(_tag), tag_name)

    def test_check_unique_constraint(self):
        tag_name = 'sample_tag'
        _user = self.users[0]
        _tag = self.__create_and_save(_user, tag_name)
        self.__chk_instance_data(_tag.pk, _user, tag_name)
        self.assertEqual(self.model.objects.count(), 1)
        _user = self.users[1]
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                _ = self.__create_and_save(_user, tag_name)
        self.assertEqual(self.model.objects.all().count(), 1)

class PostTests(BlogModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Post

    def __chk_instance_data(self, pk, data):
        post = self.model.objects.get(pk=pk)

        num_tags = data.pop('tags')
        num_posts = data.pop('relation_posts')

        for key, value in data.items():
            self.assertEqual(getattr(post, key), value)
        self.assertEqual(post.tags.all().count(), num_tags)
        self.assertEqual(post.relation_posts.all().count(), num_posts)

    def __create_and_save(self, data):
        post = self.model()

        for key, value in data.items():
            if key not in ['tags', 'relation_posts']:
                setattr(post, key, value)
        post.save()
        keys = data.keys()
        if 'tags' in keys:
            post.tags.set(data['tags'])
        if 'relation_posts' in keys:
            post.relation_posts.set(data['relation_posts'])

        return post

    def test_post_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_post(self):
        _user = self.users[0]
        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        post = self.__create_and_save(data)
        self.assertEqual(self.model.objects.filter(user=_user).count(), 1)
        expected = {key: value for key, value in data.items()}
        expected['tags'] = 0
        expected['relation_posts'] = 0
        self.__chk_instance_data(post.pk, expected)

    def test_create_post_with_tag(self):
        _user = self.users[1]
        tag_name = '_tag'
        tag = models.Tag()
        tag.user = _user
        tag.name = tag_name
        tag.save()
        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'tags': [tag.pk],
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        post = self.__create_and_save(data)
        self.assertEqual(self.model.objects.filter(user=_user).count(), 1)
        expected = {key: value for key, value in data.items()}
        expected['tags'] = 1
        expected['relation_posts'] = 0
        self.__chk_instance_data(post.pk, expected)
        _ = post.tags.get(pk=tag.pk)

    def test_create_post_with_tag_and_other_post(self):
        _user = self.users[2]
        tag_name = '_tag'
        tag = models.Tag()
        tag.user = _user
        tag.name = tag_name
        tag.save()
        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        first_post = self.__create_and_save(data)

        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'tags': [tag.pk],
            'relation_posts': [first_post.pk],
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        post = self.__create_and_save(data)
        self.assertEqual(self.model.objects.filter(user=_user).count(), 2)
        expected = {key: value for key, value in data.items()}
        expected['tags'] = 1
        expected['relation_posts'] = 1
        self.__chk_instance_data(post.pk, expected)

class CommentTests(BlogModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Comment

    def __chk_instance_data(self, pk, data):
        comment = self.model.objects.get(pk=pk)

        post_pk = data.pop('target')

        for key, value in data.items():
            self.assertEqual(getattr(comment, key), value)
        self.assertEqual(comment.target.pk, post_pk)

    def __create_and_save(self, data):
        comment = self.model()

        for key, value in data.items():
            setattr(comment, key, value)
        comment.save()

        return comment

    def __set_post_data(self):
        _user = self.users[3]
        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        post = models.Post()
        for key, value in data.items():
            setattr(post, key, value)
        post.save()

        return post

    def test_comment_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_create_comment(self):
        post = self.__set_post_data()
        text = 'comment'
        data = {
            'name': 'comment_user',
            'text': text,
            'target': post,
        }
        comment = self.__create_and_save(data)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(self.model.objects.get(pk=comment.pk).target.pk, post.pk)
        self.assertEqual(str(comment), text)

    def test_create_comment_length_is_more_than_32characters(self):
        post = self.__set_post_data()
        text = 'a' * 33
        data = {
            'name': 'comment_user',
            'text': text,
            'target': post,
        }
        comment = self.__create_and_save(data)
        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(self.model.objects.get(pk=comment.pk).target.pk, post.pk)
        self.assertEqual(str(comment), text[:32])

class ReplyTests(BlogModel):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.model = models.Reply

    def __chk_instance_data(self, pk, data):
        reply = self.model.objects.get(pk=pk)

        comment_pk = data.pop('target')

        for key, value in data.items():
            self.assertEqual(getattr(reply, key), value)
        self.assertEqual(reply.target.pk, comment_pk)

    def __create_and_save(self, data):
        reply = self.model()

        for key, value in data.items():
            setattr(reply, key, value)
        reply.save()

        return reply

    def __set_post_and_comment_data(self):
        _user = self.users[4]
        data = {
            'user': _user,
            'title': '_title',
            'text': '_text',
            'is_public': True,
            'description': '_description',
            'keywords': '_post_keyword',
        }
        post = models.Post()
        for key, value in data.items():
            setattr(post, key, value)
        post.save()

        text = 'comment'
        data = {
            'name': 'comment_user',
            'text': text,
            'target': post,
        }
        comment = models.Comment()
        for key, value in data.items():
            setattr(comment, key, value)
        comment.save()

        return comment

    def test_reply_is_empty(self):
        self.assertEqual(self.model.objects.count(), 0)

    def test_reply_comment(self):
        comment = self.__set_post_and_comment_data()
        text = 'rely'
        data = {
            'name': 'reply_user',
            'text': text,
            'target': comment,
        }
        reply = self.__create_and_save(data)

        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(self.model.objects.get(pk=reply.pk).target.pk, comment.pk)
        self.assertEqual(str(reply), text)

    def test_create_relpy_length_is_more_than_20characters(self):
        comment = self.__set_post_and_comment_data()
        text = 'a' * 21
        data = {
            'name': 'reply_user',
            'text': text,
            'target': comment,
        }
        reply = self.__create_and_save(data)

        self.assertEqual(self.model.objects.count(), 1)
        self.assertEqual(self.model.objects.get(pk=reply.pk).target.pk, comment.pk)
        self.assertEqual(str(reply), text[:20])
