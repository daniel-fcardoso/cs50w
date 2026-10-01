from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watchlist/<int:listing_id>", views.watchlist_toggle, name="watchlist_toggle"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listing/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("listing/<int:listing_id>/comment", views.add_comment, name="add_comment"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.category, name="category"),
]
