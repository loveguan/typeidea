from django.contrib import admin
from .models import Post, Category, Tag
from django.urls import reverse
from django.utils.html import format_html
from .adminforms import PostAdminForm
from typeidea.custom_site import custom_site
from typeidea.BaseOwnerAdmin import BaseOwnerAdmin


# Register your models here.
class PostInline(admin.TabularInline):
    fields = ('title', 'desc')
    extra = 1
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]
    list_display = ('name', 'status', 'is_nav', 'created_time', 'post_count', 'operator')
    fields = ('name', 'status', 'is_nav')

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '数量'

    def operator(self, obj):
        # return format_html('<a href="{}">编辑</a>', reverse('admin:blog_category_change', args=(obj.id,)))
        return format_html('<a href="{}">编辑</a>', reverse('cus_admin:blog_category_change', args=(obj.id,)))

    operator.short_description = '操作'

    # def save_model(self, request, obj, form, change):
    #     obj.owner = request.user
    #     return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')
    #
    # def save_model(self, request, obj, form, change):
    #     obj.owner = request.user
    #     return super(TagAdmin, self).save_model(request, obj, form, change)


# 定制文章中的过滤器，只显示自己创建的过滤器

class CategoryOwnerFilter(admin.SimpleListFilter):
    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=category_id)
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    # 显示内容
    list_display = [
        'title', 'category', 'status',
        'created_time', 'operator', 'owner',
    ]

    list_display_links = []
    # 引用前边定制i的过滤方法
    list_filter = [CategoryOwnerFilter, 'tag']
    search_fields = ['title', 'category__name']
    actions_on_top = True
    actions_on_bottom = True
    save_on_top = True
    exclude = ('owner',)

    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )

    # 定制操作方法
    def operator(self, obj):
        return format_html('<a href="{}">编辑</a>', reverse('cus_admin:blog_post_change', args=(obj.id,)))
        # return format_html('<a href="{}">编辑</a>', reverse('admin:blog_post_change', args=(obj.id,)))

    operator.short_description = '操作'

    # 定制只展示自己的文章,加了一个过滤的条件
    # def get_queryset(self, request):
    #     qs = super(PostAdmin, self).get_queryset(request)
    #     return qs.filter(owner=request.user)

    # 控制页面布局和fields只能一个存在

    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('collapse',),
            'fields': ('tag',),
        })
    )

    # 修改复选框的样式，解决自带的好的问题
    # filter_horizontal = ('tag',)
    filter_vertical = ('tag',)
    # 定制样式
    form = PostAdminForm

    # def save_model(self, request, obj, form, change):
    #     obj.owner = request.user
    #     return super(PostAdmin, self).save_model(request, obj, form, change)
