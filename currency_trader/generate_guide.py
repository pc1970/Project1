"""Generate Currency Trader Pro PDF user guide using ReportLab."""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate

# ── Colour palette ─────────────────────────────────────────────────────────────
DARK_BG    = colors.HexColor("#0f1629")
ACCENT     = colors.HexColor("#3b82f6")
GREEN      = colors.HexColor("#10b981")
RED        = colors.HexColor("#ef4444")
GOLD       = colors.HexColor("#f59e0b")
LIGHT_GREY = colors.HexColor("#e5e7eb")
MID_GREY   = colors.HexColor("#9ca3af")
DARK_GREY  = colors.HexColor("#374151")
TABLE_HDR  = colors.HexColor("#1e2a4a")
TABLE_ALT  = colors.HexColor("#f8fafc")
WHITE      = colors.white
BLACK      = colors.HexColor("#111827")

W, H = A4   # 595 x 842 pt

# ── Page numbering callback ────────────────────────────────────────────────────
def _header_footer(canv: canvas.Canvas, doc):
    canv.saveState()
    # Header bar
    canv.setFillColor(DARK_BG)
    canv.rect(0, H - 30, W, 30, fill=1, stroke=0)
    canv.setFillColor(ACCENT)
    canv.rect(0, H - 32, W, 2, fill=1, stroke=0)
    canv.setFont("Helvetica-Bold", 8)
    canv.setFillColor(WHITE)
    canv.drawString(2*cm, H - 20, "Currency Trader Pro")
    canv.setFont("Helvetica", 8)
    canv.setFillColor(MID_GREY)
    canv.drawRightString(W - 2*cm, H - 20, "User Guide v1.0")

    # Footer
    canv.setFillColor(LIGHT_GREY)
    canv.rect(0, 0, W, 22, fill=1, stroke=0)
    canv.setFillColor(ACCENT)
    canv.rect(0, 22, W, 1, fill=1, stroke=0)
    canv.setFont("Helvetica", 7.5)
    canv.setFillColor(DARK_GREY)
    canv.drawString(2*cm, 7, "Currency Trader Pro — For educational / paper-trading use only")
    canv.drawRightString(W - 2*cm, 7, f"Page {doc.page}")
    canv.restoreState()


def _cover_page(canv: canvas.Canvas, doc):
    canv.saveState()
    # Dark gradient background
    canv.setFillColor(DARK_BG)
    canv.rect(0, 0, W, H, fill=1, stroke=0)
    # Blue accent bar top
    canv.setFillColor(ACCENT)
    canv.rect(0, H - 6, W, 6, fill=1, stroke=0)
    # Gold accent bar bottom
    canv.setFillColor(GOLD)
    canv.rect(0, 0, W, 6, fill=1, stroke=0)
    # Decorative stripe
    canv.setFillColor(colors.HexColor("#1e2a4a"))
    canv.rect(0, H*0.38, W, H*0.28, fill=1, stroke=0)
    # Chart icon (simple bar chart shapes)
    bx, by = W/2 - 60, H*0.60
    bar_data = [(10, 55), (20, 80), (30, 45), (40, 95), (50, 70), (60, 110), (70, 85), (80, 120)]
    for x_off, bar_h in bar_data:
        canv.setFillColor(ACCENT)
        canv.rect(bx + x_off, by, 8, bar_h * 0.6, fill=1, stroke=0)
    # Trend line overlay
    canv.setStrokeColor(GREEN)
    canv.setLineWidth(2.5)
    pts = [(bx + x + 4, by + h * 0.6) for x, h in bar_data]
    canv.lines([(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1]) for i in range(len(pts)-1)])
    # Title
    canv.setFillColor(WHITE)
    canv.setFont("Helvetica-Bold", 36)
    canv.drawCentredString(W/2, H*0.50, "Currency Trader Pro")
    canv.setFont("Helvetica", 18)
    canv.setFillColor(GOLD)
    canv.drawCentredString(W/2, H*0.44, "User Guide & Reference Manual")
    # Version / date
    canv.setFont("Helvetica", 10)
    canv.setFillColor(MID_GREY)
    canv.drawCentredString(W/2, H*0.39, "Version 1.0  •  2026")
    # Tagline
    canv.setFillColor(colors.HexColor("#60a5fa"))
    canv.setFont("Helvetica-Oblique", 12)
    canv.drawCentredString(W/2, H*0.33, "Real-Time Prices · Automated Strategies · Full Portfolio Analytics")
    # Disclaimer
    canv.setFont("Helvetica", 8)
    canv.setFillColor(MID_GREY)
    canv.drawCentredString(W/2, 40, "Paper Trading Mode · No Real Money Involved · Educational Use Only")
    canv.restoreState()


# ── Style helpers ─────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def S(name, **kw):
    return ParagraphStyle(name, **kw)

H1 = S("H1", fontSize=18, fontName="Helvetica-Bold", textColor=ACCENT,
        spaceAfter=8, spaceBefore=18, leading=22)
H2 = S("H2", fontSize=13, fontName="Helvetica-Bold", textColor=BLACK,
        spaceAfter=5, spaceBefore=12, leading=17,
        borderPad=(0,0,4,0))
H3 = S("H3", fontSize=11, fontName="Helvetica-Bold", textColor=DARK_GREY,
        spaceAfter=3, spaceBefore=8, leading=15)
BODY = S("Body", fontSize=9.5, fontName="Helvetica", textColor=BLACK,
         spaceAfter=5, spaceBefore=2, leading=14, alignment=TA_JUSTIFY)
BULLET = S("Bullet", fontSize=9.5, fontName="Helvetica", textColor=BLACK,
           spaceAfter=3, spaceBefore=1, leading=14,
           leftIndent=16, bulletIndent=4)
CODE = S("Code", fontSize=8.5, fontName="Courier", textColor=colors.HexColor("#1d4ed8"),
         backColor=colors.HexColor("#eff6ff"), borderPad=4,
         spaceAfter=6, spaceBefore=4, leading=13)
NOTE = S("Note", fontSize=9, fontName="Helvetica-Oblique", textColor=DARK_GREY,
         backColor=colors.HexColor("#fefce8"), borderPad=6,
         spaceAfter=6, spaceBefore=4, leading=13, leftIndent=8)
WARN = S("Warn", fontSize=9, fontName="Helvetica-Oblique", textColor=colors.HexColor("#92400e"),
         backColor=colors.HexColor("#fff7ed"), borderPad=6,
         spaceAfter=6, spaceBefore=4, leading=13, leftIndent=8)
CAPTION = S("Caption", fontSize=8, fontName="Helvetica-Oblique", textColor=MID_GREY,
            alignment=TA_CENTER, spaceAfter=6)

def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BODY)
def b(t):  return Paragraph(f"• {t}", BULLET)
def code(t): return Paragraph(t, CODE)
def note(t): return Paragraph(f"<b>Note:</b> {t}", NOTE)
def warn(t): return Paragraph(f"<b>⚠ Warning:</b> {t}", WARN)
def sp(h=6): return Spacer(1, h)
def hr():  return HRFlowable(width="100%", thickness=0.5, color=LIGHT_GREY, spaceAfter=6, spaceBefore=6)

def tbl(data, col_widths, header_row=True):
    t = Table(data, colWidths=col_widths, repeatRows=1 if header_row else 0)
    style = [
        ("BACKGROUND", (0,0), (-1,0), TABLE_HDR),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, TABLE_ALT]),
        ("GRID",       (0,0), (-1,-1), 0.4, LIGHT_GREY),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]
    t.setStyle(TableStyle(style))
    return t

def info_box(text, color=ACCENT):
    data = [[Paragraph(text, S("ib", fontSize=9, fontName="Helvetica",
                               textColor=BLACK, leading=13))]]
    t = Table(data, colWidths=[W - 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ("LEFTPADDING",  (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LINEBEFORE",   (0,0), (0,-1), 4, color),
        ("LINEBELOW",    (0,0), (-1,-1), 0.3, LIGHT_GREY),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# CONTENT
# ══════════════════════════════════════════════════════════════════════════════
def build_content():
    story = []

    # ── 1. Introduction ───────────────────────────────────────────────────────
    story += [
        h1("1. Introduction"),
        p("Currency Trader Pro is a full-stack, self-contained trading platform designed for "
          "paper trading, strategy research, and financial education. It provides live market "
          "data, an intelligent order engine, four automated algorithmic strategies, and a "
          "professional dark-themed UI — all in a single executable file."),
        sp(),
        info_box("Currency Trader Pro operates exclusively in <b>Paper Trading Mode</b>. "
                 "All trades use a virtual $10,000 starting balance. No real exchange accounts "
                 "are connected and no real money is ever at risk.", GOLD),
        sp(8),
        h2("1.1  Key Capabilities"),
        tbl([
            ["Capability", "Detail"],
            ["Live Crypto Prices", "Binance WebSocket — BTC, ETH, SOL, BNB, ADA, DOGE, XRP, AVAX"],
            ["Forex Prices", "Simulated realistic prices — EUR/USD, GBP/USD, USD/JPY + 4 more"],
            ["Order Types", "Market, Limit, Stop — with optional Take-Profit & Stop-Loss"],
            ["Auto Trading", "4 built-in strategies run every 30 seconds automatically"],
            ["Portfolio Analytics", "Real-time P&L, allocation chart, 30-day daily P&L history"],
            ["Trade History", "Full audit trail with per-trade fee and realised P&L"],
            ["Executable", "Single binary — no installation, no database server required"],
        ], [5.5*cm, 11*cm]),
        sp(12),

        h2("1.2  System Requirements"),
        tbl([
            ["Component", "Minimum", "Recommended"],
            ["Operating System", "Windows 10 / Debian 11", "Windows 11 / Debian 12"],
            ["CPU",              "Dual-core 2 GHz",        "Quad-core 3 GHz"],
            ["RAM",              "2 GB",                   "4 GB"],
            ["Disk Space",       "150 MB",                 "500 MB"],
            ["Network",          "Required (market data)", "Broadband"],
            ["Browser",          "Chrome / Firefox / Edge","Chrome 120+"],
        ], [4.5*cm, 5.5*cm, 6*cm]),
        sp(8),
        note("An internet connection is required to receive live cryptocurrency prices from Binance. "
             "Forex prices are generated locally and work offline."),
    ]

    story.append(PageBreak())

    # ── 2. Installation ───────────────────────────────────────────────────────
    story += [
        h1("2. Installation & First Launch"),
        h2("2.1  Using the Pre-Built Executable"),
        p("The simplest way to run Currency Trader Pro is using the pre-built binary. "
          "No Python or Node.js installation is required."),
        sp(6),

        h3("Linux / Debian"),
        code("# 1. Download or copy currency_trader to your machine\n"
             "# 2. Make it executable\n"
             "chmod +x currency_trader\n\n"
             "# 3. Run it\n"
             "./currency_trader"),
        p("The application will start a local web server on port <b>8765</b> and "
          "automatically open your default browser. If the browser does not open, "
          "navigate manually to: <b>http://localhost:8765</b>"),
        sp(6),

        h3("Windows"),
        code("# Double-click currency_trader.exe\n"
             "# OR run from Command Prompt:\n"
             "currency_trader.exe"),
        p("Windows Defender SmartScreen may show a warning on first run because the "
          "binary is not code-signed. Click <b>More info → Run anyway</b> to proceed."),
        sp(8),

        h2("2.2  Building from Source"),
        p("If you have Python 3.10+ and Node.js 18+ installed, you can build the "
          "executable yourself from the source code."),
        sp(4),

        h3("Linux / macOS"),
        code("cd currency_trader\n"
             "chmod +x build.sh\n"
             "./build.sh\n\n"
             "# Output: dist/currency_trader"),
        sp(4),

        h3("Windows"),
        code("cd currency_trader\n"
             "build.bat\n\n"
             "# Output: dist\\currency_trader.exe"),
        sp(4),

        p("The build script automatically:"),
        b("Creates a Python virtual environment and installs all backend dependencies"),
        b("Installs Node.js packages and compiles the React frontend"),
        b("Bundles everything into a single self-contained executable via PyInstaller"),
        sp(8),

        h2("2.3  Development Mode"),
        p("For development with hot reload on both frontend and backend:"),
        code("cd currency_trader\n"
             "./run_dev.sh\n\n"
             "# Backend  → http://localhost:8765   (FastAPI)\n"
             "# Frontend → http://localhost:5173   (Vite dev server)"),
        warn("Development mode requires Python 3.10+ with virtual environment support "
             "and Node.js 18+. The run_dev.sh script installs all dependencies automatically."),
    ]

    story.append(PageBreak())

    # ── 3. Interface Overview ─────────────────────────────────────────────────
    story += [
        h1("3. Interface Overview"),
        p("The interface is divided into four main zones:"),
        sp(4),

        tbl([
            ["Zone", "Description"],
            ["Ticker Bar (top)",    "Live scrolling price feed for all 15 symbols with 24h change"],
            ["Sidebar (left)",      "Navigation menu, mini portfolio summary, and connection status"],
            ["Main Content Area",   "The active page — changes based on the sidebar selection"],
            ["Status Bar (bottom)", "Page number and paper trading mode indicator"],
        ], [4.5*cm, 12*cm]),
        sp(10),

        h2("3.1  Navigation Pages"),
        tbl([
            ["Page", "Icon", "Purpose"],
            ["Dashboard",    "📊", "Overview — chart, portfolio stats, top movers, P&L history"],
            ["Trade",        "📈", "Place buy/sell orders, view and cancel open orders"],
            ["Portfolio",    "💼", "Positions, asset allocation, performance statistics"],
            ["Auto Trading", "🤖", "Create and manage automated algorithmic strategies"],
            ["History",      "📋", "Full trade history, open orders, win rate"],
            ["Settings",     "⚙",  "App configuration, data sources, portfolio reset"],
        ], [3.5*cm, 1.5*cm, 11.5*cm]),
        sp(8),

        h2("3.2  Live Ticker"),
        p("The scrolling banner at the top of every page shows all 15 supported symbols. "
          "Each entry displays the current price and 24-hour percentage change. "
          "Green values indicate a price increase; red indicates a decrease. "
          "Hover over the ticker to pause scrolling."),
        sp(8),

        h2("3.3  Portfolio Summary (Sidebar)"),
        p("The sidebar always shows your current total portfolio value and overall P&L "
          "so you can monitor performance at a glance without leaving the current page."),
        sp(4),
        info_box("The <b>Live Feed</b> indicator at the bottom of the sidebar shows the "
                 "WebSocket connection status. When connected, prices update every second in real time."),
    ]

    story.append(PageBreak())

    # ── 4. Dashboard ──────────────────────────────────────────────────────────
    story += [
        h1("4. Dashboard"),
        p("The Dashboard is the default landing page and provides a high-level view of "
          "your account and the market."),
        sp(6),

        h2("4.1  Statistics Cards"),
        tbl([
            ["Card", "Description"],
            ["Portfolio Value", "Total account value (cash + open position market value)"],
            ["Cash Balance",    "USD available for new trades"],
            ["Holdings Value",  "Current market value of all open positions"],
            ["Selected Symbol", "Live price and 24h change for the active chart symbol"],
        ], [4.5*cm, 12*cm]),
        sp(8),

        h2("4.2  Candlestick Chart"),
        p("The main chart area displays a <b>1-minute OHLCV candlestick chart</b> powered by "
          "TradingView's Lightweight Charts library. Features include:"),
        b("Pan and zoom with mouse scroll or trackpad pinch"),
        b("Crosshair with exact OHLC values on hover"),
        b("Volume histogram in the lower portion of the chart"),
        b("Green candles = bullish (close ≥ open)  |  Red candles = bearish (close < open)"),
        b("Live tick updates — the latest bar updates in real time as new prices arrive"),
        sp(6),
        p("Use the <b>symbol dropdown</b> above the chart to switch between any of the 15 "
          "available symbols. The chart automatically reloads with up to 200 historical bars."),
        sp(8),

        h2("4.3  Top Movers"),
        p("The right panel lists the 6 symbols with the largest absolute 24-hour price "
          "movement. Click any symbol to instantly switch the chart to that symbol."),
        sp(8),

        h2("4.4  Daily P&L Sparkline"),
        p("An area chart shows your realised P&L aggregated by calendar day for the past "
          "14 days. This helps identify performance trends and trading patterns over time."),
        sp(8),

        h2("4.5  Open Positions"),
        p("If you have any open positions they appear in a compact list in the sidebar area "
          "of the dashboard showing symbol, quantity, current value, and unrealised P&L."),
    ]

    story.append(PageBreak())

    # ── 5. Trading ────────────────────────────────────────────────────────────
    story += [
        h1("5. Trading"),
        p("The Trade page allows you to place orders manually. The chart and order form "
          "are displayed side-by-side for efficient decision-making."),
        sp(6),

        h2("5.1  Order Types"),
        tbl([
            ["Type", "Behaviour"],
            ["Market", "Executes immediately at the current live price. "
                       "No price field required."],
            ["Limit",  "Placed in the order book and fills only when the market price "
                       "reaches your specified limit price. Buy fills when price ≤ limit; "
                       "Sell fills when price ≥ limit."],
            ["Stop",   "Triggers when the market reaches the stop price, then executes at "
                       "market. Useful for stop-loss protection on existing positions."],
        ], [2.5*cm, 14*cm]),
        sp(8),

        h2("5.2  Placing an Order"),
        p("Follow these steps to place a trade:"),
        sp(4),
        tbl([
            ["Step", "Action"],
            ["1", "Select a symbol from the dropdown above the chart, or navigate to the "
                  "Dashboard and click a symbol in Top Movers."],
            ["2", "Choose <b>Buy</b> or <b>Sell</b> using the tab buttons (green/red)."],
            ["3", "Select the Order Type (Market, Limit, or Stop)."],
            ["4", "If using Limit or Stop, enter the trigger price in the price field."],
            ["5", "Enter the quantity. Use the slider + <b>calc</b> button to auto-fill "
                  "a percentage of your available USD balance."],
            ["6", "Optionally set Take-Profit and/or Stop-Loss prices."],
            ["7", "Click the Buy/Sell button. A confirmation message appears below the form."],
        ], [1*cm, 15.5*cm]),
        sp(8),

        h2("5.3  Quantity Calculator"),
        p("The slider above the Quantity field lets you specify what percentage of your "
          "available USD balance to use for the trade. After adjusting the slider, "
          "click <b>calc</b> to fill the Quantity field automatically based on the current price."),
        sp(4),
        note("The estimated trade value is shown in small grey text below the quantity field "
             "as you type, giving you an immediate cost preview before submitting."),
        sp(8),

        h2("5.4  Take-Profit & Stop-Loss"),
        p("When provided, Take-Profit and Stop-Loss prices are stored with your position. "
          "The trading engine monitors these levels continuously:"),
        b("<b>Take-Profit:</b> When the market price reaches or exceeds this level, "
          "the system automatically places a market SELL order to lock in profit."),
        b("<b>Stop-Loss:</b> When the market price falls to or below this level, "
          "the system places a market SELL order to limit your loss."),
        sp(4),
        note("TP/SL are stored as reference prices and checked every 0.5 seconds against "
             "the live price. For SELL orders, the logic is reversed (SL above entry)."),
        sp(8),

        h2("5.5  Managing Open Orders"),
        p("Open (unfilled) Limit and Stop orders appear in a list below the order form. "
          "Click the <b>✕</b> button next to any order to cancel it immediately. "
          "Market orders are always filled instantly and never appear in the open orders list."),
        sp(8),

        h2("5.6  Fees"),
        p("A flat <b>0.1% taker fee</b> is applied to every executed order. "
          "Fees are deducted from your USD balance on buys and from the proceeds on sells. "
          "The fee is shown separately in Trade History so you can track total costs."),
    ]

    story.append(PageBreak())

    # ── 6. Portfolio ──────────────────────────────────────────────────────────
    story += [
        h1("6. Portfolio"),
        p("The Portfolio page provides a detailed breakdown of your account, open positions, "
          "and performance metrics."),
        sp(6),

        h2("6.1  Summary Cards"),
        tbl([
            ["Card", "Formula"],
            ["Total Value",   "Cash Balance + Holdings Value (at current market prices)"],
            ["Cash Balance",  "USD available — decremented on buys, incremented on sells"],
            ["Total P&L",     "Total Value − Initial Balance ($10,000)"],
            ["Return %",      "(Total Value / 10,000 − 1) × 100"],
        ], [3.5*cm, 13*cm]),
        sp(8),

        h2("6.2  Asset Allocation Chart"),
        p("A pie chart shows the proportional allocation of your portfolio across cash "
          "and each open position (by current market value). This gives an instant view "
          "of concentration risk. Mouse over any segment to see the exact USD value."),
        sp(8),

        h2("6.3  Daily P&L Bar Chart"),
        p("A bar chart of realised P&L grouped by calendar day over the last 30 days. "
          "Green bars indicate profitable days; red bars indicate losing days. "
          "Only closed (SELL) trades contribute to realised P&L."),
        sp(8),

        h2("6.4  Performance Statistics"),
        tbl([
            ["Metric", "Description"],
            ["Total Trades", "Count of all executed trades (both buys and sells)"],
            ["Win Rate",     "Percentage of SELL trades with positive P&L"],
            ["Avg Win",      "Average P&L of winning trades (P&L > 0)"],
            ["Avg Loss",     "Average P&L of losing trades (P&L < 0), shown as positive"],
            ["Total Fees",   "Sum of all fees paid across all trades"],
        ], [3.5*cm, 13*cm]),
        sp(8),

        h2("6.5  Open Positions Table"),
        tbl([
            ["Column", "Description"],
            ["Symbol",        "Trading pair (e.g. BTC/USDT)"],
            ["Qty",           "Number of units held"],
            ["Avg Entry",     "Volume-weighted average purchase price"],
            ["Current",       "Latest live market price"],
            ["Value",         "Qty × Current Price"],
            ["Unrealised P&L","(Current − Avg Entry) × Qty − fees accrued"],
            ["%",             "Unrealised P&L as percentage of entry cost"],
        ], [3*cm, 13.5*cm]),
        sp(4),
        note("Unrealised P&L updates every 5 seconds. The portfolio total refreshes "
             "automatically via WebSocket — no manual refresh needed."),
    ]

    story.append(PageBreak())

    # ── 7. Auto Trading ───────────────────────────────────────────────────────
    story += [
        h1("7. Auto Trading"),
        p("The Auto Trading page lets you configure algorithmic strategies that trade "
          "automatically on your behalf using your paper balance. Strategies run "
          "every <b>30 seconds</b> when active."),
        sp(6),

        info_box("All automated strategies use <b>paper balance only</b>. They follow the "
                 "same fee rules and portfolio limits as manual trades. No external exchange "
                 "APIs are called."),
        sp(8),

        h2("7.1  Available Strategies"),
        tbl([
            ["Strategy", "Type", "Buy Signal", "Sell Signal"],
            ["SMA Crossover", "Trend-Following",
             "Fast SMA crosses above Slow SMA", "Fast SMA crosses below Slow SMA"],
            ["RSI", "Mean-Reversion",
             "RSI falls below oversold threshold (default: 30)",
             "RSI rises above overbought threshold (default: 70)"],
            ["MACD", "Momentum",
             "MACD line crosses above Signal line",
             "MACD line crosses below Signal line"],
            ["Bollinger Bands", "Mean-Reversion",
             "Price touches or breaks below lower band",
             "Price touches or exceeds upper band"],
        ], [3.5*cm, 3.5*cm, 5*cm, 4.5*cm]),
        sp(8),

        h2("7.2  Strategy Parameters"),

        h3("SMA Crossover"),
        tbl([
            ["Parameter",    "Default", "Description"],
            ["fast_period",  "10",      "Number of bars for the fast (short-term) moving average"],
            ["slow_period",  "30",      "Number of bars for the slow (long-term) moving average"],
        ], [3.5*cm, 2*cm, 11*cm]),
        sp(6),

        h3("RSI"),
        tbl([
            ["Parameter",  "Default", "Description"],
            ["period",     "14",      "Number of bars used to calculate RSI"],
            ["oversold",   "30",      "RSI level that triggers a BUY signal"],
            ["overbought", "70",      "RSI level that triggers a SELL signal"],
        ], [3.5*cm, 2*cm, 11*cm]),
        sp(6),

        h3("MACD"),
        tbl([
            ["Parameter", "Default", "Description"],
            ["fast",      "12",      "Fast EMA period"],
            ["slow",      "26",      "Slow EMA period"],
            ["signal",    "9",       "Signal line EMA period"],
        ], [3.5*cm, 2*cm, 11*cm]),
        sp(6),

        h3("Bollinger Bands"),
        tbl([
            ["Parameter", "Default", "Description"],
            ["period",    "20",      "Look-back period for the moving average and std deviation"],
            ["std_mult",  "2.0",     "Number of standard deviations for the band width"],
        ], [3.5*cm, 2*cm, 11*cm]),
        sp(8),

        h2("7.3  Risk Management Settings"),
        tbl([
            ["Setting",              "Default", "Description"],
            ["Position Size %",      "10%",     "Percentage of current USD balance used per entry"],
            ["Stop Loss %",          "2%",      "Auto stop-loss placed at entry_price × (1 − SL%)"],
            ["Take Profit %",        "4%",      "Auto take-profit placed at entry_price × (1 + TP%)"],
            ["Max Positions",        "1",       "Max concurrent open positions for this strategy"],
        ], [4.5*cm, 2*cm, 10*cm]),
        sp(8),

        h2("7.4  Creating a Strategy"),
        tbl([
            ["Step", "Action"],
            ["1", "Click <b>New Strategy</b> in the top-right corner of the Auto Trading page."],
            ["2", "Enter a descriptive name (e.g. 'BTC RSI 14')."],
            ["3", "Choose a Strategy Type from the dropdown. A description appears below."],
            ["4", "Select the Symbol to trade (e.g. BTC/USDT)."],
            ["5", "Adjust Position Size, Stop Loss, and Take Profit percentages."],
            ["6", "Review and optionally edit the strategy-specific parameters."],
            ["7", "Click <b>Create</b>. The strategy is saved but not yet active."],
            ["8", "Click <b>Start</b> on the strategy card to activate it."],
        ], [1*cm, 15.5*cm]),
        sp(8),

        h2("7.5  Strategy Logs"),
        p("Each strategy card has a <b>Logs</b> button that expands a scrollable log panel "
          "showing the last 20 actions. Log entries include:"),
        b("Buy/Sell decisions with price, quantity, and the signal that triggered them"),
        b("Errors (shown in red) if an order failed to execute"),
        b("Timestamps in UTC for all events"),
        sp(4),
        note("If a strategy is active but showing no log entries, it means the signal "
             "conditions have not yet been met. Check back after a few minutes."),
    ]

    story.append(PageBreak())

    # ── 8. Trade History ──────────────────────────────────────────────────────
    story += [
        h1("8. Trade History"),
        p("The History page shows a comprehensive record of all trades and orders."),
        sp(6),

        h2("8.1  Summary Metrics"),
        tbl([
            ["Metric",        "Description"],
            ["Total Trades",  "All executed trades (buys + sells)"],
            ["Realised P&L",  "Sum of P&L on all SELL trades"],
            ["Win Rate",      "% of SELL trades with positive P&L"],
            ["Open Orders",   "Count of limit/stop orders currently waiting to fill"],
        ], [4*cm, 12.5*cm]),
        sp(8),

        h2("8.2  Open Orders Panel"),
        p("All pending Limit and Stop orders are listed with full details: symbol, side, "
          "type, quantity, trigger price, TP, SL, and creation time. "
          "Click <b>Cancel</b> to remove an order without executing it."),
        sp(8),

        h2("8.3  Executed Trade Log"),
        tbl([
            ["Column",       "Description"],
            ["#",            "Unique trade ID"],
            ["Symbol",       "Trading pair"],
            ["Side",         "BUY (green) or SELL (red)"],
            ["Qty",          "Number of units traded"],
            ["Price",        "Execution price"],
            ["Value",        "Qty × Price (gross trade value)"],
            ["Fee",          "0.1% taker fee charged for this trade"],
            ["P&L",          "Realised profit/loss (SELL trades only; BUY shows —)"],
            ["Strategy",     "Name of the automated strategy that triggered the trade, or — for manual trades"],
            ["Time",         "Execution timestamp (UTC)"],
        ], [3*cm, 13.5*cm]),
        sp(4),
        note("The most recent 100 trades are displayed. All trades are permanently stored "
             "in the SQLite database file (~/.currency_trader/currency_trader.db)."),
    ]

    story.append(PageBreak())

    # ── 9. Settings ───────────────────────────────────────────────────────────
    story += [
        h1("9. Settings"),
        h2("9.1  Trading Configuration"),
        tbl([
            ["Setting",           "Value", "Notes"],
            ["Fee Rate",          "0.1%",  "Fixed taker fee applied to all executed orders"],
            ["Strategy Interval", "30 s",  "Frequency of automated strategy evaluation"],
            ["Price Update",      "1 s",   "WebSocket push interval for live prices"],
        ], [5*cm, 2.5*cm, 9*cm]),
        sp(8),

        h2("9.2  Data Sources"),
        tbl([
            ["Source",             "Type",      "Symbols"],
            ["Binance WebSocket",  "Live",      "BTC/USDT ETH/USDT SOL/USDT BNB/USDT ADA/USDT DOGE/USDT XRP/USDT AVAX/USDT"],
            ["Forex Simulation",   "Simulated", "EUR/USD GBP/USD USD/JPY AUD/USD USD/CAD USD/CHF NZD/USD"],
        ], [4*cm, 2.5*cm, 10*cm]),
        sp(6),
        info_box("Forex prices use a <b>mean-reverting random walk</b> model seeded with "
                 "realistic exchange rates. The drift pulls prices back toward the seed value, "
                 "creating natural-looking fluctuations with 0.02% volatility per second.", GOLD),
        sp(8),

        h2("9.3  Resetting the Paper Portfolio"),
        p("The <b>Reset Paper Portfolio</b> button in the Danger Zone clears all trade "
          "history, positions, and orders, returning your balance to the default $10,000. "
          "A confirmation dialog is shown before any data is removed. After resetting, "
          "restart the application to apply the changes fully."),
        warn("This action is irreversible. All trade history, P&L records, and open "
             "positions will be permanently deleted from the database."),
    ]

    story.append(PageBreak())

    # ── 10. Technical Reference ───────────────────────────────────────────────
    story += [
        h1("10. Technical Reference"),
        h2("10.1  Architecture"),
        tbl([
            ["Layer",       "Technology",          "Role"],
            ["Backend",     "Python 3.11 + FastAPI","REST API, WebSocket server, trading engine"],
            ["Database",    "SQLite + aiosqlite",   "Persistent storage for trades, portfolio, strategies"],
            ["Market Data", "Binance WebSocket",    "Live crypto price stream (no API key required)"],
            ["Frontend",    "React 18 + TypeScript","Single-page trading terminal UI"],
            ["Styling",     "Tailwind CSS",         "Utility-first dark-theme styling"],
            ["Charts",      "TradingView LW Charts","Candlestick, area, and histogram charts"],
            ["State",       "Zustand",              "Lightweight global state management"],
            ["Build",       "PyInstaller + Vite",   "Single-file executable bundling"],
        ], [3*cm, 4.5*cm, 9*cm]),
        sp(8),

        h2("10.2  API Endpoints"),
        tbl([
            ["Method", "Path",                      "Description"],
            ["GET",    "/api/market/prices",         "All current prices"],
            ["GET",    "/api/market/history/{sym}",  "OHLCV history (up to 200 bars)"],
            ["GET",    "/api/market/symbols",        "List of all supported symbols"],
            ["GET",    "/api/portfolio/summary",     "Portfolio value, positions, P&L"],
            ["GET",    "/api/portfolio/performance", "Daily P&L, win rate, stats"],
            ["POST",   "/api/trades/order",          "Place a new order"],
            ["DELETE", "/api/trades/order/{id}",     "Cancel an open order"],
            ["GET",    "/api/trades/orders",         "List orders (filter by status)"],
            ["GET",    "/api/trades/history",        "Executed trade history"],
            ["GET",    "/api/strategy/",             "List all strategies"],
            ["POST",   "/api/strategy/",             "Create a new strategy"],
            ["PATCH",  "/api/strategy/{id}",         "Update strategy (activate/deactivate/params)"],
            ["DELETE", "/api/strategy/{id}",         "Delete a strategy"],
            ["GET",    "/api/strategy/{id}/logs",    "Strategy execution logs"],
            ["WS",     "/ws",                        "WebSocket — live price + portfolio push every 1 s"],
        ], [1.5*cm, 5.5*cm, 9.5*cm]),
        sp(8),

        h2("10.3  Database Schema"),
        tbl([
            ["Table",          "Key Columns"],
            ["portfolio",      "usd_balance, total_value, total_pnl, total_pnl_pct"],
            ["positions",      "symbol, quantity, avg_entry_price, current_price, unrealized_pnl"],
            ["orders",         "symbol, side, order_type, quantity, price, stop_price, take_profit, stop_loss, status"],
            ["trades",         "symbol, side, quantity, price, value, fee, pnl, strategy, executed_at"],
            ["strategies",     "name, strategy_type, symbol, is_active, params(JSON), position_size_pct, stop_loss_pct, take_profit_pct"],
            ["strategy_logs",  "strategy_id, message, level, created_at"],
        ], [3.5*cm, 13*cm]),
        sp(4),
        p("The database file is located at:"),
        b("<b>Linux / macOS:</b>  ~/.currency_trader/currency_trader.db"),
        b("<b>Windows:</b>  C:\\Users\\&lt;username&gt;\\.currency_trader\\currency_trader.db"),
        sp(8),

        h2("10.4  Port Configuration"),
        p("The application binds to <b>port 8765</b> by default. "
          "If this port is in use, you can modify the port in "
          "<code>backend/app/main.py</code> in the <code>run()</code> function "
          "and rebuild the executable."),
        sp(8),

        h2("10.5  File Structure"),
        code("currency_trader/\n"
             "├── backend/\n"
             "│   ├── app/\n"
             "│   │   ├── main.py          # FastAPI app + WebSocket\n"
             "│   │   ├── database.py      # SQLite async setup\n"
             "│   │   ├── models.py        # ORM models\n"
             "│   │   ├── market_data.py   # Binance + forex prices\n"
             "│   │   ├── trading_engine.py# Order execution + P&L\n"
             "│   │   ├── strategies.py    # SMA / RSI / MACD / BB\n"
             "│   │   └── routers/         # REST endpoints\n"
             "│   └── requirements.txt\n"
             "├── frontend/\n"
             "│   └── src/\n"
             "│       ├── components/      # React UI components\n"
             "│       ├── store/           # Zustand state\n"
             "│       └── hooks/           # WebSocket hook\n"
             "├── static/                  # Built React app\n"
             "├── build.sh / build.bat     # Build scripts\n"
             "├── run_dev.sh               # Dev launcher\n"
             "└── currency_trader.spec     # PyInstaller spec"),
    ]

    story.append(PageBreak())

    # ── 11. Troubleshooting ───────────────────────────────────────────────────
    story += [
        h1("11. Troubleshooting"),
        tbl([
            ["Problem", "Likely Cause", "Solution"],
            ["Browser does not open",
             "Port 8765 in use or firewall",
             "Open http://localhost:8765 manually. Check if another process uses port 8765."],
            ["Ticker shows '—' or no prices",
             "WebSocket not yet connected",
             "Wait 2–3 seconds for the connection to establish. Check internet access."],
            ["Crypto prices not updating",
             "Binance WebSocket blocked",
             "Check firewall / proxy settings. Forex prices work offline."],
            ["'Insufficient balance' error",
             "Not enough USD for the trade",
             "Reduce quantity or use the % slider to stay within your balance."],
            ["Strategy not placing trades",
             "Signal conditions not met yet",
             "Strategies need sufficient price history (30–50 bars). Wait a few minutes "
             "or check the strategy logs."],
            ["Blank white screen",
             "Frontend not built",
             "Run build.sh (Linux) or build.bat (Windows) to compile the frontend."],
            ["Windows SmartScreen warning",
             "Binary not code-signed",
             "Click 'More info' → 'Run anyway'. This is expected for self-built binaries."],
            ["Database locked error",
             "Multiple instances running",
             "Close all instances of currency_trader and relaunch once."],
        ], [4*cm, 4*cm, 8.5*cm]),
    ]

    story.append(PageBreak())

    # ── 12. Glossary ─────────────────────────────────────────────────────────
    story += [
        h1("12. Glossary"),
        tbl([
            ["Term",             "Definition"],
            ["OHLCV",           "Open, High, Low, Close, Volume — the five values that define a price bar"],
            ["Candlestick",     "Visual price bar showing Open, High, Low, Close for a time period"],
            ["Market Order",    "An order that executes immediately at the best available price"],
            ["Limit Order",     "An order that waits until the market price reaches a specified level"],
            ["Stop Order",      "An order that triggers a market execution when price crosses a stop level"],
            ["Take-Profit (TP)","A price at which an open position is automatically closed for a gain"],
            ["Stop-Loss (SL)",  "A price at which an open position is automatically closed to cap a loss"],
            ["P&L",             "Profit and Loss — the gain or loss from trading activity"],
            ["Unrealised P&L",  "P&L on open positions, calculated at the current market price"],
            ["Realised P&L",    "P&L locked in after closing (selling) a position"],
            ["Position Size",   "The amount of capital allocated to a single trade"],
            ["Win Rate",        "Percentage of closed trades that generated a profit"],
            ["SMA",             "Simple Moving Average — arithmetic mean of closing prices over N bars"],
            ["EMA",             "Exponential Moving Average — weighted average giving more weight to recent bars"],
            ["RSI",             "Relative Strength Index (0–100) — measures momentum and overbought/oversold levels"],
            ["MACD",            "Moving Average Convergence Divergence — trend-following momentum indicator"],
            ["Bollinger Bands", "Price channel based on standard deviation around a moving average"],
            ["Paper Trading",   "Simulated trading with virtual money — no real financial risk"],
            ["Taker Fee",       "Fee paid for orders that consume existing liquidity (market orders)"],
            ["WebSocket",       "Full-duplex network protocol enabling real-time server-to-client data push"],
        ], [4.5*cm, 12*cm]),
    ]

    story.append(PageBreak())

    # ── 13. Legal ─────────────────────────────────────────────────────────────
    story += [
        h1("13. Legal & Disclaimer"),
        sp(4),
        warn("Currency Trader Pro is provided for <b>educational and research purposes only</b>. "
             "It is not financial advice. Past simulated performance does not guarantee future "
             "real-world results."),
        sp(8),
        p("Currency Trader Pro does not:"),
        b("Connect to any real exchange account"),
        b("Execute trades with real money"),
        b("Hold, transmit, or request any financial credentials"),
        b("Provide regulated financial advice"),
        sp(8),
        p("Cryptocurrency and forex markets are highly volatile. Real trading involves "
          "substantial risk of loss. Always consult a licensed financial advisor before "
          "committing real capital to any trading strategy."),
        sp(8),
        p("Market data is sourced from Binance's publicly available WebSocket API. "
          "The authors are not affiliated with Binance or any other exchange. "
          "Forex prices are simulated and do not represent real market conditions."),
        sp(8),
        hr(),
        Paragraph(
            "Currency Trader Pro v1.0 · 2026 · Open Source · Educational Use Only",
            S("footer_txt", fontSize=8, fontName="Helvetica-Oblique",
              textColor=MID_GREY, alignment=TA_CENTER)
        ),
    ]

    return story


# ══════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ══════════════════════════════════════════════════════════════════════════════
OUTPUT = "/home/user/Project1/currency_trader/Currency_Trader_Pro_User_Guide.pdf"

class CoverDoc(BaseDocTemplate):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.is_cover = True

    def handle_pageBegin(self):
        super().handle_pageBegin()

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=1.8*cm,
    title="Currency Trader Pro — User Guide",
    author="Currency Trader Pro",
    subject="Full-Stack Trading Platform",
)

# We need to inject a cover page manually
from reportlab.platypus import Flowable

def _first_page(canv, doc):
    _cover_page(canv, doc)

content = build_content()

doc.build(
    content,
    onFirstPage=_first_page,
    onLaterPages=_header_footer,
)

print(f"PDF created: {OUTPUT}")
