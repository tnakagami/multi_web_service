from django import template

register = template.Library()

@register.filter
def filtered_username(user, username):
    return user.filter(username=username)

@register.filter
def filtered_viewname(user, viewname):
    return user.filter(viewname=viewname)

@register.filter
def filtered_owner(relationship, pk):
    return relationship.filter(owner__pk=pk)

@register.filter
def filtered_follower(relationship, pk):
    return relationship.filter(follower__pk=pk)

@register.filter
def get_first_element(queryset):
    return queryset.first()

@register.filter
def ignored_userpk(queryset, pk):
    return queryset.exclude(pk=pk)
