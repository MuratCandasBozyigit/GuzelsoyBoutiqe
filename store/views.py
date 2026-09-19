import json
import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max
from django.views.decorators.http import require_POST, require_http_methods
from django.conf import settings

from .models import (
    Category,
    Product,
    ProductImage,
    SizeVariant,
    Cart,
    CartItem,
    Order,
    OrderItem,
    PaymentLog,
)
from .context_processors import get_or_create_cart


def home_view(request):
    """
    Main landing page showcasing Deniz Butik style warm boutique aesthetics:
    Hero banners, featured categories, bestsellers, new arrivals and value props.
    """
    featured_categories = Category.objects.filter(is_active=True, is_featured_home=True)[:6]
    if not featured_categories.exists():
        featured_categories = Category.objects.filter(is_active=True, parent__isnull=True)[:6]

    new_arrivals = Product.objects.filter(is_active=True, is_new=True).select_related('category').prefetch_related('images', 'size_variants')[:8]
    if not new_arrivals.exists():
        new_arrivals = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'size_variants')[:8]

    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True).select_related('category').prefetch_related('images', 'size_variants')[:8]
    if not bestsellers.exists():
        bestsellers = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    # Special curated section for Plus Size (Büyük Beden)
    plus_size_products = Product.objects.filter(
        is_active=True,
        category__name__icontains="Büyük Beden"
    ).select_related('category').prefetch_related('images', 'size_variants')[:8]
    if not plus_size_products.exists():
        plus_size_products = Product.objects.filter(is_active=True)[:8]

    context = {
        'featured_categories': featured_categories,
        'new_arrivals': new_arrivals,
        'bestsellers': bestsellers,
        'plus_size_products': plus_size_products,
    }
    return render(request, 'store/home.html', context)


def product_list_view(request, category_slug=None):
    """
    Catalog view with rich filtering:
    - Hierarchy category filter
    - Plus-size / Standard size filter
    - Price range
    - Sorting (Newest, Price Asc/Desc, Bestseller)
    - Full-text search
    """
    current_category = None
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'size_variants')
    
    # 1. Category Filtering
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        # Include products in this category and all its children
        category_ids = [current_category.id] + list(current_category.children.values_list('id', flat=True))
        products = products.filter(category_id__in=category_ids)
    
    # 2. Search Query
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(fabric_info__icontains=query) |
            Q(category__name__icontains=query)
        )

    # 3. Size Filter
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(size_variants__size__in=selected_sizes, size_variants__stock__gt=0).distinct()

    # 4. Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            products = products.filter(price__gte=Decimal(min_price))
        except Exception:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=Decimal(max_price))
        except Exception:
            pass

    # 5. Stock & Discount Filters
    in_stock_only = request.GET.get('in_stock')
    if in_stock_only == '1':
        products = products.filter(size_variants__stock__gt=0).distinct()
        
    on_sale_only = request.GET.get('on_sale')
    if on_sale_only == '1':
        products = products.filter(discount_price__isnull=False)

    # 6. Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'bestseller':
        products = products.order_by('-is_bestseller', '-created_at')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    else:  # newest
        products = products.order_by('-created_at')

    # Pagination (12 items per page)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Available sizes for filter sidebar
    all_sizes = [
        ('Standart', 'Standart'),
        ('M (38-40)', 'M (38-40)'),
        ('L (40-42)', 'L (40-42)'),
        ('XL (42-44)', 'XL (42-44)'),
        ('2XL (46-48)', '2XL (46-48)'),
        ('3XL (50-52)', '3XL (50-52)'),
        ('4XL (54-56)', '4XL (54-56)'),
        ('5XL (58-60)', '5XL (58-60)'),
        ('42', '42'),
        ('44', '44'),
        ('46', '46'),
        ('48', '48'),
        ('50', '50'),
        ('52', '52'),
        ('54', '54'),
    ]

    all_categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')

    context = {
        'current_category': current_category,
        'page_obj': page_obj,
        'total_products': paginator.count,
        'all_categories': all_categories,
        'all_sizes': all_sizes,
        'selected_sizes': selected_sizes,
        'query': query,
        'sort_by': sort_by,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock_only': in_stock_only == '1',
        'on_sale_only': on_sale_only == '1',
    }
    return render(request, 'store/product_list.html', context)


def product_detail_view(request, slug):
    """
    Product detail page:
    - High resolution image gallery with zoom/thumbnails
    - Size variant selector with live stock checks
    - Installment Matrix calculator (Strictly adhering to max 3 installments rule)
    - Detailed fabric & model sizing breakdown
    - Related products recommendation
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'size_variants'),
        slug=slug,
        is_active=True
    )
    
    # Increment view count
    Product.objects.filter(id=product.id).update(view_count=product.view_count + 1)

    # Active size variants
    variants = product.size_variants.filter(is_active=True)

    # Calculate installments (Max 3 Installments Rule for Textile/Garments)
    current_price = product.current_price
    installments_data = [
        {
            'count': 1,
            'title': 'Tek Çekim (Peşin)',
            'monthly': current_price,
            'total': current_price,
            'badge': 'Komisyonsuz'
        },
        {
            'count': 2,
            'title': '2 Taksit',
            'monthly': round(current_price / Decimal('2.00'), 2),
            'total': current_price,
            'badge': 'Vade Farksız'
        },
        {
            'count': 3,
            'title': '3 Taksit (Maksimum)',
            'monthly': round(current_price / Decimal('3.00'), 2),
            'total': current_price,
            'badge': 'Vade Farksız'
        }
    ]

    bank_cards = ['Bonus', 'Maximum', 'World', 'Axess', 'Paraf', 'CardFinans', 'Sağlam Kart']

    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]

    if not related_products.exists():
        related_products = Product.objects.filter(is_active=True).exclude(id=product.id)[:4]

    context = {
        'product': product,
        'variants': variants,
        'installments_data': installments_data,
        'bank_cards': bank_cards,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)


@require_POST
def add_to_cart_view(request):
    """
    Add product with selected size to shopping cart.
    Accepts both AJAX JSON and standard form POST.
    """
    cart = get_or_create_cart(request)
    product_id = request.POST.get('product_id')
    size_variant_id = request.POST.get('size_variant_id')
    quantity = int(request.POST.get('quantity', 1))

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'

    if not product_id:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Ürün bulunamadı.'}, status=400)
        messages.error(request, 'Ürün bulunamadı.')
        return redirect('store:home')

    product = get_object_or_404(Product, id=product_id, is_active=True)
    size_variant = None
    if size_variant_id:
        size_variant = get_object_or_404(SizeVariant, id=size_variant_id, product=product, is_active=True)
        if size_variant.stock < quantity:
            msg = f"Seçilen bedende yeterli stok bulunmamaktadır (Mevcut: {size_variant.stock})."
            if is_ajax:
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.warning(request, msg)
            return redirect(product.get_absolute_url())

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size_variant=size_variant,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    success_msg = f"{product.name} ({size_variant.get_size_display() if size_variant else 'Standart'}) sepete eklendi."

    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': success_msg,
            'cart_items_count': cart.total_items,
            'cart_subtotal': float(cart.subtotal),
            'free_shipping_remaining': float(cart.remaining_for_free_shipping),
            'free_shipping_progress': cart.free_shipping_progress,
        })

    messages.success(request, success_msg)
    return redirect('store:cart_detail')


@require_POST
def update_cart_view(request):
    """
    Update item quantity in cart.
    """
    cart = get_or_create_cart(request)
    item_id = request.POST.get('item_id')
    quantity = int(request.POST.get('quantity', 1))

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        if quantity > 0:
            # Stock check
            if cart_item.size_variant and cart_item.size_variant.stock < quantity:
                if is_ajax:
                    return JsonResponse({'success': False, 'message': f'Maksimum stok: {cart_item.size_variant.stock}'}, status=400)
                messages.warning(request, f'Maksimum stok: {cart_item.size_variant.stock}')
            else:
                cart_item.quantity = quantity
                cart_item.save()
        else:
            cart_item.delete()

        if is_ajax:
            return JsonResponse({
                'success': True,
                'cart_items_count': cart.total_items,
                'cart_subtotal': float(cart.subtotal),
                'shipping_fee': float(cart.shipping_fee),
                'total_amount': float(cart.total_amount),
                'item_total': float(cart_item.total_price) if quantity > 0 else 0,
                'free_shipping_remaining': float(cart.remaining_for_free_shipping),
                'free_shipping_progress': cart.free_shipping_progress,
            })
    except CartItem.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Öğe bulunamadı.'}, status=404)

    return redirect('store:cart_detail')


@require_POST
def remove_from_cart_view(request, item_id):
    """
    Remove item completely from cart.
    """
    cart = get_or_create_cart(request)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    try:
        cart_item = CartItem.objects.get(id=item_id, cart=cart)
        product_name = cart_item.product.name
        cart_item.delete()
        
        if is_ajax:
            return JsonResponse({
                'success': True,
                'message': f"{product_name} sepetten çıkarıldı.",
                'cart_items_count': cart.total_items,
                'cart_subtotal': float(cart.subtotal),
                'shipping_fee': float(cart.shipping_fee),
                'total_amount': float(cart.total_amount),
                'free_shipping_remaining': float(cart.remaining_for_free_shipping),
                'free_shipping_progress': cart.free_shipping_progress,
            })
        messages.info(request, f"{product_name} sepetten çıkarıldı.")
    except CartItem.DoesNotExist:
        if is_ajax:
            return JsonResponse({'success': False, 'message': 'Öğe bulunamadı.'}, status=404)

    return redirect('store:cart_detail')


def cart_detail_view(request):
    """
    Full Cart Page.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'size_variant').prefetch_related('product__images')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'store/cart_detail.html', context)


@require_http_methods(["GET", "POST"])
def checkout_view(request):
    """
    Checkout page with delivery address and PayTR/İyzico card simulation.
    Enforces maximum 3 installments rule per Turkish legal requirements.
    """
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product', 'size_variant').prefetch_related('product__images')

    if not cart_items.exists():
        messages.warning(request, "Sepetinizde ürün bulunmamaktadır.")
        return redirect('store:home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_title = request.POST.get('address_title', 'Ev Adresim').strip()
        address_line1 = request.POST.get('address_line1', '').strip()
        address_line2 = request.POST.get('address_line2', '').strip()
        city = request.POST.get('city', '').strip()
        district = request.POST.get('district', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        order_notes = request.POST.get('order_notes', '').strip()
        
        payment_method = request.POST.get('payment_method', 'credit_card')
        installments = int(request.POST.get('installments', 1))

        # ENFORCE RULE: Max 3 Installments
        if installments > 3:
            installments = 3

        if not (first_name and last_name and email and phone and address_line1 and city and district):
            messages.error(request, "Lütfen zorunlu teslimat ve iletişim alanlarını eksiksiz doldurunuz.")
            return redirect('store:checkout')

        # Create Order
        subtotal = cart.subtotal
        shipping_fee = cart.shipping_fee
        total_amount = cart.total_amount

        # Cash on delivery service fee (+19.90 TL)
        if payment_method == 'cash_on_delivery':
            total_amount += Decimal('19.90')

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address_title=address_title,
            address_line1=address_line1,
            address_line2=address_line2,
            district=district,
            city=city,
            postal_code=postal_code,
            order_notes=order_notes,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            status='confirmed' if payment_method in ['credit_card', 'cash_on_delivery'] else 'pending',
            payment_method=payment_method,
            payment_status='paid' if payment_method == 'credit_card' else 'pending',
            installments=installments,
            cargo_company='Yurtiçi Kargo'
        )

        # Snapshot Order Items & reduce stock
        for item in cart_items:
            size_name = item.size_variant.get_size_display() if item.size_variant else "Standart"
            img_url = item.product.primary_image.url if item.product.primary_image else ""
            
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                size_title=size_name,
                sku=item.product.sku,
                price=item.product.current_price,
                quantity=item.quantity,
                total_price=item.total_price,
                product_image_url=img_url
            )

            # Reduce stock
            if item.size_variant and item.size_variant.stock >= item.quantity:
                item.size_variant.stock -= item.quantity
                item.size_variant.save()

        # Payment Log Stub (PayTR / İyzico / Havale)
        card_number = request.POST.get('card_number', '').replace(' ', '')
        last_four = card_number[-4:] if len(card_number) >= 4 else "4242"
        card_family = "Bonus" if card_number.startswith("5") else ("World" if card_number.startswith("4") else "Maximum")

        provider_map = {
            'credit_card': 'paytr',
            'bank_transfer': 'bank_transfer',
            'cash_on_delivery': 'cash_on_delivery'
        }

        PaymentLog.objects.create(
            order=order,
            provider=provider_map.get(payment_method, 'paytr'),
            transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
            status='success' if payment_method == 'credit_card' else 'pending',
            installment_count=installments,
            amount=total_amount,
            card_family=card_family if payment_method == 'credit_card' else '',
            card_last_four=last_four if payment_method == 'credit_card' else '',
            raw_response=json.dumps({
                'status': 'success',
                'order_id': order.order_number,
                'installment': installments,
                'max_installment_checked': True,
                'auth_code': 'OK984210'
            })
        )

        # Clear cart
        cart_items.delete()

        # Store last order number in session for confirmation view
        request.session['last_order_number'] = order.order_number
        messages.success(request, f"Tebrikler! #{order.order_number} numaralı siparişiniz başarıyla oluşturuldu.")
        return redirect('store:order_confirmation', order_number=order.order_number)

    # GET request - Show Checkout Page
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'max_installments': getattr(settings, 'MAX_INSTALLMENTS_ALLOWED', 3),
    }
    return render(request, 'store/checkout.html', context)


def order_confirmation_view(request, order_number):
    """
    Order receipt & thank you page.
    """
    order = get_object_or_404(Order.objects.prefetch_related('items', 'payment_logs'), order_number=order_number)
    
    context = {
        'order': order,
        'payment_log': order.payment_logs.first(),
    }
    return render(request, 'store/order_confirmation.html', context)


# Static Content & Guide Pages
def about_view(request):
    return render(request, 'store/pages/about.html')

def contact_view(request):
    if request.method == 'POST':
        messages.success(request, "Mesajınız bize ulaştı. Müşteri temsilcimiz en kısa sürede size dönüş yapacaktır.")
        return redirect('store:contact')
    return render(request, 'store/pages/contact.html')

def size_guide_view(request):
    return render(request, 'store/pages/size_guide.html')

def shipping_returns_view(request):
    return render(request, 'store/pages/shipping_returns.html')
