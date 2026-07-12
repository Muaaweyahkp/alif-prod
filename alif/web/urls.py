from django.urls import path
from . import views

app_name = "web"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("blogs/", views.BlogListView.as_view(), name="blogs"),
    path("blog-details/<slug:slug>/", views.blog_details, name="blog_details"),
    path("shop/", views.ShopView.as_view(), name="shop"),
    path("product/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]