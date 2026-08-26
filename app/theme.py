"""Arayüzün görsel teması: palet, CSS ve grafik stili."""

# Koyu zemin, sari aksan. Grafik renkleri de buradan geliyor ki arayuz ile
# gorseller ayni paleti kullansin.
PALETTE = {
    "bg": "#0D0D0D",
    "surface": "#161616",
    "surface_2": "#1E1E1E",
    "border": "#2A2A2A",
    "text": "#F5F5F0",
    "muted": "#8A8A84",
    "accent": "#E9E34F",
    "accent_dark": "#CFC93C",
    "lstm": "#9B8CF0",
    "gru": "#E9E34F",
    "actual": "#6E6E68",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #0D0D0D;
  --surface: #161616;
  --surface-2: #1E1E1E;
  --border: #2A2A2A;
  --text: #F5F5F0;
  --muted: #8A8A84;
  --accent: #E9E34F;
  --accent-dark: #CFC93C;
}

/* --- Temel --- */
.stApp { background: var(--bg); }

/* Arka plan atmosferi: yavasca dolasan iki isik lekesi ve ince izgara.
   Sabit konumlu, icerigin arkasinda, tiklamayi engellemiyor. */
.stApp::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(680px 480px at 12% 8%, rgba(233,227,79,.10), transparent 65%),
    radial-gradient(560px 420px at 88% 22%, rgba(155,140,240,.09), transparent 62%),
    radial-gradient(720px 520px at 50% 105%, rgba(233,227,79,.05), transparent 70%);
  animation: sur 26s ease-in-out infinite alternate;
}
/* Sayfa boyunca inen dikey sutun cizgileri. Sabit konumlu, tam yukseklik. */
.stApp::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: repeating-linear-gradient(
    90deg,
    rgba(255,255,255,.055) 0 1px,
    transparent 1px calc(100% / 7)
  );
  background-size: 100% 100%;
  mask-image: linear-gradient(180deg, transparent 0, #000 8%, #000 88%, transparent 100%);
}

/* Dar ekranda cizgiler sikisip gurultu yapmasin */
@media (max-width: 900px) {
  .stApp::after { background-image: repeating-linear-gradient(
    90deg, rgba(255,255,255,.05) 0 1px, transparent 1px calc(100% / 3)); }
}
@keyframes sur {
  0%   { transform: translate3d(0, 0, 0) scale(1); }
  50%  { transform: translate3d(-2.5%, 2%, 0) scale(1.06); }
  100% { transform: translate3d(2%, -1.5%, 0) scale(1.02); }
}
[data-testid="stMainBlockContainer"], [data-testid="stSidebar"] { position: relative; z-index: 1; }
html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; color: var(--text); }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { padding-top: 2rem; max-width: 1240px; }
p, li, span, label { color: var(--text); }

/* --- Basliklar --- */
h1, h2, h3 { font-family: 'Inter', sans-serif !important; color: var(--text);
  letter-spacing: -0.03em; font-weight: 700 !important; }
h2 { font-size: 1.7rem !important; margin-top: 2.6rem !important; }
h3 { font-size: 1.1rem !important; }

/* Bolum basliklarinin ustundeki ince cizgi */
h2::before { content: ""; display: block; width: 28px; height: 2px;
  background: var(--accent); margin-bottom: .9rem; }

/* --- Monospace etiketler --- */
.mono { font-family: 'JetBrains Mono', monospace; font-size: .68rem;
  letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }

/* --- Animasyonlar --- */
@keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
@keyframes grow { from { width: 0 !important; } }
@keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: .2; } }
@keyframes nudge { 0%,100% { transform: translateX(0); } 50% { transform: translateX(-4px); } }
.fade { animation: fadeUp .6s cubic-bezier(.22,.61,.36,1) both; }
.d1 { animation-delay: .07s; } .d2 { animation-delay: .14s; }
.d3 { animation-delay: .21s; } .d4 { animation-delay: .28s; }
/* Kaydirmaya bagli animasyon. @supports disinda kalan tarayicilarda
   icerik animasyonsuz ve normal gorunur. */
@supports (animation-timeline: view()) {
  h2 {
    animation: buyu linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 26%;
  }
  .card, .step, .stat {
    animation: belir linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 22%;
  }
}
@keyframes buyu {
  from { opacity: 0; transform: scale(.86) translateY(24px); letter-spacing: .01em; }
  to   { opacity: 1; transform: none; letter-spacing: -.03em; }
}
@keyframes belir {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .fade, .vs-fill, .card { animation: none !important; }
  .stApp::before { animation: none; }
  @supports (animation-timeline: view()) {
    h2, .card, .step, .stat { animation: none; }
  }
}

/* --- Hero --- */
.hero { padding: 2.5rem 0 1rem; }

.hero-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: .7rem;
  letter-spacing: .18em; text-transform: uppercase; color: var(--accent);
  display: block; margin-bottom: 1.6rem;
  opacity: 0; animation: sizinti .7s ease .1s forwards; }
@keyframes sizinti { to { opacity: 1; } }

/* Baslik maskeli perde gibi asagidan aciliyor */
.hero-title-kap { overflow: hidden; }
.hero-title {
  font-size: clamp(3.4rem, 11vw, 8.5rem); font-weight: 800;
  line-height: .88; letter-spacing: -.05em; color: var(--text);
  margin: 0; text-transform: none;
  transform: translateY(110%);
  animation: perde 1s cubic-bezier(.16,1,.3,1) .18s forwards;
}
@keyframes perde { to { transform: translateY(0); } }

/* Baslik altindaki iki kose etiketi */
.hero-meta { display: flex; justify-content: space-between; align-items: flex-end;
  gap: 2rem; margin: 1.4rem 0 2rem; flex-wrap: wrap;
  opacity: 0; animation: sizinti .8s ease .75s forwards; }
.hero-meta .mono { line-height: 1.7; }
.hero-meta .sag { text-align: right; color: var(--accent); }

.hero-sub { font-size: 1.02rem; color: var(--muted); max-width: 54ch;
  line-height: 1.75; margin: 0;
  opacity: 0; animation: sizinti .8s ease .6s forwards; }

/* Ince akan cizgi */
.akan { height: 1px; background: var(--border); position: relative;
  overflow: hidden; margin: 2.4rem 0 1.6rem; }
.akan::after { content: ""; position: absolute; top: 0; left: -35%;
  width: 35%; height: 100%;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  animation: kay 4.5s ease-in-out infinite; }
@keyframes kay { 0% { left: -35%; } 100% { left: 100%; } }


/* --- Ozet seridi --- */
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  border-top: 1px solid var(--border); border-bottom: 1px solid var(--border);
  margin: 2.2rem 0 1.6rem; }
.stat { padding: 1.1rem 1.2rem 1.1rem 0; border-right: 1px solid var(--border);
  display: flex; flex-direction: column; gap: .35rem; }
.stat:last-child { border-right: none; }
.stat-label { font-family: 'JetBrains Mono', monospace; font-size: .64rem;
  letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.stat-value { font-size: 1.45rem; font-weight: 700; color: var(--text);
  letter-spacing: -.02em; }

/* --- Kartlar --- */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1rem; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 4px;
  padding: 1.4rem 1.5rem; transition: border-color .25s ease, transform .25s ease; }
.card:hover { border-color: #3A3A3A; transform: translateY(-3px); }
.card.win { border-color: var(--accent); }
.card-label { font-family: 'JetBrains Mono', monospace; font-size: .66rem;
  letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
.card-value { font-size: 2.6rem; font-weight: 800; color: var(--text);
  margin: .5rem 0 .2rem; letter-spacing: -.035em; line-height: 1; }
.card.win .card-value { color: var(--accent); }
.card-sub { font-size: .8rem; color: var(--muted); }
.badge { display: inline-block; font-family: 'JetBrains Mono', monospace;
  font-size: .58rem; letter-spacing: .1em; text-transform: uppercase;
  color: #0D0D0D; background: var(--accent); padding: .22rem .5rem;
  border-radius: 2px; margin-left: .6rem; vertical-align: middle; font-weight: 500; }
.cards .card:nth-child(1) { animation: fadeUp .5s cubic-bezier(.22,.61,.36,1) .05s both; }
.cards .card:nth-child(2) { animation: fadeUp .5s cubic-bezier(.22,.61,.36,1) .14s both; }
.bar { height: 3px; background: var(--border); border-radius: 100px; margin-top: 1rem; overflow: hidden; }
.bar span { display: block; height: 100%; background: var(--accent);
  animation: grow .8s cubic-bezier(.22,.61,.36,1) both; }

/* --- Sidebar --- */
[data-testid="stSidebar"] { background: #111111; border-right: 1px solid var(--border); }
[data-testid="stSidebar"] h2 { font-size: 1.1rem !important; margin-top: .3rem !important; }
[data-testid="stSidebar"] h2::before { display: none; }
.side-note { font-family: 'JetBrains Mono', monospace; font-size: .68rem;
  letter-spacing: .06em; color: var(--muted); border-left: 2px solid var(--accent);
  padding: .5rem .7rem; margin-top: 1rem; background: rgba(233,227,79,.05); }

/* --- Butonlar ---
   Aksan rengi yalnizca burada zemin olarak kullaniliyor. */
.stButton > button, .stButton > button * {
  color: #0D0D0D !important; }
.stButton > button {
  background: var(--accent) !important; border: none !important;
  border-radius: 3px; font-weight: 700; font-size: .88rem;
  letter-spacing: .02em; padding: .8rem 1rem; width: 100%;
  transition: background .2s ease, transform .12s ease, box-shadow .25s ease; }
.stButton > button:hover {
  background: #F4EF74 !important; transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(233,227,79,.22); }
.stButton > button:active { transform: translateY(0); box-shadow: none; }

/* --- Adim paneli --- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid var(--border); }
.step { padding: 1.8rem 1.6rem 1.8rem 0; border-right: 1px solid var(--border); }
.step:last-child { border-right: none; }
.step-num { font-family: 'JetBrains Mono', monospace; font-size: .8rem;
  color: var(--accent); display: block; margin-bottom: 1rem; letter-spacing: .1em; }
.step-title { font-size: 1rem; font-weight: 600; color: var(--text); margin: 0 0 .5rem; }
.step-text { font-size: .86rem; color: var(--muted); line-height: 1.65; margin: 0; }

.hint { display: flex; align-items: center; gap: .55rem; margin-top: 1.4rem;
  font-size: .85rem; color: var(--muted); }
.hint-arrow { color: var(--accent); animation: nudge 1.6s ease-in-out infinite; }

/* --- Grafik yanindaki mini ozet --- */
.mini { border-top: 1px solid var(--border); }
.mini-satir { display: flex; justify-content: space-between; align-items: baseline;
  padding: .72rem 0; border-bottom: 1px solid var(--border); }
.mini-satir b { font-size: 1.05rem; font-weight: 700; color: var(--text);
  letter-spacing: -.01em; }

/* --- Sonuc anlatimi --- */
.verdict { font-size: 1.15rem; line-height: 1.7; color: var(--text);
  max-width: 68ch; margin: 0 0 1.6rem; font-weight: 400; }
.verdict strong { color: var(--accent); font-weight: 600; }

.vs { margin: 1.4rem 0 .3rem; }
.vs-row { display: flex; align-items: center; gap: .8rem; margin-bottom: .6rem; }
.vs-ad { font-family: 'JetBrains Mono', monospace; font-size: .7rem;
  color: var(--muted); width: 46px; letter-spacing: .08em; }
.vs-track { flex: 1; height: 8px; background: var(--surface-2); overflow: hidden; }
.vs-fill { height: 100%; animation: grow .8s cubic-bezier(.22,.61,.36,1) both; }
.vs-deger { font-family: 'JetBrains Mono', monospace; font-size: .78rem;
  color: var(--text); width: 56px; text-align: right; }

.note { border-left: 2px solid var(--accent); background: rgba(233,227,79,.05);
  padding: 1rem 1.2rem; font-size: .9rem; line-height: 1.7; color: var(--muted);
  margin-top: 1.6rem; max-width: 74ch; }
.note strong { color: var(--text); }

/* --- Egitim durumu --- */
.training { display: flex; align-items: center; font-family: 'JetBrains Mono', monospace;
  font-size: .8rem; letter-spacing: .08em; color: var(--muted); padding: .9rem 0; }
.pulse { display: inline-block; width: 6px; height: 6px; border-radius: 50%;
  background: var(--accent); margin-right: .6rem; animation: blink 1.1s ease-in-out infinite; }

/* --- Sekmeler --- */
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .2rem; border-bottom: 1px solid var(--border); }
[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: 'JetBrains Mono', monospace; font-size: .74rem; letter-spacing: .09em;
  text-transform: uppercase; color: var(--muted); padding: .6rem .9rem;
  transition: color .18s ease, background .18s ease; }
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--text); background: rgba(233,227,79,.06); }
[data-testid="stTabs"] [aria-selected="true"] { color: var(--accent) !important; }
[data-testid="stTabs"] [data-testid="stTabPanel"] { animation: fadeUp .35s ease both; padding-top: .8rem; }

/* --- Sozluk --- */
[data-testid="stExpander"] { border: 1px solid var(--border); border-radius: 4px;
  background: var(--surface); }
[data-testid="stExpander"] summary { font-size: .88rem; font-weight: 600; color: var(--text); }
.terim { padding: .7rem 0; border-bottom: 1px solid var(--border); }
.terim:last-child { border-bottom: none; }
.terim b { color: var(--accent); font-size: .88rem; font-weight: 600; }
.terim span { display: block; font-size: .85rem; color: var(--muted); line-height: 1.65; margin-top: .3rem; }

/* --- Secim etiketleri (multiselect) ---
   Streamlit varsayilan olarak primaryColor'i zemin yapiyor; notr yuzeye
   cekiliyor ki aksan rengi yalnizca ana dugmede kalsin. */
[data-baseweb="tag"] {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
}
[data-baseweb="tag"] span,
[data-baseweb="tag"] div { color: var(--text) !important; font-weight: 500; }
[data-baseweb="tag"] svg { fill: var(--muted) !important; }
[data-baseweb="tag"]:hover { border-color: #3A3A3A !important; }
[data-baseweb="tag"] [role="button"]:hover svg { fill: var(--accent) !important; }

/* Acilir listede secili satir */
[data-baseweb="menu"] li[aria-selected="true"] { background: rgba(233,227,79,.14) !important; }

/* --- Tablo --- */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }

/* --- Alt bilgi --- */
.footer { border-top: 1px solid var(--border); margin-top: 3.5rem; padding: 1.6rem 0 2.5rem;
  font-family: 'JetBrains Mono', monospace; font-size: .68rem; letter-spacing: .1em;
  text-transform: uppercase; color: var(--muted);
  display: flex; justify-content: space-between; flex-wrap: wrap; gap: .8rem; }

/* Streamlit'in eylem menusunu gizle. stToolbar'in tamami gizlenemez:
   kenar cubugunu geri acan dugme de o kapsamda. */
[data-testid="stToolbarActions"], footer { visibility: hidden; }

/* Durum bildirimi (calisiyor / baglanti hatasi) temaya uysun.
   Gizlemiyoruz; baglanti koptugunda gorunmesi gerekiyor. */
[data-testid="stStatusWidget"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px;
  font-family: 'JetBrains Mono', monospace; font-size: .7rem;
  letter-spacing: .06em;
}
[data-testid="stStatusWidget"] * { color: var(--text) !important; }
[data-testid="stStatusWidget"] svg { fill: var(--accent) !important; }
[data-testid="stStatusWidget"] button:hover { background: rgba(233,227,79,.10) !important; }

[data-testid="stExpandSidebarButton"],
[data-testid="stSidebarCollapseButton"] {
  visibility: visible !important; opacity: 1 !important; pointer-events: auto !important; }
[data-testid="stExpandSidebarButton"] button:hover,
[data-testid="stSidebarCollapseButton"] button:hover { background: rgba(233,227,79,.12); }

@media (max-width: 760px) {
  .steps { grid-template-columns: 1fr; }
  .step { border-right: none; border-bottom: 1px solid var(--border); padding-right: 0; }
  .step:last-child { border-bottom: none; }
}
</style>
"""


def altair_theme():
    """Grafikleri koyu zeminle uyumlu hale getirir."""
    return {
        "config": {
            "background": PALETTE["surface"],
            "view": {"stroke": "transparent"},
            "font": "Inter",
            "title": {"color": PALETTE["text"], "fontSize": 13, "fontWeight": 600,
                      "anchor": "start", "dy": -6},
            "axis": {
                "labelColor": PALETTE["muted"],
                "titleColor": PALETTE["muted"],
                "labelFontSize": 10,
                "titleFontSize": 10,
                "titleFontWeight": 500,
                "gridColor": "#232323",
                "domainColor": PALETTE["border"],
                "tickColor": PALETTE["border"],
            },
            "legend": {
                "labelColor": PALETTE["muted"],
                "titleColor": PALETTE["muted"],
                "labelFontSize": 11,
                "titleFontSize": 11,
            },
        }
    }
