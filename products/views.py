from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from .models import Product, Category, Rating, Comment
from .forms import ProductForm, RatingForm
from .forms import CommentForm
# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            elif sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def edit_comment(request, product_id, comment_id):
    """
    Display an individual comment for edit.
    *Context*

    `product`
        An instance of :model:products.Product.
    `comment`
        A single comment related to the product.
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    product = get_object_or_404(Product, pk=product_id)

    if request.method == "POST":
        comment_form = CommentForm(data=request.POST, instance=comment)

        if comment_form.is_valid() and comment.author == request.user:
            comment = comment_form.save(commit=False)
            comment.product = product
            comment.approved = False
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment Updated!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.add_message(request, messages.ERROR, 'Error updating comment!')

    else:
        comment_form = CommentForm(instance=comment)

    context = {
        'product': product,
        'comment': comment,
        'comment_form': comment_form,
    }
    return render(request, 'products/edit_comment.html', context)


def delete_comment(request, product_id, comment_id):
    """
    Delete an individual comment.

    **Context**

    ``product``
        An instance of :model:`products.Product`.
    ``comment``
        A single comment related to the product.
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    product = get_object_or_404(Product, pk=product_id)

    if comment.author == request.user:
        comment.delete()
        messages.add_message(request, messages.SUCCESS, 'Comment deleted!')
    else:
        messages.add_message(request, messages.ERROR, 'You can only delete your own comments!')

    return redirect(reverse('product_detail', args=[product.id]))


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = request.user.favorite.filter(id=product_id).exists()

    ratings = product.rating_set.all()
    average_rating = product.average_rating()

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST' and 'rate' in request.POST:
        form = RatingForm(request.POST)
        if user_rating:
            messages.error(request, 'You have already rated this product.')
        elif form.is_valid():
            rating = form.save(commit=False)
            rating.product = product
            rating.user = request.user
            rating.save()
            messages.success(request, 'Rating submitted!')
            return redirect('product_detail', product_id=product.id)
    else:
        form = RatingForm()

    comments = product.comments.all()
    comment_count = product.comments.count()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.product = product
            comment.save()
            messages.add_message(request, messages.SUCCESS, 'Comment submitted')
            return redirect('product_detail', product_id=product.id)
    else:
        comment_form = CommentForm()

    context = {
        'product': product,
        'is_in_wishlist': is_in_wishlist,
        'ratings': ratings,
        'average_rating': average_rating,
        'form': form,
        'user_rating': user_rating,
        'comments': comments,
        'comment_count': comment_count,
        'comment_form': comment_form,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def delete_rating(request, product_id):
    user = request.user
    rating = get_object_or_404(Rating, user=user, product_id=product_id)
    rating.delete()
    messages.add_message(request, messages.SUCCESS, 'Rating deleted!')
    return redirect(reverse('product_detail', args=[product_id]))


@login_required
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()
    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ Edit a product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """ Delete a product from the store """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))


def wishlist(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to view your wishlist.')
        return redirect('account_login')

    products_in_wishlist = request.user.favorite.all()

    context = {
        'wishlist': products_in_wishlist,
    }
    return render(request, 'products/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    request.user.favorite.add(product)
    messages.success(request, 'Product added to wishlist!')
    return redirect(reverse('product_detail', args=[product.id]))


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.user.favorite.filter(id=product_id).exists():
        request.user.favorite.remove(product)
        messages.success(request, 'Product removed from wishlist!')
    return redirect(reverse('product_detail', args=[product.id]))
