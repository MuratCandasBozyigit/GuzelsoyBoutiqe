from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Home
    path('', views.home_view, name='home'),
    
    # Products & Catalog
    path('urunler/', views.product_list_view, name='product_list'),
    path('kategori/<slug:category_slug>/', views.product_list_view, name='product_list_by_category'),
    path('urun/<slug:slug>/', views.product_detail_view, name='product_detail'),
    
    # Cart Operations
    path('sepet/', views.cart_detail_view, name='cart_detail'),
    path('sepet/ekle/', views.add_to_cart_view, name='add_to_cart'),
    path('sepet/guncelle/', views.update_cart_view, name='update_cart'),
    path('sepet/sil/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    
    # Checkout & Orders
    path('odeme/', views.checkout_view, name='checkout'),
    path('siparis-onay/<str:order_number>/', views.order_confirmation_view, name='order_confirmation'),
    
    # Info & Customer Service Pages
    path('hakkimizda/', views.about_view, name='about'),
    path('iletisim/', views.contact_view, name='contact'),
    path('beden-tablosu/', views.size_guide_view, name='size_guide'),
    path('kargo-ve-iade/', views.shipping_returns_view, name='shipping_returns'),
]
