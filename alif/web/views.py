from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Slider, Category, SubCategory, Product, FlashSale, Review, Blog, Client
from django.utils import timezone
from urllib.parse import quote
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse

def index(request):
    sliders = Slider.objects.all()
    flash_sales = FlashSale.objects.filter(is_active=True, end_time__gte=timezone.now())
    flash_sale_end_time = flash_sales.first().end_time.isoformat() if flash_sales.exists() else None
    reviews = Review.objects.all()
    blogs = Blog.objects.filter(status="Published")[:3]
    clients = Client.objects.filter(status="Published")
    
    # Fetch exactly 8 products for each category
    best_sellers = Product.objects.filter(status="Published", is_best_selling=True)[:8]
    on_selling = Product.objects.filter(status="Published", is_on_selling=True)[:8]
    top_rated = Product.objects.filter(status="Published", is_top_rating=True)[:8]
    
    # Combine all for "All Products" filter, ensuring no duplicates
    all_products = list(dict.fromkeys(list(best_sellers) + list(on_selling) + list(top_rated)))
    
    context = {
        'sliders': sliders,
        'flash_sales': flash_sales,
        'flash_sale_end_time': flash_sale_end_time,
        'reviews': reviews,
        'blogs': blogs,
        'clients': clients,
        'categories': Category.objects.filter(status="Published"),
        'products': all_products,  # All 24 products for "All Products" filter
        'best_sellers': best_sellers,  # 8 best-selling products
        'on_selling': on_selling,  # 8 on-selling products
        'top_rated': top_rated,  # 8 top-rated products
    }
    return render(request, 'web/index.html', context)

def about(request):
    reviews = Review.objects.all()
    context = {'reviews': reviews}
    return render(request, 'web/about.html', context)

def contact(request):
    return render(request, 'web/contact.html')

class BlogListView(ListView):
    model = Blog
    template_name = "web/blogs.html"
    context_object_name = "blogs"
    queryset = Blog.objects.filter(status="Published").order_by('-created_at')

def blog_details(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status="Published")
    recent_posts = Blog.objects.filter(status="Published").order_by('-created_at')[:3]
    return render(request, 'web/blog-details.html', {'blog': blog, 'recent_posts': recent_posts})

class ShopView(ListView):
    model = Product
    template_name = "web/shop.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.filter(status="Published")
        category_slug = self.request.GET.get('category')
        subcategory_slug = self.request.GET.get('subcategory')
        size = self.request.GET.get('size')
        status = self.request.GET.get('status')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug, status="Published")
            queryset = Product.objects.filter(subcategory__category=category, status="Published")
        elif subcategory_slug:
            subcategory = get_object_or_404(SubCategory, slug=subcategory_slug, status="Published")
            queryset = subcategory.get_published_products()
        elif size:
            queryset = queryset.filter(sizes__contains=[size])
        elif status:
            queryset = queryset.filter(status=status)

        # Filter by product type booleans if provided
        selected_types = self.request.GET.getlist('product_types')
        if selected_types:
            filters = {}
            for type_name in selected_types:
                if type_name == "All Products":
                    filters['is_all_products'] = True
                elif type_name == "Best Selling":
                    filters['is_best_selling'] = True
                elif type_name == "On Selling":
                    filters['is_on_selling'] = True
                elif type_name == "Top Rating":
                    filters['is_top_rating'] = True
            if filters:
                queryset = queryset.filter(**filters).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(status="Published")
        context["subcategories"] = SubCategory.objects.filter(status="Published")
        context["size_options"] = [
            ("XS", "XS"),
            ("S", "S"),
            ("M", "M"),
            ("L", "L"),
            ("XL", "XL"),
            ("XXL", "XXL"),
        ]
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = "web/shop-details.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        message_text = f"Hi! I’m interested in buying or enquiring about {product.name} from Alif Uniforms! 😊\n- Product: {product.name}\n- Category: {product.subcategory.category.name}\n- Subcategory: {product.subcategory.name}\nPlease let me know the next steps!"
        context["whatsapp_link"] = f"https://wa.me/+971509173282?text={quote(message_text)}"
        context["reviews"] = product.reviews.all()  # Keep reviews for the review section
        context["sizes"] = product.sizes  # Pass the sizes MultiSelectField to the template
        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        reviewer_name = request.POST.get("reviewer_name")
        review_text = request.POST.get("review_text")
        rating = request.POST.get("rating")

        if not all([reviewer_name, review_text, rating]):
            messages.error(request, "All fields are required.")
        else:
            try:
                rating = int(rating)
                if not 1 <= rating <= 5:
                    raise ValidationError("Rating must be between 1 and 5.")
                Review.objects.create(
                    product=product,
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    rating=rating
                )
                messages.success(request, "Review submitted successfully!")
            except ValidationError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, "An error occurred while submitting the review.")
        return redirect("web:product_detail", slug=product.slug)
    
def robots_txt(request):
    return HttpResponse("User-agent: *\n", content_type="text/plain")