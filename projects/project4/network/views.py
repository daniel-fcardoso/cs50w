from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

import json

from .models import User, Post


def index(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        content = request.POST.get("content")

        if content:
            Post.objects.create(
                user=request.user,
                content=content
            )

        return HttpResponseRedirect(reverse("index"))

    posts = Post.objects.all().order_by("-timestamp")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    followed_users = request.user.following.all()

    posts = Post.objects.filter(
        user__in=followed_users
    ).order_by("-timestamp")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "page_obj": page_obj
    })


def profile(request, username):
    profile_user = User.objects.get(username=username)

    posts = Post.objects.filter(
        user=profile_user
    ).order_by("-timestamp")

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    is_following = False

    if request.user.is_authenticated:
        is_following = request.user.following.filter(
            id=profile_user.id
        ).exists()

    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "page_obj": page_obj,
        "followers_count": profile_user.followers.count(),
        "following_count": profile_user.following.count(),
        "is_following": is_following,
    })


def follow_toggle(request, username):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    profile_user = User.objects.get(username=username)

    if request.user == profile_user:
        return HttpResponseRedirect(
            reverse("profile", args=[username])
        )

    if request.method == "POST":
        if request.user.following.filter(id=profile_user.id).exists():
            request.user.following.remove(profile_user)
        else:
            request.user.following.add(profile_user)

    return HttpResponseRedirect(
        reverse("profile", args=[username])
    )


def edit_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Authentication required."
        }, status=401)

    if request.method != "PUT":
        return JsonResponse({
            "error": "PUT request required."
        }, status=405)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({
            "error": "Post not found."
        }, status=404)

    if post.user != request.user:
        return JsonResponse({
            "error": "You cannot edit this post."
        }, status=403)

    data = json.loads(request.body)
    content = data.get("content", "").strip()

    if not content:
        return JsonResponse({
            "error": "Post content cannot be empty."
        }, status=400)

    post.content = content
    post.save()

    return JsonResponse({
        "message": "Post updated successfully.",
        "content": post.content
    })


def like_post(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Authentication required."
        }, status=401)

    if request.method != "POST":
        return JsonResponse({
            "error": "POST request required."
        }, status=405)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({
            "error": "Post not found."
        }, status=404)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    return JsonResponse({
        "liked": liked,
        "likes_count": post.likes.count()
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

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

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(
                username,
                email,
                password
            )

            user.save()

        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })

        login(request, user)

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "network/register.html")
