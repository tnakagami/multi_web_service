from django import template
from django.template.defaultfilters import stringfilter

import markdown as md

register = template.Library()

@register.simple_tag
def url_replace(request, field, value):
    """
    replace field of GET parameter to value
    """
    url_dict = request.GET.copy()
    url_dict[field] = str(value)

    return url_dict.urlencode()

@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])
