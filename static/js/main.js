/**
 * Gala Butik - Main Interactive JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
    initCartDrawer();
    initAddToCartForms();
    initProductGallery();
    initSizeSelectors();
    initQuantitySteppers();
    initCheckoutTabs();
    initSearchModal();
    initMobileNav();
});

// Toast notification helper
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    const bgClass = type === 'success' ? 'bg-[#2B2623] text-white border-l-4 border-[#B85032]' : 'bg-[#dc2626] text-white';
    
    toast.className = `flex items-center gap-3 p-4 rounded shadow-lg text-sm transition-all duration-300 transform translate-y-2 opacity-0 ${bgClass}`;
    toast.innerHTML = `
        <svg class="w-5 h-5 flex-shrink-0 text-[#D48B6F]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <span class="flex-1">${message}</span>
        <button class="text-gray-400 hover:text-white" onclick="this.parentElement.remove()">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
        </button>
    `;

    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Update Cart Badge & Progress
function updateCartUI(data) {
    // Update badge count
    const badges = document.querySelectorAll('.cart-badge-count');
    badges.forEach(b => {
        b.textContent = data.cart_items_count;
        b.style.display = data.cart_items_count > 0 ? 'inline-flex' : 'none';
    });

    // Update subtotals
    const subtotalEls = document.querySelectorAll('.cart-subtotal-val');
    subtotalEls.forEach(el => {
        el.textContent = (data.cart_subtotal || 0).toLocaleString('tr-TR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' ₺';
    });

    // Update free shipping bar
    const progressBars = document.querySelectorAll('.shipping-progress-bar');
    const remainingLabels = document.querySelectorAll('.free-shipping-msg');

    progressBars.forEach(p => {
        p.style.width = (data.free_shipping_progress || 0) + '%';
    });

    remainingLabels.forEach(lbl => {
        if (data.free_shipping_remaining && data.free_shipping_remaining > 0) {
            lbl.innerHTML = `Kargonun <strong>ÜCRETSİZ</strong> olması için <span class="text-[#B85032] font-bold">${data.free_shipping_remaining.toLocaleString('tr-TR', { minimumFractionDigits: 2 })} ₺</span> daha ürün ekleyin!`;
        } else {
            lbl.innerHTML = `<span class="text-[#16a34a] font-bold">🎉 Tebrikler! Ücretsiz Kargo Kazandınız!</span>`;
        }
    });
}

// Cart Drawer
function initCartDrawer() {
    const drawer = document.getElementById('cart-drawer');
    const backdrop = document.getElementById('cart-backdrop');
    const openBtns = document.querySelectorAll('.cart-drawer-trigger');
    const closeBtns = document.querySelectorAll('.cart-drawer-close');

    if (!drawer) return;

    function openDrawer() {
        drawer.classList.remove('translate-x-full');
        backdrop.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }

    function closeDrawer() {
        drawer.classList.add('translate-x-full');
        backdrop.classList.add('hidden');
        document.body.style.overflow = '';
    }

    openBtns.forEach(btn => btn.addEventListener('click', (e) => {
        e.preventDefault();
        openDrawer();
    }));

    closeBtns.forEach(btn => btn.addEventListener('click', closeDrawer));
    if (backdrop) backdrop.addEventListener('click', closeDrawer);
}

// Add to Cart Forms (AJAX)
function initAddToCartForms() {
    const forms = document.querySelectorAll('.ajax-add-to-cart');
    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('button[type="submit"]');
            const originalBtnText = btn ? btn.innerHTML : '';
            
            // Validate size selection if sizes exist
            const sizeInput = form.querySelector('input[name="size_variant_id"]');
            const hasSizes = form.querySelector('.size-options-container');
            if (hasSizes && (!sizeInput || !sizeInput.value)) {
                showToast('Lütfen bir beden seçiniz.', 'error');
                return;
            }

            if (btn) {
                btn.disabled = true;
                btn.innerHTML = `
                    <svg class="animate-spin h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg> Ekleniyor...`;
            }

            try {
                const formData = new FormData(form);
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                const data = await response.json();
                if (data.success) {
                    showToast(data.message, 'success');
                    updateCartUI(data);
                    
                    // Optionally open drawer
                    const drawer = document.getElementById('cart-drawer');
                    if (drawer) {
                        const openDrawerBtn = document.querySelector('.cart-drawer-trigger');
                        if (openDrawerBtn) openDrawerBtn.click();
                    }
                } else {
                    showToast(data.message || 'Ürün eklenirken hata oluştu.', 'error');
                }
            } catch (err) {
                console.error(err);
                form.submit(); // fallback to standard submit
            } finally {
                if (btn) {
                    btn.disabled = false;
                    btn.innerHTML = originalBtnText;
                }
            }
        });
    });
}

// Product Detail Image Gallery
function initProductGallery() {
    const mainImg = document.getElementById('main-product-image');
    const thumbnails = document.querySelectorAll('.gallery-thumb');

    if (!mainImg || !thumbnails.length) return;

    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', () => {
            thumbnails.forEach(t => t.classList.remove('border-[#B85032]', 'opacity-100'));
            thumbnails.forEach(t => t.classList.add('border-transparent', 'opacity-60'));
            
            thumb.classList.remove('border-transparent', 'opacity-60');
            thumb.classList.add('border-[#B85032]', 'opacity-100');
            
            const newSrc = thumb.getAttribute('data-full-src');
            if (newSrc) {
                mainImg.src = newSrc;
            }
        });
    });
}

// Size Variant Selection Pills
function initSizeSelectors() {
    const sizePills = document.querySelectorAll('.size-select-pill');
    const hiddenInput = document.getElementById('selected-size-variant-id');
    const stockDisplay = document.getElementById('size-stock-feedback');

    if (!sizePills.length || !hiddenInput) return;

    sizePills.forEach(pill => {
        pill.addEventListener('click', () => {
            if (pill.classList.contains('disabled')) return;

            sizePills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');

            const variantId = pill.getAttribute('data-variant-id');
            const stock = parseInt(pill.getAttribute('data-stock') || '0', 10);
            
            hiddenInput.value = variantId;

            if (stockDisplay) {
                if (stock <= 3 && stock > 0) {
                    stockDisplay.innerHTML = `<span class="text-[#dc2626] font-semibold">⚠️ Acele edin! Son ${stock} adet kaldı!</span>`;
                } else if (stock > 3) {
                    stockDisplay.innerHTML = `<span class="text-[#16a34a] font-semibold">✓ Stokta var (${stock} adet)</span>`;
                } else {
                    stockDisplay.innerHTML = `<span class="text-[#786C63]">Tükendi</span>`;
                }
            }
        });
    });
}

// Quantity Steppers
function initQuantitySteppers() {
    const steppers = document.querySelectorAll('.quantity-stepper');
    steppers.forEach(stepper => {
        const input = stepper.querySelector('input[name="quantity"]');
        const minusBtn = stepper.querySelector('.btn-qty-minus');
        const plusBtn = stepper.querySelector('.btn-qty-plus');

        if (!input) return;

        if (minusBtn) {
            minusBtn.addEventListener('click', () => {
                let val = parseInt(input.value, 10) || 1;
                if (val > 1) {
                    input.value = val - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }

        if (plusBtn) {
            plusBtn.addEventListener('click', () => {
                let val = parseInt(input.value, 10) || 1;
                input.value = val + 1;
                input.dispatchEvent(new Event('change'));
            });
        }
    });
}

// Checkout Payment Tabs
function initCheckoutTabs() {
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    const paymentSections = {
        'credit_card': document.getElementById('payment-section-card'),
        'bank_transfer': document.getElementById('payment-section-bank'),
        'cash_on_delivery': document.getElementById('payment-section-cod')
    };

    if (!paymentRadios.length) return;

    paymentRadios.forEach(radio => {
        radio.addEventListener('change', () => {
            Object.keys(paymentSections).forEach(key => {
                const section = paymentSections[key];
                if (section) {
                    if (key === radio.value) {
                        section.classList.remove('hidden');
                    } else {
                        section.classList.add('hidden');
                    }
                }
            });
        });
    });
}

// Search Modal
function initSearchModal() {
    const modal = document.getElementById('search-modal');
    const openBtns = document.querySelectorAll('.search-modal-trigger');
    const closeBtns = document.querySelectorAll('.search-modal-close');
    const searchInput = document.getElementById('search-modal-input');

    if (!modal) return;

    openBtns.forEach(btn => btn.addEventListener('click', (e) => {
        e.preventDefault();
        modal.classList.remove('hidden');
        if (searchInput) searchInput.focus();
    }));

    closeBtns.forEach(btn => btn.addEventListener('click', () => {
        modal.classList.add('hidden');
    }));
}

// Mobile Nav
function initMobileNav() {
    const navDrawer = document.getElementById('mobile-nav-drawer');
    const openBtn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('mobile-menu-close');
    const backdrop = document.getElementById('mobile-nav-backdrop');

    if (!navDrawer || !openBtn) return;

    openBtn.addEventListener('click', () => {
        navDrawer.classList.remove('-translate-x-full');
        if (backdrop) backdrop.classList.remove('hidden');
    });

    const closeNav = () => {
        navDrawer.classList.add('-translate-x-full');
        if (backdrop) backdrop.classList.add('hidden');
    };

    if (closeBtn) closeBtn.addEventListener('click', closeNav);
    if (backdrop) backdrop.addEventListener('click', closeNav);
}
