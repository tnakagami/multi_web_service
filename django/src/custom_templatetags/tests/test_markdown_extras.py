from django.test import TestCase
from custom_templatetags import markdown_extras.py

class MarkdownExtras(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

class Markdown2HtmlTests(MarkdownExtras):
    def test_empty_text(self):
        text = ""
        ret = markdown_extras.markdown2html(text)
        self.assertEqual(ret, text)

    def test_h1_tag(self):
        text = "# A"
        ret = markdown_extras.markdown2html(text)
        self.assertTrue('h1' in ret)
        self.assertTrue('A' in ret)

class Markdown2HtmlxWithEscapeTests(MarkdownExtras):
    def test_empty_text(self):
        text = ""
        ret = markdown_extras.markdown2html_with_escape(text)
        self.assertEqual(ret, text)

    def test_text_with_script(self):
        text = "# A\n<script>alert('C');</script>"
        ret = markdown_extras.markdown2html_with_escape(text)
        self.assertTrue('&lt;script&gt;' in ret)
        self.assertTrue('&lt;/script&gt;' in ret)

    def test_text_with_a_tag(self):
        text = "# A\n<a href=\"ccc\">here</a>"
        ret = markdown_extras.markdown2html_with_escape(text)
        self.assertTrue('&lt;a href="ccc"&gt;' in ret)
        self.assertTrue('&lt;/a&gt;' in ret)
