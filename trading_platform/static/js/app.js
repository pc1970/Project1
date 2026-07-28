// ── State ────────────────────────────────────────────────────────────────────
const S = {
  token: localStorage.getItem('token') || '',
  username: localStorage.getItem('username') || '',
  currentPage: 'dashboard',
  prices: {},
  prevPrices: {},
  portfolios: [],
  selectedPortfolio: null,
  ws: null,
  charts: {},
  orderSide: 'buy',
  availableStrategies: [],
  symbols: { forex: [], crypto: [], stocks: [] },
};

const API = '/api';

// ── HTTP helpers ─────────────────────────────────────────────────────────────
async function api(method, path, body) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json', ...(S.token ? { Authorization: `Bearer ${S.token}` } : {}) },
  };
  if (body) opts.body = JSON.stringify(body);
  const r = await fetch(API + path, opts);
  if (r.status === 401) { logout(); return null; }
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}
const GET = (p) => api('GET', p);
const POST = (p, b) => api('POST', p, b);
const PATCH = (p, b) => api('PATCH', p, b);
const DELETE = (p) => api('DELETE', p);

// ── Formatting ───────────────────────────────────────────────────────────────
function fmt(n, d = 2) { return n == null ? '--' : Number(n).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }
function fmtPrice(n) {
  if (n == null) return '--';
  const v = Math.abs(n);
  if (v >= 1000) return fmt(n, 2);
  if (v >= 1) return fmt(n, 4);
  return fmt(n, 6);
}
function fmtPnl(n) {
  const s = n >= 0 ? '+' : '';
  return `${s}$${fmt(Math.abs(n), 2)}`;
}
function colorPnl(n) { return n >= 0 ? 'positive' : 'negative'; }
function badgeSide(s) { return `<span class="badge badge-${s}">${s.toUpperCase()}</span>`; }
function badgeStatus(s) {
  const map = { filled: 'green', open: 'blue', pending: 'yellow', cancelled: 'red', rejected: 'red' };
  return `<span class="badge badge-${map[s] || 'blue'}">${s}</span>`;
}

// ── Login ────────────────────────────────────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');
  try {
    const fd = new FormData();
    fd.append('username', username);
    fd.append('password', password);
    const r = await fetch(`${API}/auth/token`, { method: 'POST', body: fd });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Login failed');
    S.token = data.access_token;
    S.username = data.username;
    localStorage.setItem('token', S.token);
    localStorage.setItem('username', S.username);
    showApp();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
});

function logout() {
  S.token = '';
  localStorage.removeItem('token');
  localStorage.removeItem('username');
  if (S.ws) S.ws.close();
  document.getElementById('app').classList.add('hidden');
  document.getElementById('login-screen').classList.remove('hidden');
}
document.getElementById('logout-btn').addEventListener('click', logout);

// ── App Init ─────────────────────────────────────────────────────────────────
async function showApp() {
  document.getElementById('login-screen').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');
  document.getElementById('header-username').textContent = S.username;
  await loadSymbols();
  await loadPortfolios();
  await loadAvailableStrategies();
  populateSymbolSelects();
  setupNavigation();
  connectWebSocket();
  navigateTo('dashboard');
  setInterval(refreshCurrentPage, 8000);
}

if (S.token) showApp();

// ── Navigation ───────────────────────────────────────────────────────────────
function setupNavigation() {
  document.querySelectorAll('.sidebar-nav a[data-page]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      navigateTo(link.dataset.page);
    });
  });
}

function navigateTo(page) {
  S.currentPage = page;
  document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
  document.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
  const pageEl = document.getElementById(`page-${page}`);
  if (pageEl) pageEl.classList.remove('hidden');
  const navLink = document.querySelector(`.sidebar-nav a[data-page="${page}"]`);
  if (navLink) navLink.classList.add('active');
  const titles = {
    dashboard: 'Dashboard', markets: 'Markets', trading: 'Trade',
    portfolio: 'Portfolio', strategies: 'Strategies', backtest: 'Backtester',
    history: 'Trade History', risk: 'Risk Management', alerts: 'Price Alerts',
  };
  document.getElementById('page-title').textContent = titles[page] || page;
  loadPage(page);
}

function refreshCurrentPage() { loadPage(S.currentPage); }

async function loadPage(page) {
  try {
    switch (page) {
      case 'dashboard': await loadDashboard(); break;
      case 'markets': await loadMarkets(); break;
      case 'trading': await loadTrading(); break;
      case 'portfolio': await loadPortfolio(); break;
      case 'strategies': await loadStrategies(); break;
      case 'backtest': setupBacktest(); break;
      case 'history': await loadHistory(); break;
      case 'risk': await loadRisk(); break;
      case 'alerts': await loadAlerts(); break;
    }
  } catch (err) { console.error('Page load error:', err); }
}

// ── WebSocket ─────────────────────────────────────────────────────────────────
function connectWebSocket() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  S.ws = new WebSocket(`${proto}://${location.host}/ws`);
  const dot = document.querySelector('.status-dot');
  const label = document.getElementById('ws-status');

  S.ws.onopen = () => {
    dot.className = 'status-dot connected';
    label.innerHTML = '<span class="status-dot connected"></span> Live';
  };
  S.ws.onclose = () => {
    dot.className = 'status-dot disconnected';
    label.innerHTML = '<span class="status-dot disconnected"></span> Disconnected';
    setTimeout(connectWebSocket, 3000);
  };
  S.ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.type === 'price') {
      S.prevPrices[msg.symbol] = S.prices[msg.symbol];
      S.prices[msg.symbol] = msg.price;
      updateLivePriceUI(msg.symbol, msg.price, msg.display);
    } else if (msg.type === 'snapshot') {
      Object.assign(S.prices, msg.prices);
    } else if (msg.type === 'order_filled') {
      showToast(`✓ Order filled: ${msg.side?.toUpperCase()} ${msg.symbol} @ ${fmtPrice(msg.fill_price)}`);
      loadPage(S.currentPage);
    }
  };
}

function updateLivePriceUI(symbol, price, display) {
  const prev = S.prevPrices[symbol];
  const dir = prev ? (price > prev ? 'up' : price < prev ? 'down' : '') : '';
  // Dashboard live prices
  const row = document.getElementById(`price-row-${symbol.replace(/[^a-z0-9]/gi, '-')}`);
  if (row) {
    const valEl = row.querySelector('.price-val');
    if (valEl) { valEl.textContent = fmtPrice(price); valEl.className = `price-val ${dir}`; }
  }
  // Ticker
  const ticker = document.getElementById(`ticker-${symbol.replace(/[^a-z0-9]/gi, '-')}`);
  if (ticker) {
    ticker.querySelector('.ticker-price').textContent = fmtPrice(price);
    ticker.className = `ticker-item ${dir}`;
  }
}

// ── Symbols & Portfolios ──────────────────────────────────────────────────────
async function loadSymbols() {
  const data = await GET('/market/symbols');
  if (data) S.symbols = data;
}

async function loadPortfolios() {
  const data = await GET('/portfolio');
  if (data && data.length) {
    S.portfolios = data;
    S.selectedPortfolio = data[0];
  }
}

async function loadAvailableStrategies() {
  const data = await GET('/strategies/available');
  if (data) S.availableStrategies = data;
}

function allSymbols() {
  return [
    ...S.symbols.forex, ...S.symbols.crypto, ...S.symbols.stocks
  ];
}

function populateSymbolSelects() {
  const allSyms = allSymbols();
  const selects = ['order-symbol', 'trade-chart-symbol', 'market-chart-symbol', 'bt-symbol', 'alert-symbol'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = allSyms.map(s => `<option value="${s.symbol}">${s.display || s.symbol}</option>`).join('');
  });
  // Backtest strategy
  const btStrat = document.getElementById('bt-strategy');
  if (btStrat) {
    btStrat.innerHTML = S.availableStrategies.map(s => `<option value="${s.type}">${s.type} - ${s.description}</option>`).join('');
  }
  // Strategy modal symbols multi-select
  const stratSyms = document.getElementById('strat-symbols');
  if (stratSyms) {
    stratSyms.innerHTML = allSyms.map(s => `<option value="${s.symbol}">${s.display || s.symbol}</option>`).join('');
  }
  // Strategy modal type
  const stratType = document.getElementById('strat-type');
  if (stratType) {
    stratType.innerHTML = S.availableStrategies.map(s => `<option value="${s.type}">${s.type}</option>`).join('');
    stratType.addEventListener('change', () => {
      const strat = S.availableStrategies.find(x => x.type === stratType.value);
      document.getElementById('strat-desc').textContent = strat ? strat.description : '';
      document.getElementById('strat-params').value = strat ? JSON.stringify(strat.default_params, null, 2) : '';
    });
    stratType.dispatchEvent(new Event('change'));
  }
  // Strategy modal portfolio
  const stratPort = document.getElementById('strat-portfolio');
  if (stratPort && S.portfolios.length) {
    stratPort.innerHTML = S.portfolios.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
  }
  // History portfolio
  const histPort = document.getElementById('history-portfolio');
  if (histPort && S.portfolios.length) {
    histPort.innerHTML = S.portfolios.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
    histPort.addEventListener('change', loadHistory);
  }
  // Dashboard symbol chart
  buildTicker();
}

function buildTicker() {
  const strip = document.getElementById('ticker-strip');
  if (!strip) return;
  const syms = allSymbols().slice(0, 12);
  strip.innerHTML = syms.map(s => {
    const id = `ticker-${s.symbol.replace(/[^a-z0-9]/gi, '-')}`;
    return `<span class="ticker-item" id="${id}"><span class="ticker-sym">${s.display || s.symbol}</span> <span class="ticker-price">${fmtPrice(S.prices[s.symbol] || 0)}</span></span>`;
  }).join('');
}

// ── Dashboard ─────────────────────────────────────────────────────────────────
async function loadDashboard() {
  await loadPortfolios();
  const p = S.selectedPortfolio;
  if (p) {
    document.getElementById('stat-total-value').textContent = `$${fmt(p.total_value)}`;
    document.getElementById('stat-balance').textContent = `$${fmt(p.balance)}`;
    document.getElementById('stat-positions').textContent = p.position_count;
    const unreal = p.unrealized_pnl;
    const unrEl = document.getElementById('stat-unrealized');
    unrEl.textContent = fmtPnl(unreal);
    unrEl.className = `stat-value ${colorPnl(unreal)}`;
    const pnlPct = p.total_pnl_pct;
    document.getElementById('stat-total-change').textContent = `${pnlPct >= 0 ? '+' : ''}${fmt(pnlPct)}%`;
    document.getElementById('stat-total-change').className = `stat-change ${pnlPct >= 0 ? 'up' : 'down'}`;
  }
  // Active strategies count
  const strats = await GET('/strategies');
  if (strats) {
    document.getElementById('stat-strategies').textContent = strats.filter(s => s.status === 'active').length;
  }
  // Live prices
  buildLivePrices();
  // Positions
  if (p) await buildDashPositions(p.id);
  // Recent trades
  await buildRecentTrades();
  // Dashboard chart
  buildDashChart();
}

function buildLivePrices() {
  const container = document.getElementById('live-prices');
  if (!container) return;
  const syms = allSymbols().slice(0, 15);
  container.innerHTML = syms.map(s => {
    const id = `price-row-${s.symbol.replace(/[^a-z0-9]/gi, '-')}`;
    const price = S.prices[s.symbol] || 0;
    return `<div class="price-row" id="${id}">
      <span class="price-symbol">${s.display || s.symbol}</span>
      <span class="price-val">${fmtPrice(price)}</span>
    </div>`;
  }).join('');
}

async function buildDashPositions(portfolioId) {
  const positions = await GET(`/portfolio/${portfolioId}/positions`);
  const tbody = document.getElementById('dash-positions-body');
  if (!tbody || !positions) return;
  tbody.innerHTML = positions.slice(0, 8).map(p => `
    <tr>
      <td>${p.display || p.symbol}</td>
      <td>${badgeSide(p.side)}</td>
      <td>${fmt(p.quantity, 4)}</td>
      <td>${fmtPrice(p.avg_entry_price)}</td>
      <td>${fmtPrice(p.current_price)}</td>
      <td class="${colorPnl(p.unrealized_pnl)}">${fmtPnl(p.unrealized_pnl)}</td>
    </tr>`).join('') || '<tr><td colspan="6" style="text-align:center;color:var(--text-muted)">No open positions</td></tr>';
}

async function buildRecentTrades() {
  const orders = await GET('/orders?limit=8');
  const tbody = document.getElementById('recent-trades-body');
  if (!tbody || !orders) return;
  const filled = orders.filter(o => o.status === 'filled');
  tbody.innerHTML = filled.slice(0, 8).map(o => `
    <tr>
      <td>${o.display || o.symbol}</td>
      <td>${badgeSide(o.side)}</td>
      <td>${fmtPrice(o.avg_fill_price)}</td>
      <td>${fmt(o.filled_quantity, 4)}</td>
      <td>--</td>
    </tr>`).join('') || '<tr><td colspan="5" style="text-align:center;color:var(--text-muted)">No trades yet</td></tr>';
}

async function buildDashChart() {
  const sym = document.getElementById('dash-symbol-select')?.value || 'EURUSD=X';
  const data = await GET(`/market/history/${sym}?period=1mo&interval=1d`);
  if (!data) return;
  renderLineChart('dash-chart', data.data.map(d => ({ x: d.t, y: d.c })), sym);
}

document.getElementById('dash-symbol-select')?.addEventListener('change', buildDashChart);

// ── Markets ───────────────────────────────────────────────────────────────────
let marketFilter = 'all';
async function loadMarkets() {
  const syms = allSymbols();
  renderMarketTable(syms);
  buildMarketChart();
  // Populate chart symbol select
  const sel = document.getElementById('market-chart-symbol');
  if (sel) sel.innerHTML = syms.map(s => `<option value="${s.symbol}">${s.display || s.symbol}</option>`).join('');

  document.querySelectorAll('#market-filter .tab-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('#market-filter .tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      marketFilter = btn.dataset.filter;
      const filtered = marketFilter === 'all' ? syms :
        marketFilter === 'forex' ? S.symbols.forex :
        marketFilter === 'crypto' ? S.symbols.crypto : S.symbols.stocks;
      renderMarketTable(filtered);
    };
  });
  document.getElementById('market-chart-symbol')?.addEventListener('change', buildMarketChart);
  document.getElementById('market-chart-interval')?.addEventListener('change', buildMarketChart);
}

function renderMarketTable(syms) {
  const tbody = document.getElementById('market-table-body');
  if (!tbody) return;
  tbody.innerHTML = syms.map(s => {
    const price = S.prices[s.symbol] || 0;
    const change = (Math.random() - 0.48) * 2; // simulated
    return `<tr>
      <td><strong>${s.display || s.symbol}</strong></td>
      <td class="price-val">${fmtPrice(price)}</td>
      <td class="${change >= 0 ? 'positive' : 'negative'}">${change >= 0 ? '+' : ''}${fmt(change, 2)}%</td>
      <td>${fmtPrice(price * 1.005)}</td>
      <td>${fmtPrice(price * 0.995)}</td>
      <td><button class="btn-primary btn-sm" onclick="quickTrade('${s.symbol}')">Trade</button></td>
    </tr>`;
  }).join('');
}

async function buildMarketChart() {
  const sym = document.getElementById('market-chart-symbol')?.value || 'EURUSD=X';
  const interval = document.getElementById('market-chart-interval')?.value || '1d';
  const period = interval === '5m' ? '5d' : interval === '1h' ? '1mo' : '3mo';
  const data = await GET(`/market/history/${sym}?period=${period}&interval=${interval}`);
  if (!data) return;
  renderLineChart('market-chart', data.data.map(d => ({ x: d.t, y: d.c })), sym);
}

function quickTrade(symbol) {
  navigateTo('trading');
  const sel = document.getElementById('order-symbol');
  if (sel) { sel.value = symbol; sel.dispatchEvent(new Event('change')); }
}

// ── Trading ───────────────────────────────────────────────────────────────────
async function loadTrading() {
  await loadOpenOrders();
  setupOrderForm();
  buildTradeChart();
}

function setupOrderForm() {
  // Side tabs
  document.querySelectorAll('.order-tab').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.order-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      S.orderSide = tab.dataset.side;
      const btn = document.getElementById('order-submit');
      if (btn) {
        btn.className = `btn-${S.orderSide} btn-full`;
        btn.textContent = `Place ${S.orderSide.toUpperCase()} Order`;
      }
    };
  });
  // Order type toggle
  document.getElementById('order-type')?.addEventListener('change', (e) => {
    const priceGroup = document.getElementById('order-price-group');
    if (priceGroup) priceGroup.style.display = e.target.value === 'market' ? 'none' : 'block';
  });
  // Symbol price update
  document.getElementById('order-symbol')?.addEventListener('change', updateOrderPrice);
  updateOrderPrice();
  // Trade chart
  document.getElementById('trade-chart-symbol')?.addEventListener('change', buildTradeChart);
}

function updateOrderPrice() {
  const sym = document.getElementById('order-symbol')?.value;
  const price = sym ? S.prices[sym] : null;
  const el = document.getElementById('order-curr-price');
  if (el) el.textContent = `Current Price: ${fmtPrice(price)}`;
}

async function loadOpenOrders() {
  const orders = await GET('/orders?limit=20');
  const tbody = document.getElementById('open-orders-body');
  if (!tbody || !orders) return;
  const active = orders.filter(o => ['pending', 'open'].includes(o.status));
  tbody.innerHTML = active.map(o => `
    <tr>
      <td>${o.display || o.symbol}</td>
      <td>${o.order_type}</td>
      <td>${badgeSide(o.side)}</td>
      <td>${fmt(o.quantity, 4)}</td>
      <td>${o.price ? fmtPrice(o.price) : 'Market'}</td>
      <td>${badgeStatus(o.status)}</td>
      <td>${new Date(o.created_at).toLocaleString()}</td>
      <td><button class="btn-danger" onclick="cancelOrder(${o.id})">Cancel</button></td>
    </tr>`).join('') || '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">No open orders</td></tr>';
}

async function cancelOrder(id) {
  try { await DELETE(`/orders/${id}`); await loadOpenOrders(); }
  catch (e) { showToast('Cancel failed: ' + e.message, true); }
}

document.getElementById('order-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const errEl = document.getElementById('order-error');
  const sucEl = document.getElementById('order-success');
  errEl.classList.add('hidden');
  sucEl.classList.add('hidden');
  const portId = S.selectedPortfolio?.id;
  if (!portId) { errEl.textContent = 'No portfolio found'; errEl.classList.remove('hidden'); return; }
  const symbol = document.getElementById('order-symbol').value;
  const orderType = document.getElementById('order-type').value;
  const qty = parseFloat(document.getElementById('order-quantity').value) || null;
  const price = parseFloat(document.getElementById('order-price').value) || null;
  const sl = parseFloat(document.getElementById('order-sl').value) || null;
  const tp = parseFloat(document.getElementById('order-tp').value) || null;
  try {
    const result = await POST('/orders', {
      portfolio_id: portId, symbol, side: S.orderSide, order_type: orderType,
      quantity: qty, price, stop_loss: sl, take_profit: tp, use_risk_sizing: !qty,
    });
    sucEl.textContent = `Order ${result.status}: ${result.side?.toUpperCase()} ${fmt(result.fill_qty || result.quantity, 4)} ${symbol} @ ${fmtPrice(result.fill_price)}`;
    sucEl.classList.remove('hidden');
    document.getElementById('order-form').reset();
    await loadOpenOrders();
    await loadPortfolios();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  }
});

async function buildTradeChart() {
  const sym = document.getElementById('trade-chart-symbol')?.value || 'EURUSD=X';
  const data = await GET(`/market/history/${sym}?period=2mo&interval=1d`);
  if (!data) return;
  renderLineChart('trade-chart', data.data.map(d => ({ x: d.t, y: d.c })), sym);
}

// ── Portfolio ─────────────────────────────────────────────────────────────────
async function loadPortfolio() {
  await loadPortfolios();
  const container = document.getElementById('portfolio-stats');
  if (container && S.portfolios.length) {
    container.innerHTML = S.portfolios.map(p => `
      <div class="port-stat-card">
        <div class="stat-label">${p.name}</div>
        <div class="stat-value">$${fmt(p.total_value)}</div>
        <div class="stat-change ${p.total_pnl >= 0 ? 'up' : 'down'}">
          ${fmtPnl(p.total_pnl)} (${p.total_pnl_pct >= 0 ? '+' : ''}${fmt(p.total_pnl_pct)}%)
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:6px">
          Cash: $${fmt(p.balance)} | Unrealized: ${fmtPnl(p.unrealized_pnl)}
        </div>
      </div>`).join('');
  }
  if (S.selectedPortfolio) {
    await loadPositions(S.selectedPortfolio.id);
    await loadPerformance(S.selectedPortfolio.id);
  }
  document.getElementById('perf-days')?.addEventListener('change', () => {
    if (S.selectedPortfolio) loadPerformance(S.selectedPortfolio.id);
  });
}

async function loadPositions(portfolioId) {
  const positions = await GET(`/portfolio/${portfolioId}/positions`);
  const tbody = document.getElementById('positions-body');
  if (!tbody || !positions) return;
  tbody.innerHTML = positions.map(p => `
    <tr>
      <td><strong>${p.display || p.symbol}</strong></td>
      <td>${badgeSide(p.side)}</td>
      <td>${fmt(p.quantity, 4)}</td>
      <td>${fmtPrice(p.avg_entry_price)}</td>
      <td>${fmtPrice(p.current_price)}</td>
      <td>$${fmt(p.position_value)}</td>
      <td class="${colorPnl(p.unrealized_pnl)}">${fmtPnl(p.unrealized_pnl)} (${p.unrealized_pnl_pct >= 0 ? '+' : ''}${fmt(p.unrealized_pnl_pct)}%)</td>
      <td class="${colorPnl(p.realized_pnl)}">${fmtPnl(p.realized_pnl)}</td>
      <td>${p.stop_loss ? fmtPrice(p.stop_loss) : '--'}</td>
      <td>${p.take_profit ? fmtPrice(p.take_profit) : '--'}</td>
      <td><button class="btn-danger" onclick="closePosition(${portfolioId}, '${p.symbol}', ${p.quantity})">Close</button></td>
    </tr>`).join('') || '<tr><td colspan="11" style="text-align:center;color:var(--text-muted)">No open positions</td></tr>';
}

async function closePosition(portfolioId, symbol, qty) {
  if (!confirm(`Close position: SELL ${fmt(qty, 4)} ${symbol}?`)) return;
  try {
    await POST('/orders', {
      portfolio_id: portfolioId, symbol, side: 'sell',
      order_type: 'market', quantity: qty, use_risk_sizing: false,
    });
    showToast(`Position closed: ${symbol}`);
    await loadPortfolio();
  } catch (e) { showToast('Close failed: ' + e.message, true); }
}

async function loadPerformance(portfolioId) {
  const days = document.getElementById('perf-days')?.value || 30;
  const data = await GET(`/analytics/performance?portfolio_id=${portfolioId}&days=${days}`);
  if (!data) return;
  const container = document.getElementById('perf-stats');
  if (container) {
    container.innerHTML = [
      ['Total Trades', data.total_trades],
      ['Win Rate', `${fmt(data.win_rate)}%`],
      ['Total P&L', `<span class="${colorPnl(data.total_pnl)}">${fmtPnl(data.total_pnl)}</span>`],
      ['Profit Factor', fmt(data.profit_factor, 3)],
      ['Avg Win', `$${fmt(data.avg_win)}`],
      ['Avg Loss', `$${fmt(data.avg_loss)}`],
      ['Commission', `$${fmt(data.total_commission)}`],
    ].map(([l, v]) => `<div class="perf-stat"><div class="perf-stat-label">${l}</div><div class="perf-stat-val">${v}</div></div>`).join('');
  }
  // P&L chart
  if (data.daily_pnl.length) {
    const pts = data.daily_pnl.map(d => ({ x: new Date(d.date).getTime(), y: d.pnl }));
    renderBarChart('perf-chart', pts, 'Daily P&L');
  }
}

// ── Strategies ────────────────────────────────────────────────────────────────
async function loadStrategies() {
  const strats = await GET('/strategies');
  const container = document.getElementById('strategies-list');
  if (!container || !strats) return;
  if (!strats.length) {
    container.innerHTML = '<p style="color:var(--text-muted);padding:16px">No strategies yet. Create one to start automated trading.</p>';
    return;
  }
  container.innerHTML = strats.map(s => `
    <div class="strategy-card">
      <div class="strategy-card-header">
        <div>
          <div class="strategy-name">${s.name}</div>
          <div style="font-size:12px;color:var(--text-muted)">${s.strategy_type} · ${s.symbols.join(', ')}</div>
        </div>
        <div class="strategy-actions">
          ${s.status === 'active'
            ? `<button class="btn-secondary btn-sm" onclick="updateStrategyStatus(${s.id},'paused')">Pause</button>`
            : `<button class="btn-primary btn-sm" onclick="updateStrategyStatus(${s.id},'active')">Start</button>`}
          <button class="btn-danger" onclick="deleteStrategy(${s.id})">Delete</button>
        </div>
      </div>
      <div class="strategy-meta">
        <div class="strategy-stat"><span class="stat-label">Status</span><span class="strategy-stat-val">${badgeStatus(s.status)}</span></div>
        <div class="strategy-stat"><span class="stat-label">P&L</span><span class="strategy-stat-val ${colorPnl(s.total_profit_loss)}">${fmtPnl(s.total_profit_loss)}</span></div>
        <div class="strategy-stat"><span class="stat-label">Trades</span><span class="strategy-stat-val">${s.total_trades}</span></div>
        <div class="strategy-stat"><span class="stat-label">Win Rate</span><span class="strategy-stat-val">${fmt(s.win_rate)}%</span></div>
        <div class="strategy-stat"><span class="stat-label">Risk/Trade</span><span class="strategy-stat-val">${s.risk_per_trade}%</span></div>
      </div>
    </div>`).join('');

  // Setup modal
  setupStrategyModal();
}

function setupStrategyModal() {
  document.getElementById('new-strategy-btn').onclick = () => {
    document.getElementById('strategy-modal').classList.remove('hidden');
  };
  document.getElementById('strategy-modal-close').onclick =
  document.getElementById('strategy-cancel').onclick = () => {
    document.getElementById('strategy-modal').classList.add('hidden');
  };
}

document.getElementById('strategy-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const symSelect = document.getElementById('strat-symbols');
  const symbols = Array.from(symSelect.selectedOptions).map(o => o.value);
  if (!symbols.length) { alert('Select at least one symbol'); return; }
  let params = null;
  const paramsStr = document.getElementById('strat-params').value.trim();
  if (paramsStr) { try { params = JSON.parse(paramsStr); } catch { alert('Invalid JSON parameters'); return; } }
  try {
    await POST('/strategies', {
      name: document.getElementById('strat-name').value,
      strategy_type: document.getElementById('strat-type').value,
      symbols,
      parameters: params,
      portfolio_id: parseInt(document.getElementById('strat-portfolio').value),
      risk_per_trade: parseFloat(document.getElementById('strat-risk').value),
      max_positions: parseInt(document.getElementById('strat-maxpos').value),
    });
    document.getElementById('strategy-modal').classList.add('hidden');
    showToast('Strategy created!');
    await loadStrategies();
  } catch (e) { alert('Error: ' + e.message); }
});

async function updateStrategyStatus(id, status) {
  try { await PATCH(`/strategies/${id}/status`, { status }); await loadStrategies(); }
  catch (e) { showToast('Error: ' + e.message, true); }
}

async function deleteStrategy(id) {
  if (!confirm('Delete this strategy?')) return;
  try { await DELETE(`/strategies/${id}`); await loadStrategies(); }
  catch (e) { showToast('Error: ' + e.message, true); }
}

// ── Backtest ──────────────────────────────────────────────────────────────────
function setupBacktest() {
  const btStrat = document.getElementById('bt-strategy');
  if (btStrat && !btStrat.innerHTML) {
    btStrat.innerHTML = S.availableStrategies.map(s => `<option value="${s.type}">${s.type}</option>`).join('');
  }
}

document.getElementById('backtest-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = document.getElementById('bt-run-btn');
  btn.textContent = 'Running...';
  btn.disabled = true;
  let params = null;
  const ps = document.getElementById('bt-params').value.trim();
  if (ps) { try { params = JSON.parse(ps); } catch { alert('Invalid JSON'); btn.textContent = 'Run Backtest'; btn.disabled = false; return; } }
  try {
    const result = await POST('/backtest', {
      strategy_type: document.getElementById('bt-strategy').value,
      symbol: document.getElementById('bt-symbol').value,
      period: document.getElementById('bt-period').value,
      interval: document.getElementById('bt-interval').value,
      initial_capital: parseFloat(document.getElementById('bt-capital').value),
      risk_per_trade: parseFloat(document.getElementById('bt-risk').value),
      parameters: params,
    });
    renderBacktestResults(result);
  } catch (e) { showToast('Backtest error: ' + e.message, true); }
  btn.textContent = 'Run Backtest';
  btn.disabled = false;
});

function renderBacktestResults(r) {
  document.getElementById('bt-results').classList.remove('hidden');
  const grid = document.getElementById('bt-stats-grid');
  grid.innerHTML = [
    ['Total Return', `<span class="${colorPnl(r.total_return)}">${r.total_return_pct >= 0 ? '+' : ''}${fmt(r.total_return_pct)}%</span>`],
    ['Final Capital', `$${fmt(r.final_capital)}`],
    ['Max Drawdown', `<span class="negative">-${fmt(r.max_drawdown_pct)}%</span>`],
    ['Sharpe Ratio', fmt(r.sharpe_ratio, 3)],
    ['Win Rate', `${fmt(r.win_rate_pct)}%`],
    ['Profit Factor', fmt(r.profit_factor, 3)],
    ['Total Trades', r.total_trades],
    ['Avg Win', `$${fmt(r.avg_win)}`],
    ['Avg Loss', `$${fmt(r.avg_loss)}`],
    ['Max Consec. Losses', r.max_consecutive_losses],
    ['Calmar Ratio', fmt(r.calmar_ratio, 3)],
    ['Sortino Ratio', fmt(r.sortino_ratio, 3)],
  ].map(([l, v]) => `<div class="stat-card"><div class="stat-label">${l}</div><div class="stat-value">${v}</div></div>`).join('');

  // Equity curve
  const pts = r.equity_curve.map((v, i) => ({ x: i, y: v }));
  renderLineChart('bt-equity-chart', pts, 'Equity', false);

  // Trades
  const tbody = document.getElementById('bt-trades-body');
  tbody.innerHTML = r.trades.slice(0, 50).map(t => `
    <tr>
      <td>${t.entry_bar}</td>
      <td>${badgeSide(t.side)}</td>
      <td>${fmtPrice(t.entry_price)}</td>
      <td>${fmtPrice(t.exit_price)}</td>
      <td>${fmt(t.quantity, 4)}</td>
      <td class="${colorPnl(t.pnl)}">${fmtPnl(t.pnl)}</td>
      <td>${t.reason}</td>
    </tr>`).join('');
}

// ── History ───────────────────────────────────────────────────────────────────
async function loadHistory() {
  const portId = document.getElementById('history-portfolio')?.value || S.selectedPortfolio?.id;
  const query = portId ? `?portfolio_id=${portId}&limit=100` : '?limit=100';
  const orders = await GET(`/orders${query}`);
  const tbody = document.getElementById('history-body');
  if (!tbody || !orders) return;
  tbody.innerHTML = orders.map(o => `
    <tr>
      <td>${o.display || o.symbol}</td>
      <td>${badgeSide(o.side)}</td>
      <td>${o.order_type}</td>
      <td>${fmt(o.quantity, 4)}</td>
      <td>${o.avg_fill_price ? fmtPrice(o.avg_fill_price) : '--'}</td>
      <td>$${fmt(o.commission, 4)}</td>
      <td>${badgeStatus(o.status)}</td>
      <td>${new Date(o.created_at).toLocaleString()}</td>
    </tr>`).join('') || '<tr><td colspan="8" style="text-align:center;color:var(--text-muted)">No orders yet</td></tr>';
}

// ── Risk ──────────────────────────────────────────────────────────────────────
async function loadRisk() {
  const params = await GET('/risk/params');
  if (!params) return;
  const map = {
    'risk-portfolio-pct': 'max_portfolio_risk_pct',
    'risk-trade-pct': 'max_single_trade_risk_pct',
    'risk-position-pct': 'max_position_size_pct',
    'risk-drawdown-pct': 'max_drawdown_pct',
    'risk-daily-pct': 'max_daily_loss_pct',
    'risk-max-positions': 'max_open_positions',
    'risk-min-rr': 'min_risk_reward',
    'risk-kelly-fraction': 'kelly_fraction',
  };
  Object.entries(map).forEach(([elId, key]) => {
    const el = document.getElementById(elId);
    if (el) el.value = params[key];
  });
  const kellyEl = document.getElementById('risk-kelly');
  if (kellyEl) kellyEl.checked = params.use_kelly_criterion;
}

document.getElementById('risk-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const sucEl = document.getElementById('risk-success');
  const body = {
    max_portfolio_risk_pct: parseFloat(document.getElementById('risk-portfolio-pct').value),
    max_single_trade_risk_pct: parseFloat(document.getElementById('risk-trade-pct').value),
    max_position_size_pct: parseFloat(document.getElementById('risk-position-pct').value),
    max_drawdown_pct: parseFloat(document.getElementById('risk-drawdown-pct').value),
    max_daily_loss_pct: parseFloat(document.getElementById('risk-daily-pct').value),
    max_open_positions: parseInt(document.getElementById('risk-max-positions').value),
    min_risk_reward: parseFloat(document.getElementById('risk-min-rr').value),
    use_kelly_criterion: document.getElementById('risk-kelly').checked,
    kelly_fraction: parseFloat(document.getElementById('risk-kelly-fraction').value),
  };
  try {
    await PATCH('/risk/params', body);
    sucEl.classList.remove('hidden');
    setTimeout(() => sucEl.classList.add('hidden'), 3000);
  } catch (e) { showToast('Error: ' + e.message, true); }
});

// ── Alerts ────────────────────────────────────────────────────────────────────
async function loadAlerts() {
  const alerts = await GET('/alerts');
  const tbody = document.getElementById('alerts-body');
  if (!tbody || !alerts) return;
  tbody.innerHTML = alerts.map(a => `
    <tr>
      <td>${a.symbol}</td>
      <td>${a.condition}</td>
      <td>${fmtPrice(a.price)}</td>
      <td>${a.message || '--'}</td>
      <td>${a.triggered ? '<span class="badge badge-green">Triggered</span>' : '<span class="badge badge-blue">Active</span>'}</td>
      <td>${a.triggered_at ? new Date(a.triggered_at).toLocaleString() : '--'}</td>
      <td><button class="btn-danger" onclick="deleteAlert(${a.id})">Delete</button></td>
    </tr>`).join('') || '<tr><td colspan="7" style="text-align:center;color:var(--text-muted)">No alerts set</td></tr>';

  document.getElementById('new-alert-btn').onclick = () => document.getElementById('alert-modal').classList.remove('hidden');
  document.getElementById('alert-modal-close').onclick =
  document.getElementById('alert-cancel').onclick = () => document.getElementById('alert-modal').classList.add('hidden');
}

document.getElementById('alert-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await POST('/alerts', {
      symbol: document.getElementById('alert-symbol').value,
      condition: document.getElementById('alert-condition').value,
      price: parseFloat(document.getElementById('alert-price').value),
      message: document.getElementById('alert-message').value || null,
    });
    document.getElementById('alert-modal').classList.add('hidden');
    showToast('Alert created!');
    await loadAlerts();
  } catch (e) { showToast('Error: ' + e.message, true); }
});

async function deleteAlert(id) {
  try { await DELETE(`/alerts/${id}`); await loadAlerts(); }
  catch (e) { showToast('Error: ' + e.message, true); }
}

// ── Charts ────────────────────────────────────────────────────────────────────
function renderLineChart(canvasId, data, label, useTimeScale = true) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  if (S.charts[canvasId]) { S.charts[canvasId].destroy(); }
  const ctx = canvas.getContext('2d');
  const color = '#2563eb';
  S.charts[canvasId] = new Chart(ctx, {
    type: 'line',
    data: {
      datasets: [{
        label, data,
        borderColor: color, borderWidth: 1.5,
        backgroundColor: color + '18',
        fill: true, pointRadius: 0, tension: 0.2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true, animation: false,
      plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } },
      scales: {
        x: useTimeScale
          ? { type: 'time', time: { unit: 'day' }, grid: { color: '#ffffff08' }, ticks: { color: '#64748b' } }
          : { grid: { color: '#ffffff08' }, ticks: { color: '#64748b' } },
        y: { grid: { color: '#ffffff08' }, ticks: { color: '#64748b' } },
      },
    },
  });
}

function renderBarChart(canvasId, data, label) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  if (S.charts[canvasId]) { S.charts[canvasId].destroy(); }
  const ctx = canvas.getContext('2d');
  S.charts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      datasets: [{
        label, data,
        backgroundColor: data.map(d => d.y >= 0 ? '#22c55e44' : '#ef444444'),
        borderColor: data.map(d => d.y >= 0 ? '#22c55e' : '#ef4444'),
        borderWidth: 1,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: true, animation: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { type: 'time', time: { unit: 'day' }, grid: { color: '#ffffff08' }, ticks: { color: '#64748b' } },
        y: { grid: { color: '#ffffff08' }, ticks: { color: '#64748b' } },
      },
    },
  });
}

// ── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg, isError = false) {
  const t = document.createElement('div');
  t.style.cssText = `position:fixed;bottom:24px;right:24px;padding:12px 20px;border-radius:8px;
    background:${isError ? '#ef4444' : '#22c55e'};color:#fff;font-weight:600;z-index:9999;
    box-shadow:0 4px 20px rgba(0,0,0,.5);font-size:14px;max-width:400px;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}
