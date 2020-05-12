from django.contrib import admin

# Register your models here.
from .models import Comment
from typeidea.custom_site import custom_site
from typeidea.BaseOwnerAdmin import BaseOwnerAdmin


@admin.register(Comment, site=custom_site)
class CommentAdmin(BaseOwnerAdmin):
    list_display = ('target', 'nickname', 'content', 'website', 'created_time')
