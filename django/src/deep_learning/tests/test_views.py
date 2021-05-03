from unittest import mock
from django.test import TestCase
from django.urls import reverse, resolve
from deep_learning import views

class DeepLearningView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def chk_class(self, resolver, class_view):
        self.assertEqual(resolver.func.__name__, class_view.__name__)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class TopPageViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:index')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/')
        self.chk_class(resolver, views.TopPageView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class WhatDockerViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:what_docker')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/what_docker/')
        self.chk_class(resolver, views.WhatDockerView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class DockerEnvironmentViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:docker_environment')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/docker_environment/')
        self.chk_class(resolver, views.DockerEnvironmentView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class UseDockerViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:use_docker')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/use_docker/')
        self.chk_class(resolver, views.UseDockerView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class JupyterNotebookViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:jupyter_notebook')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/jupyter_notebook/')
        self.chk_class(resolver, views.JupyterNotebookView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class TutorialMnistDatasetViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:tutorial_mnist_dataset')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/tutorial_mnist_dataset/')
        self.chk_class(resolver, views.TutorialMnistDatasetView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

class HandwritingRecognitionViewTests(DeepLearningView):
    def setUp(self):
        super().setUp()
        self.url = reverse('deep_learning:handwriting_recognition')

    def test_resolve_url(self):
        resolver = resolve('/deep_learning/handwriting_recognition/')
        self.chk_class(resolver, views.HandwritingRecognitionView)

    def test_valid_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
