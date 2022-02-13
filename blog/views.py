# -*- codding: utf-8 -*-
import re
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.defaults import page_not_found
from django.http import Http404
from .models import Post, PostCategory
from .forms import AddPostForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

# Create your views here.
def paginate(request, posts):
    page = request.GET.get('page')
    paginator = Paginator(posts, 2)
    try:
        posts_page = paginator.page(page)
    except PageNotAnInteger:
        posts_page = paginator.page(1)
    except EmptyPage:
        posts_page = paginator.page(paginator.num_pages)
    return posts_page


def main_page(request):
    if request.user.is_authenticated:
        posts = Post.objects.all().order_by('published_date')
    else: posts = ""
    categories = PostCategory.objects.all()
    posts = paginate(request, list(posts))
    context = {
        'posts': posts,
        'sidebar': categories
    }
    return render(request, 'main_page.html', context)

def add_post(request):
    add_post_form=None
    if request.user.is_authenticated:
        if request.method == "POST":
            add_post_form = AddPostForm(request.POST, request.FILES)
            if add_post_form.is_valid():
                print("Valid!")
                url = request.POST.get('post_slug')
                new_post = add_post_form.save()
                new_post.save()
                print(url)
                return redirect(f"/{url}")
            else: 
                print("unValid!")
        else:
            add_post_form = AddPostForm()
    context = {
        'post_form': add_post_form
    }
    return render(request, 'add_post.html', context)


def search_post(request):
    posts = None
    if request.method == "POST":
        searched = request.POST.get('searchpost')
        posts = Post.objects.filter(title__icontains=searched)    
    sidebar = PostCategory.objects.all()
    return render(request, 
                  "search_result.html", 
                  {"sidebar": sidebar,
                   "posts": posts })

def single_slug(request, single_slug):
    sidebar = PostCategory.objects.all()
    categories = [cat.category_slug  for cat in PostCategory.objects.all()]
    if single_slug in categories:
        category_posts = Post.objects.filter(post_category__category_slug=single_slug)
        return render(request, 'category.html', {'posts':category_posts,
                      'sidebar': sidebar})
    posts_slug = [ p.post_slug for p in Post.objects.all()]
    if single_slug in posts_slug:
        post = Post.objects.get(post_slug=single_slug)
        context = {'post': post,
                   'sidebar': sidebar}
        return render(request, 'post_view.html', context)
    else:
        raise Http404
        #page_not_found(request, 'Article not found!')


def register(request):
    if request.method =="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            print("Sucsess IN REGISTER!!!")
            user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Створено новий акаунт: {username}")
            login(request, user)
            return redirect("/")
        else:
            print("ERRORS IN REGISTER!!!")
            for msg in form.error_messages:
                messages.error(request, f"{msg} : {form.error_messages[msg]} ")
            return render(request, 'register.html', context={'form': form})
    form = UserCreationForm
    context = {'form': form}
    return render(request, 'register.html', context)

def logout_request(request):
    logout(request)
    return redirect("/")

def login_request(request):
    if request.method =="POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
    form = AuthenticationForm()
    context = {'form': form}
    return render(request, "login.html", context)
