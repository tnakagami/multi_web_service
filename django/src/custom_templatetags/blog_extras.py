from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions import Extension

register = template.Library()

@register.filter
def markdown2html(text):
    """
    convert markdown to html
    """
    html = markdown.markdown(text, extensions=settings.MARKDOWN_EXTENSIONS)

    return mark_safe(html)


class EscapeHtml(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.deregister('html_block')
        md.inlinePatterns.deregister('html')


@register.filter
def markdown_to_html_with_escape(text):
    """
    convert markdown to escapsed html
    """
    extensions = settings.MARKDOWN_EXTENSIONS + [EscapeHtml()]
    html = markdown.markdown(text, extensions=extensions)

    return mark_safe(html)
