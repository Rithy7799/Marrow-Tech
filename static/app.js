const cartKey = 'morrow-cart';
const readCart = () => JSON.parse(localStorage.getItem(cartKey) || '[]');
const writeCart = (cart) => { localStorage.setItem(cartKey, JSON.stringify(cart)); renderCart(); };
const money = (value) => `$${Number(value).toFixed(2)}`;

function renderCart() {
  const cart = readCart();
  const count = cart.reduce((sum, item) => sum + item.quantity, 0);
  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  document.querySelectorAll('[data-cart-count]').forEach((node) => node.textContent = count);
  document.querySelectorAll('[data-cart-total]').forEach((node) => node.textContent = money(total));
  const target = document.querySelector('[data-cart-items]');
  if (!target) return;
  target.innerHTML = cart.length ? cart.map((item) => `<article class="cart-item"><button class="remove-item remove-item-left" data-remove="${item.id}" aria-label="Remove ${item.name}">×</button><div class="cart-item-art" style="background:${item.color}">${item.initials}</div><div class="cart-item-info"><strong>${item.name}</strong><span>${money(item.price)}</span><div class="quantity"><button data-quantity="${item.id}" data-change="-1" aria-label="Decrease quantity">−</button><span>${item.quantity}</span><button data-quantity="${item.id}" data-change="1" aria-label="Increase quantity">+</button></div></div></article>`).join('') : '<div class="empty-cart"><span>◌</span><p>Your bag is waiting for something good.</p></div>';
}

function showToast(message) {
  const toast = document.querySelector('[data-toast]');
  toast.textContent = message; toast.classList.add('is-visible');
  setTimeout(() => toast.classList.remove('is-visible'), 2800);
}
function toggleDrawer(open) {
  const drawer = document.querySelector('[data-cart-drawer]');
  drawer.classList.toggle('is-open', open); drawer.setAttribute('aria-hidden', String(!open));
}

async function openInvoice(orderId) {
  const modal = document.querySelector('[data-invoice-modal]');
  modal.classList.add('is-visible');
  modal.setAttribute('aria-hidden', 'false');
  modal.querySelector('[data-invoice-title]').textContent = `Invoice #${orderId}`;
  modal.querySelector('[data-invoice-items]').replaceChildren();
  modal.querySelector('[data-invoice-status]').textContent = 'Loading invoice...';
  try {
    const response = await fetch(`/api/orders/${encodeURIComponent(orderId)}`);
    const invoice = await response.json();
    if (!response.ok) throw new Error(invoice.error || 'Could not load this invoice.');
    modal.querySelector('[data-invoice-customer]').textContent = invoice.customer_name;
    modal.querySelector('[data-invoice-email]').textContent = invoice.email;
    modal.querySelector('[data-invoice-address]').textContent = invoice.address;
    modal.querySelector('[data-invoice-date]').textContent = `${invoice.created_at.slice(0, 10)} · ${invoice.status}`;
    modal.querySelector('[data-invoice-total]').textContent = money(invoice.total);
    modal.querySelector('[data-invoice-status]').textContent = `Order #${invoice.id}`;
    const items = modal.querySelector('[data-invoice-items]');
    invoice.items.forEach((item) => {
      const row = document.createElement('div');
      row.className = 'invoice-item';
      const description = document.createElement('div');
      const name = document.createElement('strong');
      const details = document.createElement('span');
      const lineTotal = document.createElement('strong');
      name.textContent = item.name;
      details.textContent = `${item.quantity} × ${money(item.price)}`;
      lineTotal.textContent = money(item.quantity * item.price);
      description.append(name, details);
      row.append(description, lineTotal);
      items.append(row);
    });
  } catch (error) {
    modal.querySelector('[data-invoice-status]').textContent = error.message;
  }
  modal.querySelector('[data-invoice-close]').focus();
}

function closeInvoice() {
  const modal = document.querySelector('[data-invoice-modal]');
  modal.classList.remove('is-visible');
  modal.setAttribute('aria-hidden', 'true');
}

const adminTabList = document.querySelector('[data-admin-tabs]');
if (adminTabList) {
  const adminTabs = [...adminTabList.querySelectorAll('[data-admin-tab]')];
  const activateAdminTab = (tab) => {
    adminTabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
    });
    const url = new URL(window.location.href);
    url.searchParams.set('view', tab.id.replace('admin-tab-', ''));
    window.history.replaceState({}, '', url);
  };
  adminTabList.addEventListener('click', (event) => {
    const tab = event.target.closest('[data-admin-tab]');
    if (tab) activateAdminTab(tab);
  });
  adminTabList.addEventListener('keydown', (event) => {
    const currentIndex = adminTabs.indexOf(event.target.closest('[data-admin-tab]'));
    if (currentIndex < 0) return;
    let nextIndex = currentIndex;
    if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % adminTabs.length;
    else if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + adminTabs.length) % adminTabs.length;
    else if (event.key === 'Home') nextIndex = 0;
    else if (event.key === 'End') nextIndex = adminTabs.length - 1;
    else return;
    event.preventDefault();
    adminTabs[nextIndex].focus();
    activateAdminTab(adminTabs[nextIndex]);
  });
}

document.addEventListener('click', (event) => {
  const invoiceTrigger = event.target.closest('[data-invoice-id]');
  if (invoiceTrigger) {
    openInvoice(invoiceTrigger.dataset.invoiceId);
    return;
  }
  if (event.target.closest('[data-invoice-close]') || event.target.matches('[data-invoice-modal]')) {
    closeInvoice();
    return;
  }
  const addButton = event.target.closest('[data-add-to-cart]');
  if (addButton) {
    const product = JSON.parse(addButton.dataset.addToCart);
    const cart = readCart(); const existing = cart.find((item) => item.id === product.id);
    existing ? existing.quantity++ : cart.push({...product, quantity: 1});
    writeCart(cart); showToast(`${product.name} added to your bag`);
  }
  if (event.target.closest('[data-cart-open]')) toggleDrawer(true);
  if (event.target.closest('[data-cart-close]')) toggleDrawer(false);
  const quantityButton = event.target.closest('[data-quantity]');
  if (quantityButton) {
    const cart = readCart(); const item = cart.find((entry) => entry.id === Number(quantityButton.dataset.quantity));
    if (item) item.quantity += Number(quantityButton.dataset.change);
    writeCart(cart.filter((entry) => entry.quantity > 0));
  }
  const removeButton = event.target.closest('[data-remove]');
  if (removeButton) writeCart(readCart().filter((item) => item.id !== Number(removeButton.dataset.remove)));
  if (event.target.closest('[data-checkout-open]')) {
    if (!readCart().length) return showToast('Add something to your bag first');
    document.querySelector('[data-checkout-modal]').classList.add('is-visible'); toggleDrawer(false);
  }
  if (event.target.closest('[data-checkout-close]') || event.target.matches('[data-checkout-modal]')) document.querySelector('[data-checkout-modal]').classList.remove('is-visible');
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && document.querySelector('[data-invoice-modal].is-visible')) closeInvoice();
});

document.addEventListener('submit', async (event) => {
  if (!event.target.matches('[data-checkout-form]')) return;
  event.preventDefault();
  const form = new FormData(event.target); const cart = readCart();
  const response = await fetch('/api/purchases', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ customer: Object.fromEntries(form), items: cart.map(({id, quantity}) => ({id, quantity})) }) });
  const result = await response.json();
  if (response.status === 401 && result.login_url) return window.location.assign(result.login_url);
  if (!response.ok) return showToast(result.error || 'Something went wrong');
  localStorage.removeItem(cartKey); event.target.reset(); document.querySelector('[data-checkout-modal]').classList.remove('is-visible'); renderCart(); showToast(result.message);
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('[data-page-checkout]');
  if (!form) return;
  const buyNowId = Number(form.dataset.buyNowId);
  const isBuyNow = Number.isInteger(buyNowId) && buyNowId > 0;
  const cart = isBuyNow ? [{id: buyNowId, quantity: 1}] : readCart();
  const total = isBuyNow ? 0 : cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const summary = document.querySelector('[data-page-summary]');
  const totalNode = document.querySelector('[data-page-total]');
  if (!isBuyNow && summary) summary.innerHTML = cart.length ? cart.map((item) => `<div class="summary-item"><span>${item.name} × ${item.quantity}</span><strong>${money(item.price * item.quantity)}</strong></div>`).join('') : '<p class="muted-copy">Your bag is empty.</p>';
  if (!isBuyNow && totalNode) totalNode.textContent = money(total);
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!cart.length) return showToast('Your bag is empty');
    const button = form.querySelector('button[type="submit"]');
    const originalLabel = button.innerHTML;
    let completed = false;
    button.disabled = true;
    button.textContent = 'Processing purchase...';
    try {
      const response = await fetch('/api/purchases', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ customer: Object.fromEntries(new FormData(form)), items: cart.map(({id, quantity}) => ({id, quantity})) }) });
      const result = await response.json();
      if (response.status === 401 && result.login_url) {
        window.location.assign(result.login_url);
        return;
      }
      if (!response.ok) {
        showToast(result.error || 'Something went wrong');
        return;
      }
      if (!isBuyNow) localStorage.removeItem(cartKey);
      renderCart();
      document.querySelector('[data-purchase-message]').textContent = result.message;
      document.querySelector('[data-checkout-layout]').hidden = true;
      const confirmation = document.querySelector('[data-purchase-confirmation]');
      confirmation.hidden = false;
      confirmation.focus();
      completed = true;
    } catch {
      showToast('Purchase could not be processed. Please try again.');
    } finally {
      if (!completed) {
        button.disabled = false;
        button.innerHTML = originalLabel;
      }
    }
  });
});

renderCart();
