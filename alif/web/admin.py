from django.contrib import admin
from django.utils.html import mark_safe
from .models import Slider, Category, SubCategory, Product, FlashSale, Review, Blog, Client

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'sub_head', 'slide_class', 'image_thumbnail')
    search_fields = ('title', 'sub_head', 'slide_class')

    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'image_thumbnail', 'get_subcategory_count')
    search_fields = ('name', 'slug')
    list_filter = ('status',)
    prepopulated_fields = {'slug': ('name',)}  # ✅ auto slug


    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'

    def get_subcategory_count(self, obj):
        return obj.subcategories.count()
    get_subcategory_count.short_description = 'Subcategories'

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'image_thumbnail', 'get_product_count')
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('status', 'category')
    prepopulated_fields = {'slug': ('name',)}  # ✅ auto slug


    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'

    def get_product_count(self, obj):
        return obj.get_published_products().count()
    get_product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'status', 'is_best_selling', 'is_on_selling', 'is_top_rating', 'image_thumbnail')
    search_fields = ('name', 'slug', 'subcategory__name', 'description')
    list_filter = ('status', 'subcategory__category', 'is_all_products', 'is_best_selling', 'is_on_selling', 'is_top_rating')
    prepopulated_fields = {'slug': ('name',)}  # ✅ auto slug
    filter_horizontal = ()  # No filter_horizontal needed for MultiSelectField



    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'

@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_percentage', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'reviewer_name', 'rating', 'created_at', 'image_thumbnail')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer_name', 'review_text', 'product__name')

    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'status', 'image_thumbnail')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content', 'author')
    prepopulated_fields = {'slug': ('title',)}

    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'status', 'image_thumbnail')
    list_filter = ('status',)
    search_fields = ('name', 'role', 'testimonial')

    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return "No Image"
    image_thumbnail.short_description = 'Image'