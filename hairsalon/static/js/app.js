/* Glamour Hair Salon – frontend JS */
'use strict';

const API = '';  // same origin

// ============================================================
// Utility
// ============================================================
function fmt(date) {
  if (!date) return '–';
  const d = new Date(date + 'T00:00:00');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function fmtTime(t) {
  if (!t) return '–';
  const [h, m] = t.split(':');
  const hr = parseInt(h, 10);
  return `${hr % 12 || 12}:${m} ${hr < 12 ? 'AM' : 'PM'}`;
}

function statusBadge(status) {
  const map = {
    scheduled: 'bg-yellow-100 text-yellow-700',
    confirmed:  'bg-blue-100 text-blue-700',
    completed:  'bg-green-100 text-green-700',
    cancelled:  'bg-red-100 text-red-700',
  };
  return `<span class="status-badge ${map[status] || 'bg-gray-100 text-gray-600'}">${status}</span>`;
}

function notifBadge(email, sms) {
  const e = email ? '<span title="Email sent" class="text-green-500"><i class="fas fa-envelope"></i></span>'
                  : '<span title="Email not sent" class="text-gray-300"><i class="fas fa-envelope"></i></span>';
  const s = sms   ? '<span title="SMS sent" class="text-green-500"><i class="fas fa-sms"></i></span>'
                  : '<span title="SMS not sent" class="text-gray-300"><i class="fas fa-sms"></i></span>';
  return `<span class="flex gap-1">${e}${s}</span>`;
}

let _toastTimer = null;
function toast(msg, ok = true) {
  const el   = document.getElementById('toast');
  const icon = document.getElementById('toast-icon');
  const text = document.getElementById('toast-msg');
  icon.className = ok ? 'fas fa-check-circle text-green-400' : 'fas fa-exclamation-circle text-red-400';
  text.textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.add('hidden'), 3500);
}

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ============================================================
// Tab navigation
// ============================================================
const TABS = ['dashboard', 'appointments', 'services', 'customers', 'staff'];

function showTab(name) {
  TABS.forEach(t => {
    document.getElementById(`tab-content-${t}`).classList.toggle('hidden', t !== name);
    document.getElementById(`tab-${t}`).classList.toggle('active', t === name);
  });
  const loaders = {
    dashboard:    loadDashboard,
    appointments: loadAppointments,
    services:     loadServices,
    customers:    loadCustomers,
    staff:        loadStaff,
  };
  loaders[name]?.();
}

// ============================================================
// Dashboard
// ============================================================
async function loadDashboard() {
  try {
    const d = await api('/api/dashboard/stats');
    document.getElementById('stat-today').textContent     = d.total_today;
    document.getElementById('stat-revenue').textContent   = `$${d.revenue_today.toFixed(2)}`;
    document.getElementById('stat-customers').textContent = d.total_customers;
    document.getElementById('stat-staff').textContent     = d.active_staff;

    const tbody = document.getElementById('dashboard-upcoming');
    if (!d.upcoming.length) {
      tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-gray-400">No upcoming appointments</td></tr>`;
      return;
    }
    tbody.innerHTML = d.upcoming.map(a => `
      <tr class="border-b border-gray-50 hover:bg-gray-50 transition">
        <td class="py-2 pr-4 text-gray-600">${fmt(a.appointment_date)}</td>
        <td class="py-2 pr-4 text-gray-600">${fmtTime(a.appointment_time)}</td>
        <td class="py-2 pr-4 font-medium">${a.customer_name}</td>
        <td class="py-2 pr-4 text-gray-500">${a.service_name}</td>
        <td class="py-2 pr-4 text-gray-500">${a.staff_name}</td>
        <td class="py-2">${statusBadge(a.status)}</td>
      </tr>`).join('');
  } catch (e) {
    toast(e.message, false);
  }
}

// ============================================================
// Appointments
// ============================================================
async function loadAppointments() {
  const search = document.getElementById('appt-search')?.value.trim() || '';
  const date   = document.getElementById('appt-date-filter')?.value || '';
  const status = document.getElementById('appt-status-filter')?.value || '';

  const params = new URLSearchParams();
  if (search) params.set('search', search);
  if (date)   params.set('date', date);
  if (status) params.set('status', status);

  try {
    const list = await api(`/api/appointments?${params}`);
    const tbody = document.getElementById('appts-tbody');
    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="9" class="py-8 text-center text-gray-400">No appointments found</td></tr>`;
      return;
    }
    tbody.innerHTML = list.map(a => `
      <tr class="border-b border-gray-50 hover:bg-gray-50 transition">
        <td class="px-4 py-3 text-gray-600 whitespace-nowrap">${fmt(a.appointment_date)}</td>
        <td class="px-4 py-3 whitespace-nowrap">${fmtTime(a.appointment_time)}</td>
        <td class="px-4 py-3 font-medium">${a.customer_name}</td>
        <td class="px-4 py-3 text-gray-500">${a.service_name}</td>
        <td class="px-4 py-3 text-gray-500">${a.staff_name}</td>
        <td class="px-4 py-3 text-gray-700">$${parseFloat(a.price).toFixed(2)}</td>
        <td class="px-4 py-3">${statusBadge(a.status)}</td>
        <td class="px-4 py-3">${notifBadge(a.email_sent, a.sms_sent)}</td>
        <td class="px-4 py-3 whitespace-nowrap">
          <button onclick="openApptModal(${JSON.stringify(a).replace(/"/g,'&quot;')})"
            class="text-purple-600 hover:text-purple-800 mr-2" title="Edit"><i class="fas fa-edit"></i></button>
          <button onclick="sendReminder(${a.id})"
            class="text-blue-500 hover:text-blue-700 mr-2" title="Send reminder"><i class="fas fa-bell"></i></button>
          <button onclick="deleteAppt(${a.id})"
            class="text-red-400 hover:text-red-600" title="Delete"><i class="fas fa-trash"></i></button>
        </td>
      </tr>`).join('');
  } catch (e) {
    toast(e.message, false);
  }
}

let _cachedCustomers = [];
let _cachedStaff     = [];
let _cachedServices  = [];

async function openApptModal(appt = null) {
  // Load dropdowns
  [_cachedCustomers, _cachedStaff, _cachedServices] = await Promise.all([
    api('/api/customers'),
    api('/api/staff'),
    api('/api/services'),
  ]);

  const sel = (id, items, valKey, labelFn, selVal = '') =>
    (document.getElementById(id).innerHTML =
      items.map(i => `<option value="${i[valKey]}" ${i[valKey] == selVal ? 'selected' : ''}>${labelFn(i)}</option>`).join(''));

  sel('appt-customer', _cachedCustomers, 'id', c => c.name, appt?.customer_id);
  sel('appt-staff',    _cachedStaff.filter(s => s.active), 'id', s => s.name, appt?.staff_id);
  sel('appt-service',  _cachedServices, 'id', s => `${s.name} – $${parseFloat(s.price).toFixed(2)}`, appt?.service_id);

  document.getElementById('appt-id').value       = appt?.id || '';
  document.getElementById('appt-status').value   = appt?.status || 'scheduled';
  document.getElementById('appt-date').value      = appt?.appointment_date || '';
  document.getElementById('appt-time').value      = appt?.appointment_time || '';
  document.getElementById('appt-notes').value     = appt?.notes || '';
  document.getElementById('modal-appt-title').textContent = appt ? 'Edit Appointment' : 'New Appointment';
  document.getElementById('modal-appt').classList.remove('hidden');
}

async function submitApptForm(e) {
  e.preventDefault();
  const id = document.getElementById('appt-id').value;
  const body = {
    customer_id:      document.getElementById('appt-customer').value,
    staff_id:         document.getElementById('appt-staff').value,
    service_id:       document.getElementById('appt-service').value,
    appointment_date: document.getElementById('appt-date').value,
    appointment_time: document.getElementById('appt-time').value,
    status:           document.getElementById('appt-status').value,
    notes:            document.getElementById('appt-notes').value,
  };
  try {
    if (id) {
      await api(`/api/appointments/${id}`, { method: 'PUT', body: JSON.stringify(body) });
      toast('Appointment updated');
    } else {
      const appt = await api('/api/appointments', { method: 'POST', body: JSON.stringify(body) });
      const parts = [];
      if (appt.email_sent) parts.push('email');
      if (appt.sms_sent)   parts.push('SMS');
      toast(`Appointment booked${parts.length ? ' · Confirmation sent via ' + parts.join(' & ') : ''}`);
    }
    closeModal('modal-appt');
    loadAppointments();
    loadDashboard();
  } catch (err) {
    toast(err.message, false);
  }
}

async function deleteAppt(id) {
  if (!confirm('Delete this appointment?')) return;
  try {
    await api(`/api/appointments/${id}`, { method: 'DELETE' });
    toast('Appointment deleted');
    loadAppointments();
    loadDashboard();
  } catch (e) { toast(e.message, false); }
}

async function sendReminder(id) {
  try {
    const r = await api(`/api/appointments/${id}/remind`, { method: 'POST' });
    const parts = [];
    if (r.email) parts.push('email');
    if (r.sms)   parts.push('SMS');
    toast(parts.length ? `Reminder sent via ${parts.join(' & ')}` : 'Reminder: no contact info configured');
  } catch (e) { toast(e.message, false); }
}

// ============================================================
// Services
// ============================================================
async function loadServices() {
  try {
    const list = await api('/api/services');
    const grid = document.getElementById('services-grid');
    if (!list.length) { grid.innerHTML = `<p class="text-gray-400 col-span-3 text-center py-10">No services yet.</p>`; return; }
    grid.innerHTML = list.map(s => `
      <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3 hover:shadow-md transition">
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-semibold text-gray-800">${s.name}</h3>
            <p class="text-xs text-gray-400 mt-0.5">${s.description || 'No description'}</p>
          </div>
          <span class="text-purple-700 font-bold text-lg">$${parseFloat(s.price).toFixed(2)}</span>
        </div>
        <div class="flex items-center gap-2 text-xs text-gray-400">
          <i class="fas fa-clock"></i> ${s.duration_minutes} min
        </div>
        <div class="flex gap-2 pt-1">
          <button onclick="openServiceModal(${JSON.stringify(s).replace(/"/g,'&quot;')})"
            class="flex-1 text-sm py-1.5 rounded-lg border border-purple-200 text-purple-700 hover:bg-purple-50 transition">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button onclick="deleteService(${s.id})"
            class="flex-1 text-sm py-1.5 rounded-lg border border-red-100 text-red-400 hover:bg-red-50 transition">
            <i class="fas fa-trash"></i> Delete
          </button>
        </div>
      </div>`).join('');
  } catch (e) { toast(e.message, false); }
}

function openServiceModal(svc = null) {
  document.getElementById('service-id').value          = svc?.id || '';
  document.getElementById('service-name').value        = svc?.name || '';
  document.getElementById('service-desc').value        = svc?.description || '';
  document.getElementById('service-duration').value    = svc?.duration_minutes || '';
  document.getElementById('service-price').value       = svc?.price || '';
  document.getElementById('modal-service-title').textContent = svc ? 'Edit Service' : 'New Service';
  document.getElementById('modal-service').classList.remove('hidden');
}

async function submitServiceForm(e) {
  e.preventDefault();
  const id = document.getElementById('service-id').value;
  const body = {
    name:             document.getElementById('service-name').value,
    description:      document.getElementById('service-desc').value,
    duration_minutes: document.getElementById('service-duration').value,
    price:            document.getElementById('service-price').value,
  };
  try {
    if (id) {
      await api(`/api/services/${id}`, { method: 'PUT', body: JSON.stringify(body) });
      toast('Service updated');
    } else {
      await api('/api/services', { method: 'POST', body: JSON.stringify(body) });
      toast('Service added');
    }
    closeModal('modal-service');
    loadServices();
  } catch (err) { toast(err.message, false); }
}

async function deleteService(id) {
  if (!confirm('Delete this service?')) return;
  try {
    await api(`/api/services/${id}`, { method: 'DELETE' });
    toast('Service deleted');
    loadServices();
  } catch (e) { toast(e.message, false); }
}

// ============================================================
// Customers
// ============================================================
async function loadCustomers() {
  const search = document.getElementById('cust-search')?.value.trim() || '';
  const params = search ? `?search=${encodeURIComponent(search)}` : '';
  try {
    const list = await api(`/api/customers${params}`);
    const tbody = document.getElementById('customers-tbody');
    if (!list.length) {
      tbody.innerHTML = `<tr><td colspan="5" class="py-8 text-center text-gray-400">No customers found</td></tr>`;
      return;
    }
    tbody.innerHTML = list.map(c => `
      <tr class="border-b border-gray-50 hover:bg-gray-50 transition">
        <td class="px-4 py-3 font-medium">${c.name}</td>
        <td class="px-4 py-3 text-gray-500">${c.email || '–'}</td>
        <td class="px-4 py-3 text-gray-500">${c.phone || '–'}</td>
        <td class="px-4 py-3 text-gray-400 text-xs">${fmt(c.created_at?.split('T')[0] || c.created_at?.split(' ')[0])}</td>
        <td class="px-4 py-3 whitespace-nowrap">
          <button onclick="viewCustomerHistory(${c.id},'${c.name.replace(/'/g,"\\'")}' )"
            class="text-blue-500 hover:text-blue-700 mr-2" title="View history"><i class="fas fa-history"></i></button>
          <button onclick="openCustomerModal(${JSON.stringify(c).replace(/"/g,'&quot;')})"
            class="text-purple-600 hover:text-purple-800 mr-2" title="Edit"><i class="fas fa-edit"></i></button>
          <button onclick="deleteCustomer(${c.id})"
            class="text-red-400 hover:text-red-600" title="Delete"><i class="fas fa-trash"></i></button>
        </td>
      </tr>`).join('');
  } catch (e) { toast(e.message, false); }
}

function openCustomerModal(cust = null) {
  document.getElementById('customer-id').value    = cust?.id || '';
  document.getElementById('customer-name').value  = cust?.name || '';
  document.getElementById('customer-email').value = cust?.email || '';
  document.getElementById('customer-phone').value = cust?.phone || '';
  document.getElementById('modal-customer-title').textContent = cust ? 'Edit Customer' : 'New Customer';
  document.getElementById('modal-customer').classList.remove('hidden');
}

async function submitCustomerForm(e) {
  e.preventDefault();
  const id = document.getElementById('customer-id').value;
  const body = {
    name:  document.getElementById('customer-name').value,
    email: document.getElementById('customer-email').value,
    phone: document.getElementById('customer-phone').value,
  };
  try {
    if (id) {
      await api(`/api/customers/${id}`, { method: 'PUT', body: JSON.stringify(body) });
      toast('Customer updated');
    } else {
      await api('/api/customers', { method: 'POST', body: JSON.stringify(body) });
      toast('Customer added');
    }
    closeModal('modal-customer');
    loadCustomers();
  } catch (err) { toast(err.message, false); }
}

async function deleteCustomer(id) {
  if (!confirm('Delete this customer? Their appointment history will remain.')) return;
  try {
    await api(`/api/customers/${id}`, { method: 'DELETE' });
    toast('Customer deleted');
    loadCustomers();
  } catch (e) { toast(e.message, false); }
}

async function viewCustomerHistory(id, name) {
  try {
    const c = await api(`/api/customers/${id}`);
    const appts = c.appointments || [];
    document.getElementById('modal-history-title').textContent = `${name} – Visit History`;
    const content = document.getElementById('history-content');
    if (!appts.length) {
      content.innerHTML = `<p class="text-gray-400 text-center py-6">No appointments yet.</p>`;
    } else {
      const total = appts.filter(a => a.status === 'completed').reduce((s, a) => s + parseFloat(a.price || 0), 0);
      content.innerHTML = `
        <div class="flex items-center justify-between mb-3">
          <p class="text-xs text-gray-400">${appts.length} appointment(s)</p>
          <p class="text-sm font-semibold text-purple-700">Lifetime spend: $${total.toFixed(2)}</p>
        </div>
        <table class="w-full text-sm">
          <thead><tr class="text-left text-gray-400 border-b border-gray-100">
            <th class="pb-2 pr-3">Date</th><th class="pb-2 pr-3">Service</th>
            <th class="pb-2 pr-3">Stylist</th><th class="pb-2 pr-3">Price</th><th class="pb-2">Status</th>
          </tr></thead>
          <tbody>
            ${appts.map(a => `
              <tr class="border-b border-gray-50">
                <td class="py-2 pr-3 text-gray-500 whitespace-nowrap">${fmt(a.appointment_date)}</td>
                <td class="py-2 pr-3">${a.service_name}</td>
                <td class="py-2 pr-3 text-gray-500">${a.staff_name}</td>
                <td class="py-2 pr-3">$${parseFloat(a.price).toFixed(2)}</td>
                <td class="py-2">${statusBadge(a.status)}</td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    }
    document.getElementById('modal-history').classList.remove('hidden');
  } catch (e) { toast(e.message, false); }
}

// ============================================================
// Staff
// ============================================================
const AVATAR_COLORS = ['bg-purple-200 text-purple-800', 'bg-pink-200 text-pink-800',
  'bg-blue-200 text-blue-800', 'bg-green-200 text-green-800', 'bg-yellow-200 text-yellow-800'];

async function loadStaff() {
  try {
    const list = await api('/api/staff');
    const grid = document.getElementById('staff-grid');
    if (!list.length) { grid.innerHTML = `<p class="text-gray-400 col-span-3 text-center py-10">No staff yet.</p>`; return; }
    grid.innerHTML = list.map((s, i) => `
      <div class="bg-white rounded-2xl shadow-sm p-5 flex flex-col gap-3 hover:shadow-md transition">
        <div class="flex items-center gap-3">
          <div class="w-12 h-12 rounded-full ${AVATAR_COLORS[i % AVATAR_COLORS.length]} flex items-center justify-center font-bold text-lg">
            ${s.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()}
          </div>
          <div>
            <p class="font-semibold text-gray-800">${s.name}</p>
            <p class="text-xs text-gray-400">${s.role}</p>
          </div>
          <div class="ml-auto">
            ${s.active
              ? '<span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">Active</span>'
              : '<span class="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">Inactive</span>'}
          </div>
        </div>
        <div class="text-xs text-gray-400 space-y-1">
          ${s.email ? `<p><i class="fas fa-envelope mr-1"></i>${s.email}</p>` : ''}
          ${s.phone ? `<p><i class="fas fa-phone mr-1"></i>${s.phone}</p>` : ''}
        </div>
        <div class="flex gap-2 pt-1">
          <button onclick="openStaffModal(${JSON.stringify(s).replace(/"/g,'&quot;')})"
            class="flex-1 text-sm py-1.5 rounded-lg border border-purple-200 text-purple-700 hover:bg-purple-50 transition">
            <i class="fas fa-edit"></i> Edit
          </button>
          <button onclick="deleteStaff(${s.id})"
            class="flex-1 text-sm py-1.5 rounded-lg border border-red-100 text-red-400 hover:bg-red-50 transition">
            <i class="fas fa-trash"></i> Remove
          </button>
        </div>
      </div>`).join('');
  } catch (e) { toast(e.message, false); }
}

function openStaffModal(stf = null) {
  document.getElementById('staff-id').value     = stf?.id || '';
  document.getElementById('staff-name').value   = stf?.name || '';
  document.getElementById('staff-role').value   = stf?.role || '';
  document.getElementById('staff-email').value  = stf?.email || '';
  document.getElementById('staff-phone').value  = stf?.phone || '';
  document.getElementById('staff-active').checked = stf ? !!stf.active : true;
  document.getElementById('modal-staff-title').textContent = stf ? 'Edit Staff' : 'New Staff Member';
  document.getElementById('modal-staff').classList.remove('hidden');
}

async function submitStaffForm(e) {
  e.preventDefault();
  const id = document.getElementById('staff-id').value;
  const body = {
    name:   document.getElementById('staff-name').value,
    role:   document.getElementById('staff-role').value,
    email:  document.getElementById('staff-email').value,
    phone:  document.getElementById('staff-phone').value,
    active: document.getElementById('staff-active').checked ? 1 : 0,
  };
  try {
    if (id) {
      await api(`/api/staff/${id}`, { method: 'PUT', body: JSON.stringify(body) });
      toast('Staff member updated');
    } else {
      await api('/api/staff', { method: 'POST', body: JSON.stringify(body) });
      toast('Staff member added');
    }
    closeModal('modal-staff');
    loadStaff();
  } catch (err) { toast(err.message, false); }
}

async function deleteStaff(id) {
  if (!confirm('Remove this staff member?')) return;
  try {
    await api(`/api/staff/${id}`, { method: 'DELETE' });
    toast('Staff member removed');
    loadStaff();
  } catch (e) { toast(e.message, false); }
}

// ============================================================
// Modal helpers
// ============================================================
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

// Close on backdrop click
document.querySelectorAll('[id^="modal-"]').forEach(el => {
  el.addEventListener('click', e => {
    if (e.target === el) closeModal(el.id);
  });
});

// ============================================================
// Init
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
});
