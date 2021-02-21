from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='has_perm')
def has_perm(user, permission_name):
    return user.has_perm(permission_name)
