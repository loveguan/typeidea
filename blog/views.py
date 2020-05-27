from django.shortcuts import render
from django.http import HttpResponse

from .models import Tag, Post, Category
from config.models import SideBar


# Create your views here.

def post_list(request, category_id=None, tag_id=None):
    tag = None
    category = None

    if tag_id:
        post_list, tag = Post.get_by_tag(tag_id)
    elif category_id:
        post_list, category = Post.get_by_category(category_id)
    else:
        post_list = Post.latest_posts()
    context = {
        'category': category,
        'tag': tag,
        'post_list': post_list,
        'side_bars': SideBar.get_all(),
    }
    # 获取导航条
    context.update(Category.get_nvas())
    return render(request, 'blog/list.html', context=context)


def post_detail(request, post_id=None):
    try:
        post = Post.objects.get(id=post_id)
    except:
        post = None
    context = {
        'post': post,
        'side_bars': SideBar.get_all(),
    }
    context.update(Category.get_nvas())
    return render(request, 'blog/detail.html', context=context)


from django.views.generic import DetailView, ListView

from django.views import View


class MyView(View):
    def get(self, request):
        print(self)
        return HttpResponse('result')


class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'side_bars': SideBar.get_all(),
        })
        context.update(Category.get_nvas())

        return context


class IndexView(CommonViewMixin, ListView):
    queryset = Post.latest_posts()
    paginate_by = 1
    context_object_name = 'post_list'
    template_name = 'blog/list.html'


from django.shortcuts import get_list_or_404


class CategoryView(IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_list_or_404(Category, pk=category_id)
        context.update({
            'category': category,
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_list_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


from comment.froms import CommentForm
from comment.models import Comment

from django.db.models import Q, F

from datetime import date
from django.core.cache import cache


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.latest_posts()
    context_object_name = 'post'
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, *kwargs)
        # Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1, uv=F('uv') + 1)
        # 调试
        self.handle_visited()
        from django.db import connection
        print(connection.queries)
        return response

    #  换到templete中去了comment_block.py
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context.update(
    #         {
    #             'comment_form': CommentForm,
    #             'comment_list': Comment.get_by_target(self.request.path),
    #         }
    #     )
    #
    #     return context

    def handle_visited(self):
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        print(uid)
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)
        if not cache.get(pv_key):
            increase_pv=True
            cache.set(pv_key,1,1*60)
        if not cache.get(uv_key):
            increase_uv=True
            cache.set(uv_key,1,24*60*60)
        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv')+1,uv=F('uv')+1)
        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv')+1)
        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(uv=F('uv')+1)



from django.db.models import Q


class SearchView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'keyword': self.request.GET.get('keyword', '')
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keywork')
        if not keyword:
            return queryset
        else:
            return queryset.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword))


class AuthorView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)


from django.db import connection
