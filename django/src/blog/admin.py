from django.contrib import admin
from . import models

class ReplyInline(admin.StackedInline):
    model = models.Reply
    extra = 5

class CommentAdmin(admin.ModelAdmin):
    inlines = [ReplyInline]

class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text',)
    list_display = ['title', 'is_public', 'updated_at', 'created_at', 'title_len']
    list_filter = ['is_public', 'tags']
    ordering = ('-updated_at',)

    def title_len(self, instance):
        return len(instance.title)

    title_len.short_description = 'length of title'

admin.site.register(models.Post, PostAdmin)
admin.site.register(models.Comment, CommentAdmin)
admin.site.register(models.Reply)
admin.site.register(models.Tag)
