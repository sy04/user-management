from django.shortcuts import render, redirect
from .forms import RegisterForm, PostForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from .models import Post

@login_required(login_url="/login")
def home(req):
  posts = Post.objects.all()

  if req.method == "POST":
    post_id = req.POST.get("post-id")
    user_id = req.POST.get("user-id")

    if post_id:
      post = Post.objects.filter(id=post_id).first()
      if post and (post.author == req.user or req.user.has_perm("main.delete_post")):
        post.delete()
    elif user_id:
      user = User.objects.filter(id=user_id).first()
      if user and req.user.is_staff:
        try:
          group = Group.objects.get(name='default')
          group.user_set.remove(user)
        except:
          pass

        try:
          group = Group.objects.get(name="mod")
          group.user_set.remove(user)
        except:
          pass

  return render(req, 'main/home.html', {"posts": posts})

@login_required(login_url="/login")
@permission_required("main.add_post", login_url="/login", raise_exception=True)
def create_post(req):
  if req.method == 'POST':
    form = PostForm(req.POST)
    if form.is_valid():
      post = form.save(commit=False)
      post.author = req.user
      post.save()

      return redirect('/home')
  else:
    form = PostForm()

  return render(req, 'main/create_post.html', {"form": form})

def sign_up(req):
  if req.method == 'POST':
    form = RegisterForm(req.POST)
    if form.is_valid():
      user = form.save()
      login(req, user)
      return redirect('/home')
  else:
    form = RegisterForm()

  return render(req, 'registration/sign_up.html', {"form": form})