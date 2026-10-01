from decimal import Decimal, InvalidOperation

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import User, Listing, Bid, Comment


def index(request):
    listings = Listing.objects.filter(active=True)

    for listing in listings:
        listing.current_bid = listing.bids.order_by("-amount").first()

    return render(request, "auctions/index.html", {
        "listings": listings
    })


@login_required
def create_listing(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image_url = request.POST.get("image_url", "").strip()
        category = request.POST.get("category", "").strip()

        if not title or not description:
            return render(request, "auctions/create.html", {
                "message": "Title and description are required."
            })

        try:
            starting_bid = Decimal(request.POST["starting_bid"])

            if starting_bid <= 0:
                raise ValueError

        except (InvalidOperation, ValueError):
            return render(request, "auctions/create.html", {
                "message": "Starting bid must be a positive number."
            })

        listing = Listing(
            title=title,
            description=description,
            starting_bid=starting_bid,
            image_url=image_url,
            category=category,
            creator=request.user,
            active=True
        )

        listing.save()

        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html")


def listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    highest_bid = listing.bids.order_by("-amount").first()
    comments = listing.comments.all()

    winner = None

    if not listing.active and highest_bid:
        winner = highest_bid.bidder

    if request.method == "POST":

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))

        if not listing.active:
            return HttpResponseRedirect(
                reverse("listing", args=[listing.id])
            )

        try:
            amount = Decimal(
                request.POST.get("bid", "").strip()
            )

        except (InvalidOperation, ValueError):
            in_watchlist = False

            if request.user.is_authenticated:
                in_watchlist = listing in request.user.watchlist.all()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid,
                "comments": comments,
                "in_watchlist": in_watchlist,
                "winner": winner,
                "message": "Please enter a valid bid amount."
            })

        if highest_bid:
            invalid_bid = amount <= highest_bid.amount
            minimum_bid = highest_bid.amount

            error_message = (
                f"Your bid must be greater than ${minimum_bid:.2f}."
            )

        else:
            invalid_bid = amount < listing.starting_bid
            minimum_bid = listing.starting_bid

            error_message = (
                f"Your bid must be at least ${minimum_bid:.2f}."
            )

        if invalid_bid:
            in_watchlist = False

            if request.user.is_authenticated:
                in_watchlist = listing in request.user.watchlist.all()

            return render(request, "auctions/listing.html", {
                "listing": listing,
                "highest_bid": highest_bid,
                "comments": comments,
                "in_watchlist": in_watchlist,
                "winner": winner,
                "message": error_message
            })

        bid = Bid(
            amount=amount,
            bidder=request.user,
            listing=listing
        )

        bid.save()

        return HttpResponseRedirect(
            reverse("listing", args=[listing.id])
        )

    in_watchlist = False

    if request.user.is_authenticated:
        in_watchlist = listing in request.user.watchlist.all()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "highest_bid": highest_bid,
        "comments": comments,
        "in_watchlist": in_watchlist,
        "winner": winner
    })


@login_required
@require_POST
def watchlist_toggle(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if listing in request.user.watchlist.all():
        request.user.watchlist.remove(listing)
    else:
        request.user.watchlist.add(listing)

    return HttpResponseRedirect(
        reverse("listing", args=[listing.id])
    )


@login_required
@require_POST
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    if request.user == listing.creator:
        listing.active = False
        listing.save()

    return HttpResponseRedirect(
        reverse("listing", args=[listing.id])
    )


@login_required
@require_POST
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    content = request.POST.get("content", "").strip()

    if content:
        comment = Comment(
            content=content,
            commenter=request.user,
            listing=listing
        )

        comment.save()

    return HttpResponseRedirect(
        reverse("listing", args=[listing.id])
    )


@login_required
def watchlist(request):
    listings = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categories(request):
    categories = Listing.objects.values_list(
        "category",
        flat=True
    ).exclude(
        category=""
    ).distinct()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })


def category(request, category_name):
    listings = Listing.objects.filter(
        category=category_name,
        active=True
    )

    return render(request, "auctions/category.html", {
        "category_name": category_name,
        "listings": listings
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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })

    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
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
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })

        login(request, user)

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/register.html")
