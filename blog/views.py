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
    pass

class IndexView(ListView):
    queryset = Post.latest_posts()
    paginate_by = 1
    context_object_name = 'post_list'
    template_name = 'blog/list.html'

