import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Category, Product, ProductImage, SizeVariant, Order, OrderItem, PaymentLog

User = get_user_model()

class Command(BaseCommand):
    help = "Populate Gala Butik store with rich initial categories, plus-size products, variants and mock data."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating Gala Butik initial data..."))

        # 1. Create Superuser if not exists
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@galabutik.com", "admin123")
            self.stdout.write(self.style.SUCCESS("[OK] Admin superuser created: admin / admin123"))

        # 2. Categories
        categories_data = [
            {
                "name": "Büyük Beden Elbise",
                "slug": "buyuk-beden-elbise",
                "description": "42'den 58 bedene kadar dökümlü, rahat kalıp ve şık büyük beden elbise modelleri.",
                "is_featured_home": True,
                "display_order": 1,
                "children": ["Dökümlü Viskon Elbise", "Abiye & Davet Elbisesi", "Günlük Desenli Elbise"]
            },
            {
                "name": "Tunik & Gömlek",
                "slug": "tunik-ve-gomlek",
                "description": "Rahat kesim, baseni örten şık tunikler ve pamuklu büyük beden gömlekler.",
                "is_featured_home": True,
                "display_order": 2,
                "children": ["Keten & Viskon Tunik", "Şifon Detaylı Tunik", "Oversize Gömlek"]
            },
            {
                "name": "İkili Takım",
                "slug": "ikili-takim",
                "description": "Kombin derdine son veren, dökümlü pantolonlu ve etekli büyük beden ikili takımlar.",
                "is_featured_home": True,
                "display_order": 3,
                "children": ["Pantolonlu Triko Takım", "Dökümlü Viskon Takım"]
            },
            {
                "name": "Triko & Hırka",
                "slug": "triko-ve-hirka",
                "description": "Yumuşak dokulu, nefes alan triko kazaklar, hırkalar ve mevsimlik yelekler.",
                "is_featured_home": True,
                "display_order": 4,
                "children": ["Uzun Triko Hırka", "Dökümlü Triko Kazak"]
            },
            {
                "name": "Dış Giyim & Trençkot",
                "slug": "dis-giyim-ve-trenckot",
                "description": "Büyük beden kadınlar için özel dikim trençkot, kapitone ceket ve pardösüler.",
                "is_featured_home": True,
                "display_order": 5,
                "children": ["Mevsimlik Trençkot", "Rahat Kesim Ceket"]
            },
            {
                "name": "Pantolon & Etek",
                "slug": "pantolon-ve-etek",
                "description": "Yüksek bel, beli lastikli esnek kumaş pantolonlar ve piliseli etekler.",
                "is_featured_home": True,
                "display_order": 6,
                "children": ["Beli Lastikli Havuç Pantolon", "Piliseli Dökümlü Etek"]
            }
        ]

        cat_instances = {}
        for cat_info in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cat_info["slug"],
                defaults={
                    "name": cat_info["name"],
                    "description": cat_info["description"],
                    "is_featured_home": cat_info["is_featured_home"],
                    "display_order": cat_info["display_order"]
                }
            )
            cat_instances[cat_info["name"]] = cat

            for child_name in cat_info.get("children", []):
                child_slug = f"{cat.slug}-{child_name.lower().replace(' ', '-').replace('&', 've').replace('ü', 'u').replace('ö', 'o').replace('ı', 'i').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')}"
                child_cat, _ = Category.objects.get_or_create(
                    slug=child_slug,
                    defaults={
                        "name": child_name,
                        "parent": cat,
                        "description": f"{cat.name} kategorisinde {child_name} seçenekleri.",
                        "is_active": True
                    }
                )
                cat_instances[child_name] = child_cat

        self.stdout.write(self.style.SUCCESS(f"[OK] Categories created: {len(cat_instances)} categories"))

        # 3. Products Data
        products_data = [
            {
                "category": cat_instances.get("Dökümlü Viskon Elbise", cat_instances["Büyük Beden Elbise"]),
                "name": "Yaprak Desenli Dökümlü Viskon Büyük Beden Elbise",
                "sku": "GLA-ELB-101",
                "price": Decimal("1299.90"),
                "discount_price": Decimal("999.90"),
                "short_description": "Nefes alan %100 viskon kumaş, beli büzgülü dökümlü kesim.",
                "description": "Gala Butik özel koleksiyonundan dökümlü yaprak desenli viskon elbise. Vücudu sarmayan rahat kalıbı ve terletmeyen kumaşıyla özel günlerinizde ve günlük hayatınızda konforlu şıklık sunar. Kol uçları lastikli ve manşetlidir.",
                "fabric_info": "%95 Viskon, %5 Likra. Terletmeyen dökümlü kumaş.",
                "model_measurements": "Manken Ölçüleri: Boy: 1.76m, Göğüs: 106cm, Bel: 88cm, Basen: 114cm. Manken üzerindeki beden: 44 (XL).",
                "is_bestseller": True,
                "is_featured": True,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?q=80&w=800&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1496747611176-843222e1e57c?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 15),
                    ("2XL (46-48)", 20),
                    ("3XL (50-52)", 12),
                    ("4XL (54-56)", 8),
                ]
            },
            {
                "category": cat_instances.get("Pantolonlu Triko Takım", cat_instances["İkili Takım"]),
                "name": "Düğme Detaylı Triko Büyük Beden İkili Takım - Kiremit",
                "sku": "GLA-TKM-202",
                "price": Decimal("1599.00"),
                "discount_price": Decimal("1249.90"),
                "short_description": "Yumuşak dokulu triko tunik ve beli lastikli triko pantolon ikili takım.",
                "description": "Zarafeti ve konforu bir arada sunan triko ikili takım. Terracotta (Kiremit) tonlarıyla sonbahar ve ilkbahar aylarının vazgeçilmezi. Tunik boyu baseni kapatır, pantolon beli tam esnek lastiklidir.",
                "fabric_info": "%80 Akrilik Triko, %20 Pamuk Viskon. Çekme ve tüylenme yapmaz.",
                "model_measurements": "Manken Ölçüleri: Boy: 1.74m, Göğüs: 104cm, Bel: 86cm, Basen: 112cm. Giydiği Beden: 2XL (46-48).",
                "is_bestseller": True,
                "is_featured": True,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=800&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 10),
                    ("2XL (46-48)", 18),
                    ("3XL (50-52)", 15),
                    ("4XL (54-56)", 5),
                    ("5XL (58-60)", 4),
                ]
            },
            {
                "category": cat_instances.get("Keten & Viskon Tunik", cat_instances["Tunik & Gömlek"]),
                "name": "Asimetrik Kesim Doğal Keten Büyük Beden Tunik - Bej",
                "sku": "GLA-TNK-303",
                "price": Decimal("899.90"),
                "discount_price": Decimal("699.90"),
                "short_description": "Hafif ve terletmeyen keten kumaş, modern asimetrik etek ucu.",
                "description": "Yaz ve bahar aylarında serin tutan doğal keten karışımlı tunik. Boydan sedef düğmeli, katlanabilir kollu ve yanlardan yırtmaçlı tasarımıyla ferah bir kullanım sağlar.",
                "fabric_info": "%70 Keten, %30 Viskon pamuk.",
                "model_measurements": "Manken Boy: 1.75m, Göğüs: 102cm, Giydiği Beden: 44.",
                "is_bestseller": False,
                "is_featured": True,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 25),
                    ("2XL (46-48)", 20),
                    ("3XL (50-52)", 15),
                    ("4XL (54-56)", 10),
                ]
            },
            {
                "category": cat_instances.get("Mevsimlik Trençkot", cat_instances["Dış Giyim & Trençkot"]),
                "name": "Kuşaklı Astarlı Klasik Büyük Beden Trençkot - Haki / Bej",
                "sku": "GLA-TRN-404",
                "price": Decimal("2199.00"),
                "discount_price": Decimal("1799.00"),
                "short_description": "Su itici gabardin kumaş, tam astarlı ve belden kuşaklı lüks trençkot.",
                "description": "Zarif dikiş detayları, geniş cepleri ve dökümlü yakasıyla hem klasik hem spor kombinlerin tamamlayıcısı. İç kısmı saten astarlıdır.",
                "fabric_info": "%65 Pamuk, %35 Polyester Bondit Gabardin (Su itici).",
                "model_measurements": "Manken Boy: 1.76m, Göğüs: 108cm, Giydiği Beden: 2XL (46-48).",
                "is_bestseller": True,
                "is_featured": True,
                "is_new": False,
                "images": [
                    "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 8),
                    ("2XL (46-48)", 12),
                    ("3XL (50-52)", 10),
                    ("4XL (54-56)", 6),
                ]
            },
            {
                "category": cat_instances.get("Beli Lastikli Havuç Pantolon", cat_instances["Pantolon & Etek"]),
                "name": "Likralı Duble Paça Büyük Beden Havuç Pantolon - Siyah",
                "sku": "GLA-PNT-505",
                "price": Decimal("649.90"),
                "discount_price": Decimal("499.90"),
                "short_description": "Yüksek bel, arkası lastikli ve toparlayıcı kumaş.",
                "description": "Günlük kullanımda maksimum esneklik sunan toparlayıcı kumaşlı havuç pantolon. Yüksek beli sayesinde karın bölgesini sarar ve konforlu hissettirir.",
                "fabric_info": "%90 Poliviskon, %10 Elastan.",
                "model_measurements": "Manken Boy: 1.74m, Basen: 115cm, Giydiği Beden: 46.",
                "is_bestseller": True,
                "is_featured": False,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("44", 20),
                    ("46", 25),
                    ("48", 22),
                    ("50", 18),
                    ("52", 14),
                    ("54", 10),
                ]
            },
            {
                "category": cat_instances.get("Abiye & Davet Elbisesi", cat_instances["Büyük Beden Elbise"]),
                "name": "Şifon Pelerinli Kruvaze Büyük Beden Davet Elbisesi - Bordo",
                "sku": "GLA-ABY-606",
                "price": Decimal("2499.00"),
                "discount_price": Decimal("1999.00"),
                "short_description": "Şifon pelerin omuz detayı, esnek astarlı zarafet abiyesi.",
                "description": "Düğün, nişan ve özel davetleriniz için tasarlanmış şifon pelerinli abiye elbise. Kol ve omuz kusurlarını zarifçe kapatan dökümlü pelerin tülüyle göz kamaştırır.",
                "fabric_info": "%100 İpek Şifon ve Esnek Likralı Likra Astar.",
                "model_measurements": "Manken Boy: 1.77m, Göğüs: 110cm, Giydiği Beden: 3XL (50-52).",
                "is_bestseller": False,
                "is_featured": True,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1566174053879-31528523f8ae?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 6),
                    ("2XL (46-48)", 10),
                    ("3XL (50-52)", 12),
                    ("4XL (54-56)", 8),
                    ("5XL (58-60)", 4),
                ]
            },
            {
                "category": cat_instances.get("Uzun Triko Hırka", cat_instances["Triko & Hırka"]),
                "name": "Cepli Dökümlü Selanik Örgü Büyük Beden Hırka - Vizon",
                "sku": "GLA-HRK-707",
                "price": Decimal("1149.00"),
                "discount_price": Decimal("899.90"),
                "short_description": "Selanik örgü dokulu, salaş ve dökümlü uzun hırka.",
                "description": "Geniş cepli, yumuşacık yün tuşeli vizon renk triko hırka. Her kombinin üstüne rahatlıkla atabileceğiniz zamansız parça.",
                "fabric_info": "%100 Soft Akrilik Triko.",
                "model_measurements": "Manken Boy: 1.75m, Giydiği Beden: Standart (38-48 Uyumlu).",
                "is_bestseller": True,
                "is_featured": True,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("Standart", 30),
                    ("XL (42-44)", 15),
                    ("2XL (46-48)", 20),
                    ("3XL (50-52)", 15),
                ]
            },
            {
                "category": cat_instances.get("Piliseli Dökümlü Etek", cat_instances["Pantolon & Etek"]),
                "name": "Beli Lastikli Piliseli Şifon Büyük Beden Etek - Terracotta",
                "sku": "GLA-ETK-808",
                "price": Decimal("799.00"),
                "discount_price": Decimal("599.90"),
                "short_description": "Kalıcı pilise teknolojisi, iç göstermeyen tam astarlı.",
                "description": "Dökümlü salınımı ve terracotta rengiyle zarif bir siluet sunan piliseli etek. Beli simli esnek lastiklidir.",
                "fabric_info": "%100 Şifon Viskon, %100 Pamuk Astar.",
                "model_measurements": "Manken Boy: 1.74m, Giydiği Beden: XL.",
                "is_bestseller": False,
                "is_featured": False,
                "is_new": True,
                "images": [
                    "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?q=80&w=800&auto=format&fit=crop",
                ],
                "sizes": [
                    ("XL (42-44)", 14),
                    ("2XL (46-48)", 18),
                    ("3XL (50-52)", 12),
                    ("4XL (54-56)", 8),
                ]
            }
        ]

        for p_data in products_data:
            prod, created = Product.objects.get_or_create(
                sku=p_data["sku"],
                defaults={
                    "category": p_data["category"],
                    "name": p_data["name"],
                    "price": p_data["price"],
                    "discount_price": p_data["discount_price"],
                    "short_description": p_data["short_description"],
                    "description": p_data["description"],
                    "fabric_info": p_data["fabric_info"],
                    "model_measurements": p_data["model_measurements"],
                    "is_bestseller": p_data["is_bestseller"],
                    "is_featured": p_data["is_featured"],
                    "is_new": p_data["is_new"],
                    "is_active": True,
                }
            )

            # Images
            for i, img_url in enumerate(p_data["images"]):
                ProductImage.objects.get_or_create(
                    product=prod,
                    image_url_fallback=img_url,
                    defaults={
                        "is_feature": (i == 0),
                        "display_order": i,
                        "alt_text": prod.name
                    }
                )

            # Size Variants
            for size_code, stock_qty in p_data["sizes"]:
                SizeVariant.objects.get_or_create(
                    product=prod,
                    size=size_code,
                    defaults={
                        "stock": stock_qty,
                        "sku": f"{prod.sku}-{size_code.split()[0]}",
                        "is_active": True
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"[OK] Products created: {len(products_data)} boutique products with size variants"))

        # 4. Sample Completed Order with Payment Log (3 Installments max rule verified)
        if not Order.objects.exists():
            sample_product = Product.objects.first()
            sample_variant = sample_product.size_variants.first()
            
            order = Order.objects.create(
                first_name="Ayşe",
                last_name="Demir",
                email="ayse.demir@example.com",
                phone="0532 111 22 33",
                address_title="Ev",
                address_line1="Bağdat Cad. No:142 Daire:8",
                district="Kadıköy",
                city="İstanbul",
                postal_code="34728",
                order_notes="Lütfen kapıyı çalmadan önce telefon ediniz.",
                subtotal=sample_product.current_price,
                shipping_fee=Decimal("0.00"),
                total_amount=sample_product.current_price,
                status="shipped",
                payment_method="credit_card",
                payment_status="paid",
                installments=3,  # Max 3 Installments rule
                cargo_company="Yurtiçi Kargo",
                tracking_number="YK-9842105471"
            )

            OrderItem.objects.create(
                order=order,
                product=sample_product,
                product_name=sample_product.name,
                size_title=sample_variant.get_size_display() if sample_variant else "Standart",
                sku=sample_product.sku,
                price=sample_product.current_price,
                quantity=1,
                total_price=sample_product.current_price,
                product_image_url=sample_product.primary_image.url if sample_product.primary_image else ""
            )

            PaymentLog.objects.create(
                order=order,
                provider="paytr",
                transaction_id="TXN-PAYTR-849201",
                status="success",
                installment_count=3,  # Max 3 Installment rule
                amount=order.total_amount,
                card_family="Bonus",
                card_last_four="4242",
                raw_response='{"status": "success", "installment": 3, "max_installment_checked": true, "code": "OK"}'
            )

            self.stdout.write(self.style.SUCCESS(f"[OK] Sample mock order created: #{order.order_number}"))

        self.stdout.write(self.style.SUCCESS("\n[SUCCESS] Gala Butik project data seeded successfully!"))
