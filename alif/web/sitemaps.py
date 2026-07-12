from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product  # Adjust to your model import

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['web:index', 'web:about', 'web:shop', 'web:contact']

    def location(self, item):
        return reverse(item)

class ProductSitemap(Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Product.objects.all()

    def location(self, item):
        return reverse('web:product_detail', kwargs={'slug': item.slug})