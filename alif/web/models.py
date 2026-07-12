from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from multiselectfield import MultiSelectField


class Slider(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="slider/")
    sub_head = models.CharField(max_length=400, blank=True, null=True)
    slide_class = models.CharField(max_length=50, blank=True, null=True)  # Added for custom slide classes

    class Meta:
        verbose_name = "Slider"
        verbose_name_plural = "Sliders"
        ordering = ("title",)

    def __str__(self):
        return str(self.title)

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(
        "category",
        blank=True,
        null=True,
        upload_to="categories/",
        help_text="The recommended size is 120x120 pixels.",
    )
    status = models.CharField(
        max_length=20,
        choices=(("Published", "Published"), ("Unpublished", "Unpublished")),
        default="Published",
    )

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ("name",)

    def get_product_count(self):
        return self.categoryproduct_set.count()

    def get_published_subcategories(self):
        return self.subcategories.filter(status="Published")

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(
        "subcategory",
        blank=True,
        null=True,
        upload_to="subcategories/",
        help_text="The recommended size is 120x120 pixels.",
    )
    status = models.CharField(
        max_length=20,
        choices=(("Published", "Published"), ("Unpublished", "Unpublished")),
        default="Published",
    )

    class Meta:
        verbose_name = _("SubCategory")
        verbose_name_plural = _("SubCategories")
        ordering = ("name",)

    def get_product_count(self):
        return self.categoryproducts.count()

    def get_published_products(self):
        return self.categoryproducts.filter(status="Published")

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while SubCategory.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} > {self.name}"

class Product(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="categoryproducts")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField(
        "product",
        blank=True,
        null=True,
        upload_to="products/",
        help_text="The recommended size is 300x300 pixels.",
    )
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=(("Published", "Published"), ("Unpublished", "Unpublished")),
        default="Published",
    )
    is_all_products = models.BooleanField(default=False)
    is_best_selling = models.BooleanField(default=False)
    is_on_selling = models.BooleanField(default=False)
    is_top_rating = models.BooleanField(default=False)
    sizes = MultiSelectField(
        choices=[
            ("XS", "XS"),
            ("S", "S"),
            ("M", "M"),
            ("L", "L"),
            ("XL", "XL"),
            ("XXL", "XXL"),
        ],
        max_length=20,
        blank=True,
        default="",
        help_text="Select all applicable sizes for this product.",
    )

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ("name",)

    def get_category(self):
        return self.subcategory.category

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.subcategory.name})"

class FlashSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="flash_sales")
    discount_percentage = models.PositiveIntegerField(default=0, help_text="Discount percentage (e.g., 25)")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Flash Sale")
        verbose_name_plural = _("Flash Sales")
        ordering = ("-start_time",)

    def __str__(self):
        return f"{self.product.name} - {self.discount_percentage}% Off"

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=100)
    reviewer_role = models.CharField(max_length=100)
    review_text = models.TextField()
    rating = models.PositiveIntegerField(default=5, validators=[MaxValueValidator(5)])
    image = models.ImageField(
        "reviewer",
        blank=True,
        null=True,
        upload_to="reviews/",
        help_text="Reviewer image (recommended size: 100x100 pixels)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.reviewer_name}'s review for {self.product.name}"

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(
        "blog",
        upload_to="blogs/",
        help_text="Recommended size: 300x200 pixels",
    )
    content = models.TextField()
    author = models.CharField(max_length=100, default="Admin")
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(("Published", "Published"), ("Unpublished", "Unpublished")),
        default="Published",
    )

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):
        if not self.slug or self.slug == "":
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Client(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    testimonial = models.TextField()
    image = models.ImageField(
        "client",
        upload_to="clients/",
        help_text="Recommended size: 100x100 pixels",
    )
    status = models.CharField(
        max_length=20,
        choices=(("Published", "Published"), ("Unpublished", "Unpublished")),
        default="Published",
    )

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ("name",)

    def __str__(self):
        return self.name