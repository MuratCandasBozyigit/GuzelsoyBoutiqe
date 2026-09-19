from django.conf import settings
from .models import Category, Cart


def get_or_create_cart(request):
    """
    Utility to get or create the shopping cart for either authenticated users or guest session shoppers.
    """
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
    return cart


def store_context(request):
    """
    Context processor making store navigation, boutique info and cart stats globally accessible in all templates.
    """
    # Categories for navigation and mega menu
    root_categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children', 'products')
    
    # Active Cart
    cart = None
    try:
        cart = get_or_create_cart(request)
    except Exception:
        pass

    return {
        'nav_categories': root_categories,
        'cart': cart,
        'cart_items_count': cart.total_items if cart else 0,
        'cart_subtotal': cart.subtotal if cart else 0,
        'boutique': {
            'name': getattr(settings, 'BOUTIQUE_NAME', 'Gala Butik'),
            'slogan': getattr(settings, 'BOUTIQUE_SLOGAN', 'Zarafet ve Konforun Büyük Beden Buluşması'),
            'phone': getattr(settings, 'BOUTIQUE_PHONE', '+90 (850) 305 42 52'),
            'whatsapp': getattr(settings, 'BOUTIQUE_WHATSAPP', '+90 (532) 000 00 00'),
            'email': getattr(settings, 'BOUTIQUE_EMAIL', 'destek@galabutik.com'),
            'address': getattr(settings, 'BOUTIQUE_ADDRESS', 'Nişantaşı, Teşvikiye Cad. No:42 Şişli / İstanbul'),
            'free_shipping_threshold': getattr(settings, 'FREE_SHIPPING_THRESHOLD', 750.00),
            'default_shipping_fee': getattr(settings, 'DEFAULT_SHIPPING_FEE', 69.90),
            'max_installments': getattr(settings, 'MAX_INSTALLMENTS_ALLOWED', 3),
        }
    }
