import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator



from .models import *


def index(request):
    return render(request, "network/index.html")

@csrf_exempt
@login_required
def posts(request):

    if request.method != "POST":
        return JsonResponse({'error': 'POST request required.'}, status=400)

    user = request.user
    data = json.loads(request.body)
    body = data.get("body","")

    post = Post(
        user = user,
        body = body
        )
    post.save()

    return JsonResponse({"message": "Post created succesfully!"}, status=201)

@csrf_exempt
def pick(request, pick):

    user = request.user

    data = json.loads(request.body)
    page_num = data.get("page","")

    if pick == 'all':
        posts = Post.objects.all()
    elif pick == 'followers':
        users = Follow.objects.filter(user=user)
        posts = Post.objects.filter(user__in=[e.following.id for e in users])
    elif pick == 'own':
        posts = Post.objects.filter(user=user)
    else:
        user = User.objects.get(username=pick)
        posts = Post.objects.filter(user=user.id)
    posts = posts.order_by("-timestamp").all()
    
    p = Paginator(posts, 10)
    try:
        page = p.page(page_num)
    except:
        page = p.page(1)

    p_end = p.num_pages

    results = {"lastpage": p_end, "posts":[entry.serialize() for entry in page]}

    return JsonResponse(results, safe=False)

@csrf_exempt
def edit(request, edit):
    
    user = request.user
    if request.method == "PUT":
        data = json.loads(request.body)
        body = data.get("body","")
        post = Post.objects.get(id=edit)
        if post.user == user:
            post.body = body;
        post.save()
        return JsonResponse({"message": "Post edited succesfully!"}, status=201)

@csrf_exempt
def like(request, id_post):
    
    user = request.user
    if request.method == "PUT":
        try:
            liked = Like.objects.get(post=id_post, user=user)
            liked.delete()
            post = Post.objects.get(pk=id_post)
            post.like = post.like-1
            post.save()
            return JsonResponse({"message": "unliked"}, status=201)
        except:

            like = Like(
                post = Post.objects.get(pk=id_post),
                user = user)
            like.save();
            post = Post.objects.get(pk=id_post)
            post.like = post.like+1
            post.save()
            return JsonResponse({"message": "liked"}, status=201)
    elif request.method == "GET":
        try:
            liked = Like.objects.get(post=id_post, user=user)
            return JsonResponse({"message": "liking"}, status=201)
        except:
            return JsonResponse({"message": "not liking"}, status=201)
    else:
        return JsonResponse({"message": "Error, only PUT or GET!"}, status=404)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def numbers(request, username):
    user = User.objects.get(username=username);
    follow = Follow.objects.filter(Q(user=user) | Q(following=user));
    
    return JsonResponse([entry.serialize() for entry in follow], safe=False)

@csrf_exempt
@login_required
def follow(request, username):
    user = User.objects.get(username=username);
    currentUser = User.objects.get(username=request.user);
    if request.method == 'POST':
        if user != currentUser:
            try:
                entry = Follow.objects.get(user=request.user, following=user);
                return JsonResponse({"message": "Already follwoing -> Error!"})
            except Follow.DoesNotExist:
                newFollow = Follow(
                    user=request.user,
                    following=user
                )
                newFollow.save()
                return JsonResponse({"message": "changed to following"}, status=201)
        else:
            return JsonResponse({"message": "User is looking at his own profile"}, status=201)
    elif request.method == 'PUT':
        entry = Follow.objects.get(user=request.user, following=user);
        entry.delete();
        return JsonResponse({"message": "changed to unfollowing"}, status=201)
    elif request.method == 'GET':
        try:
            entry = Follow.objects.get(user=currentUser, following=user)
            return JsonResponse({"message": "following"}, status=201)
        except Follow.DoesNotExist:
            return JsonResponse({"message": "not following"}, status=201)
    else:
        return JsonResponse({"error": "GET, PUT or PUSH request required."}, status=400)
        
