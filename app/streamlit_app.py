"""Predictor — LSTM ve GRU modellerini aynı hisse verisinde karşılaştıran arayüz."""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import altair as alt
import pandas as pd
import streamlit as st
import torch

from data import (FEATURE_COLUMNS, create_sliding_windows, download_data, fetch_market_caps,
                  format_market_cap, scale_features, scale_target, train_test_split_sequences)
from evaluate import evaluate_model
from models import GRUModel, LSTMModel
from theme import CSS, PALETTE, altair_theme
from train import train_model

st.set_page_config(page_title="Predictor — LSTM vs GRU", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)
alt.theme.register("predictor", enable=True)(altair_theme)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def _cihaz_etiketi():
    """Kısa üretici etiketi döndürür: NVIDIA GPU, AMD GPU, GPU veya CPU."""
    if DEVICE != "cuda":
        return "CPU"

    ad = torch.cuda.get_device_name(0).lower()
    if any(k in ad for k in ("nvidia", "geforce", "rtx", "gtx", "quadro", "tesla")):
        return "NVIDIA GPU"
    if any(k in ad for k in ("amd", "radeon", "instinct")):
        return "AMD GPU"
    return "GPU"


DEVICE_LABEL = _cihaz_etiketi()


@st.cache_data(ttl=60 * 60 * 12, show_spinner="Piyasa değerleri alınıyor…")
def top_companies():
    return fetch_market_caps(top_n=10)


@st.cache_data(ttl=60 * 60 * 6, show_spinner=False)
def load_prices(symbol: str, start: str, end: str) -> pd.DataFrame:
    return download_data(ticker=symbol, start=start, end=end)


def stat(label: str, value: str) -> str:
    return f'<div class="stat"><span class="stat-label">{label}</span><span class="stat-value">{value}</span></div>'


def score_card(name: str, pct: float, dollars: float, seconds: float, win: bool) -> str:
    badge = '<span class="badge">daha isabetli</span>' if win else ""
    return (
        f'<div class="card{" win" if win else ""}">'
        f'<div class="card-label">{name}</div>'
        f'<div class="card-value">%{pct:.1f}{badge}</div>'
        f'<div class="card-sub">ortalama sapma · ${dollars:.2f} · {seconds:.2f} sn</div>'
        f'<div class="bar"><span style="width:{min(pct * 4, 100):.0f}%"></span></div>'
        "</div>"
    )


def price_chart(df: pd.DataFrame, symbol: str) -> alt.Chart:
    return (
        alt.Chart(df).mark_line(color=PALETTE["accent"], strokeWidth=1.5)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y("Close:Q", title="Kapanış ($)", scale=alt.Scale(zero=False)),
            tooltip=[alt.Tooltip("Date:T", title="Tarih"),
                     alt.Tooltip("Close:Q", title="Kapanış", format="$.2f")],
        )
        .properties(height=240, title=f"{symbol} kapanış fiyatı")
    )


def prediction_chart(y_true, y_pred, name: str, color: str) -> alt.Chart:
    long = pd.concat([
        pd.DataFrame({"gun": range(len(y_true)), "fiyat": y_true, "seri": "Gerçek"}),
        pd.DataFrame({"gun": range(len(y_pred)), "fiyat": y_pred, "seri": "Tahmin"}),
    ])
    return (
        alt.Chart(long).mark_line(strokeWidth=1.4)
        .encode(
            x=alt.X("gun:Q", title="Test günü"),
            y=alt.Y("fiyat:Q", title="Fiyat ($)", scale=alt.Scale(zero=False)),
            color=alt.Color("seri:N", title=None,
                            scale=alt.Scale(domain=["Gerçek", "Tahmin"],
                                            range=[PALETTE["actual"], color])),
            tooltip=[alt.Tooltip("fiyat:Q", format="$.2f"), "seri:N"],
        )
        .properties(height=280, title=name)
    )


def combined_chart(results: dict, gun: int = 120) -> alt.Chart:
    """Son N günün gerçek fiyatı ve iki modelin tahmini, tek eksende."""
    gercek = results["LSTM"]["test"]["y_true"][-gun:]
    frames = [pd.DataFrame({"gun": range(len(gercek)), "fiyat": gercek, "seri": "Gerçek"})]
    for name in ("LSTM", "GRU"):
        p = results[name]["test"]["y_pred"][-gun:]
        frames.append(pd.DataFrame({"gun": range(len(p)), "fiyat": p, "seri": name}))

    return (
        alt.Chart(pd.concat(frames)).mark_line(strokeWidth=1.5)
        .encode(
            x=alt.X("gun:Q", title=f"Son {gun} test günü"),
            y=alt.Y("fiyat:Q", title="Fiyat ($)", scale=alt.Scale(zero=False)),
            color=alt.Color("seri:N", title=None,
                            scale=alt.Scale(domain=["Gerçek", "LSTM", "GRU"],
                                            range=[PALETTE["actual"], PALETTE["lstm"],
                                                   PALETTE["gru"]])),
            strokeDash=alt.StrokeDash("seri:N", legend=None,
                                      scale=alt.Scale(domain=["Gerçek", "LSTM", "GRU"],
                                                      range=[[1, 0], [4, 2], [4, 2]])),
            tooltip=[alt.Tooltip("fiyat:Q", format="$.2f"), "seri:N"],
        )
        .properties(height=300, title="Yakınlaştırılmış karşılaştırma")
    )


def error_chart(results: dict) -> alt.Chart:
    """Tahmin hatalarının dağılımı."""
    frames = []
    for name, r in results.items():
        hata = r["test"]["y_pred"] - r["test"]["y_true"]
        frames.append(pd.DataFrame({"hata": hata, "model": name}))

    return (
        alt.Chart(pd.concat(frames)).mark_bar(opacity=0.65)
        .encode(
            x=alt.X("hata:Q", bin=alt.Bin(maxbins=45), title="Tahmin − Gerçek ($)"),
            y=alt.Y("count()", title="Gün sayısı", stack=None),
            color=alt.Color("model:N", title=None,
                            scale=alt.Scale(domain=["LSTM", "GRU"],
                                            range=[PALETTE["lstm"], PALETTE["gru"]])),
            tooltip=["model:N", alt.Tooltip("count()", title="Gün")],
        )
        .properties(height=260, title="Hata dağılımı")
    )


def residual_chart(results: dict) -> alt.Chart:
    """Hatanın test dönemi boyunca seyri."""
    frames = []
    for name, r in results.items():
        hata = r["test"]["y_pred"] - r["test"]["y_true"]
        frames.append(pd.DataFrame({"gun": range(len(hata)), "hata": hata, "model": name}))

    return (
        alt.Chart(pd.concat(frames)).mark_line(strokeWidth=1, opacity=0.8)
        .encode(
            x=alt.X("gun:Q", title="Test günü"),
            y=alt.Y("hata:Q", title="Sapma ($)"),
            color=alt.Color("model:N", title=None,
                            scale=alt.Scale(domain=["LSTM", "GRU"],
                                            range=[PALETTE["lstm"], PALETTE["gru"]])),
        )
        .properties(height=260, title="Sapma zaman içinde")
    )


def loss_chart(histories: dict) -> alt.Chart:
    frames = [pd.DataFrame({"epoch": range(1, len(h) + 1), "kayip": h, "model": n})
              for n, h in histories.items()]
    return (
        alt.Chart(pd.concat(frames)).mark_line(strokeWidth=1.6)
        .encode(
            x=alt.X("epoch:Q", title="Epoch"),
            y=alt.Y("kayip:Q", title="Hata", scale=alt.Scale(type="log")),
            color=alt.Color("model:N", title=None,
                            scale=alt.Scale(domain=["LSTM", "GRU"],
                                            range=[PALETTE["lstm"], PALETTE["gru"]])),
            tooltip=["epoch:Q", alt.Tooltip("kayip:Q", format=".6f"), "model:N"],
        )
        .properties(height=250, title="Eğitim kaybı")
    )


with st.sidebar:
    st.markdown("## Ayarlar")

    companies = top_companies()
    MANUEL = "Diğer (sembolü kendim gireyim)"
    labels = [f"{c['ticker']} · {c['name'][:18]} — {format_market_cap(c['market_cap'])}"
              for c in companies] + [MANUEL]
    default_idx = next((i for i, c in enumerate(companies) if c["ticker"] == "MSFT"), 0)

    choice = st.selectbox("Şirket", labels, index=default_idx,
                          help="Piyasa değerine göre en büyük 10 şirket, canlı veriyle sıralanır.")
    ticker = (st.text_input("Sembol", value="MSFT").strip().upper() if choice == MANUEL
              else companies[labels.index(choice)]["ticker"])

    col_a, col_b = st.columns(2)
    start = col_a.date_input("Başlangıç", value=pd.Timestamp("2014-01-01"))
    end = col_b.date_input("Bitiş", value=pd.Timestamp("2026-01-01"))

    selected_features = st.multiselect(
        "Girdi sütunları", FEATURE_COLUMNS, default=FEATURE_COLUMNS,
        help="Modele hangi fiyat sütunlarının verileceği. Hedef her zaman ertesi "
             "günün kapanışı. Sadece Close seçmeyi deneyin, sonuç şaşırtabilir.",
    )

    with st.expander("Model ayarları"):
        lookback = st.slider(
            "Kaç gün geriye baksın", 5, 60, 20,
            help="Model tahmin yaparken kaç günlük geçmişe bakacak.",
        )
        hidden_size = st.slider(
            "Gizli katman boyutu", 8, 128, 32, step=8,
            help="Modelin kapasitesi. Büyük değer daha çok şey öğrenebilir ama "
                 "ezberlemeye de daha yatkın olur.",
        )
        epochs = st.slider(
            "Epoch", 10, 200, 100, step=10,
            help="Modelin tüm eğitim verisini kaç kez göreceği.",
        )

    run = st.button("Modelleri yarıştır", type="primary")
    st.markdown(f'<div class="side-note">Eğitim <strong>{DEVICE_LABEL}</strong> üzerinde çalışır.</div>',
                unsafe_allow_html=True)


st.markdown(
    '<div class="hero">'
    '<span class="hero-eyebrow">PyTorch · Zaman Serisi</span>'
    '<div class="hero-title-kap"><h1 class="hero-title">Predictor</h1></div>'
    '<div class="hero-meta">'
    '<span class="mono">LSTM &amp; GRU<br>KARŞILAŞTIRMASI</span>'
    f'<span class="mono sag">{DEVICE_LABEL}<br>20 GÜNLÜK PENCERE</span>'
    "</div>"
    '<p class="hero-sub">Bir hissenin son 20 gününe bakıp yarınki kapanışı tahmin etmeye '
    "çalışan iki sinir ağını yarıştırır. İkisi de aynı veriyle, aynı ayarlarla "
    "eğitilir; hangisinin daha az yanıldığı ölçülür.</p>"
    '<div class="akan"></div>'
    "</div>",
    unsafe_allow_html=True,
)

if not ticker:
    st.warning("Bir hisse sembolü girin.")
    st.stop()

df = load_prices(ticker, str(start), str(end))
if df.empty:
    st.error(f"'{ticker}' için veri bulunamadı. Sembolü ve tarih aralığını kontrol edin.")
    st.stop()

first, last = float(df["Close"].iloc[0]), float(df["Close"].iloc[-1])
change = (last - first) / first * 100
st.markdown(
    '<div class="stats fade d1">'
    + stat("Şirket", ticker)
    + stat("Gün sayısı", f"{len(df):,}".replace(",", "."))
    + stat("Fiyat aralığı", f"${df['Close'].min():.0f} – ${df['Close'].max():.0f}")
    + stat("Dönem değişimi", f"{'+' if change >= 0 else ''}{change:.0f}%")
    + "</div>",
    unsafe_allow_html=True,
)
grafik_sut, ozet_sut = st.columns([3, 1], gap="medium")
grafik_sut.altair_chart(price_chart(df, ticker), width="stretch")

son30 = df.tail(30)
degisim30 = (float(son30["Close"].iloc[-1]) - float(son30["Close"].iloc[0])) / float(
    son30["Close"].iloc[0]) * 100
ozet_sut.markdown(
    f'<div class="mini fade d2">'
    f'<div class="mini-satir"><span class="mono">Son kapanış</span>'
    f'<b>${last:.2f}</b></div>'
    f'<div class="mini-satir"><span class="mono">Son 30 gün</span>'
    f'<b style="color:{PALETTE["accent"] if degisim30 >= 0 else "#E07A5F"}">'
    f'{"+" if degisim30 >= 0 else ""}{degisim30:.1f}%</b></div>'
    f'<div class="mini-satir"><span class="mono">Ort. hacim</span>'
    f'<b>{df["Volume"].mean() / 1e6:.1f}M</b></div>'
    f'<div class="mini-satir"><span class="mono">Girdi sütunu</span>'
    f'<b>{len(selected_features)}</b></div>'
    f'<div class="mini-satir"><span class="mono">Pencere</span>'
    f'<b>{lookback} gün</b></div>'
    f"</div>",
    unsafe_allow_html=True,
)

if not run:
    st.markdown(
        '<div class="steps fade d2">'
        '<div class="step"><span class="step-num">01</span>'
        '<p class="step-title">Veriyi böl</p>'
        '<p class="step-text">20 günlük pencereler oluşur. İlk %80 öğrenmek için, '
        "son %20 sınav için ayrılır.</p></div>"
        '<div class="step"><span class="step-num">02</span>'
        '<p class="step-title">İkisini de eğit</p>'
        '<p class="step-text">LSTM ve GRU aynı veriyi aynı ayarlarla sıfırdan öğrenir. '
        "Kimse avantajlı başlamaz.</p></div>"
        '<div class="step"><span class="step-num">03</span>'
        '<p class="step-title">Sınav</p>'
        '<p class="step-text">Hiç görmedikleri son %20\'de tahmin yaparlar. '
        "Ne kadar saptıkları ölçülür.</p></div>"
        "</div>"
        '<div class="hint fade d3"><span class="hint-arrow">←</span>'
        "Ayarları soldan yapıp <strong>Modelleri yarıştır</strong> düğmesine basın.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="footer"><span>Predictor · LSTM vs GRU</span>'
        "<span>PyTorch · Streamlit · yfinance</span></div>",
        unsafe_allow_html=True,
    )
    st.stop()

if not selected_features:
    st.error("En az bir girdi sütunu seçmelisiniz.")
    st.stop()

features, _ = scale_features(df, selected_features, feature_range=(-1, 1))
target, target_scaler = scale_target(df, feature_range=(-1, 1))

X, y = create_sliding_windows(features, target, lookback=lookback)
X_train, X_test, y_train, y_test = train_test_split_sequences(X, y, train_ratio=0.8)

X_train_t = torch.from_numpy(X_train).float()
y_train_t = torch.from_numpy(y_train).float().reshape(-1, 1)
X_test_t = torch.from_numpy(X_test).float()

results, histories, param_counts = {}, {}, {}
status = st.empty()

for name, model_cls in [("LSTM", LSTMModel), ("GRU", GRUModel)]:
    status.markdown(f'<div class="training"><span class="pulse"></span>{name} öğreniyor…</div>',
                    unsafe_allow_html=True)
    torch.manual_seed(42)
    model = model_cls(input_size=len(selected_features), hidden_size=hidden_size,
                      num_layers=2, output_size=1)
    param_counts[name] = sum(p.numel() for p in model.parameters())

    model, history, elapsed = train_model(model, X_train_t, y_train_t, epochs=epochs,
                                          device=DEVICE, verbose=False)
    model.eval()
    with torch.no_grad():
        preds = model(X_test_t.to(DEVICE)).cpu().numpy()
        train_preds = model(X_train_t.to(DEVICE)).cpu().numpy()

    results[name] = {
        "test": evaluate_model(y_test, preds, target_scaler),
        "train": evaluate_model(y_train, train_preds, target_scaler),
        "time": elapsed,
    }
    histories[name] = history

status.empty()

avg_price = float(results["LSTM"]["test"]["y_true"].mean())
for r in results.values():
    r["pct"] = r["test"]["rmse"] / avg_price * 100
best = min(results, key=lambda k: results[k]["pct"])
other = "GRU" if best == "LSTM" else "LSTM"

st.markdown("## Sonuç")
st.markdown(
    f'<p class="verdict fade">{ticker} hissesinde <strong>{best}</strong> daha isabetli çıktı. '
    f"Tahminleri gerçek fiyattan ortalama <strong>%{results[best]['pct']:.1f}</strong> saptı; "
    f"{other} ise %{results[other]['pct']:.1f}. Yani 100 dolarlık bir hissede "
    f"{best} ~{results[best]['pct']:.0f} dolar yanılıyor.</p>",
    unsafe_allow_html=True,
)

cards = "".join(
    score_card(n, results[n]["pct"], results[n]["test"]["rmse"], results[n]["time"], n == best)
    for n in ("LSTM", "GRU")
)
st.markdown(f'<div class="cards fade d1">{cards}</div>', unsafe_allow_html=True)

# Iki modeli ayni olcekte gosteren cubuk
en_kotu = max(r["pct"] for r in results.values())
cubuklar = "".join(
    f'<div class="vs-row"><span class="vs-ad">{n}</span>'
    f'<span class="vs-track"><span class="vs-fill" style="width:'
    f'{results[n]["pct"] / en_kotu * 100:.0f}%;background:'
    f'{PALETTE["gru"] if n == best else PALETTE["lstm"]}"></span></span>'
    f'<span class="vs-deger">%{results[n]["pct"]:.1f}</span></div>'
    for n in ("LSTM", "GRU")
)
st.markdown(
    f'<div class="vs fade d2">{cubuklar}</div>'
    f'<p style="color:{PALETTE["muted"]};font-size:.82rem;margin:.2rem 0 0">'
    "Kısa çubuk daha az hata demek.</p>",
    unsafe_allow_html=True,
)

gap = results[best]["test"]["rmse"] / results[best]["train"]["rmse"]
st.markdown(
    f'<div class="note fade d2">{best} öğrendiği veride sadece '
    f"${results[best]['train']['rmse']:.2f} yanılıyor, hiç görmediği veride ise "
    f"${results[best]['test']['rmse']:.2f}. Arada <strong>{gap:.0f} kat</strong> fark var. "
    "Yani model geçmişi ezberlemiş, geleceği tahmin etmiyor. Hisse tahmininin neden zor "
    "olduğu tam olarak burada görülüyor.</div>",
    unsafe_allow_html=True,
)

tab_tahmin, tab_hata, tab_egitim, tab_model, tab_veri, tab_sozluk = st.tabs(
    ["Tahminler", "Hatalar", "Öğrenme", "Modeller", "Veri", "Terimler"]
)

with tab_tahmin:
    left, right = st.columns(2)
    for col, (name, color) in zip([left, right],
                                  [("LSTM", PALETTE["lstm"]), ("GRU", PALETTE["gru"])]):
        col.altair_chart(prediction_chart(results[name]["test"]["y_true"],
                                          results[name]["test"]["y_pred"], name, color),
                         width="stretch")
    st.caption("Çizgiler yapışık görünüyor ama bu yanıltıcı. Günlük değişim %1-2 "
               "civarında, eksen ise yüzlerce dolarlık aralıkta. Model 'yarın da bugüne "
               "benzer' dese bile grafik böyle çıkardı.")

    st.altair_chart(combined_chart(results), width="stretch")
    st.caption("Son 120 güne yakınlaştırınca aradaki fark görünür hale geliyor. "
               "Kesikli çizgiler tahminler, düz çizgi gerçek fiyat.")

with tab_hata:
    st.altair_chart(error_chart(results), width="stretch")
    st.altair_chart(residual_chart(results), width="stretch")
    st.caption("Soldaki dağılım 0'ın etrafında ne kadar dar toplanırsa o kadar iyi. "
               "Alttaki grafik sapmanın belirli dönemlerde mi büyüdüğünü gösteriyor.")

with tab_egitim:
    st.altair_chart(loss_chart(histories), width="stretch")
    st.caption("Logaritmik eksen. Kayıp binde birler seviyesine indiği için normal "
               "eksende son iyileşmeler görünmezdi.")

with tab_model:
    satirlar = []
    for name in ("LSTM", "GRU"):
        satirlar.append({
            "Model": name,
            "Parametre": param_counts[name],
            "Gizli katman": hidden_size,
            "Katman": 2,
            "Girdi sütunu": len(selected_features),
            "Train RMSE ($)": round(results[name]["train"]["rmse"], 2),
            "Test RMSE ($)": round(results[name]["test"]["rmse"], 2),
            "Test/Train": round(results[name]["test"]["rmse"] / results[name]["train"]["rmse"], 1),
            "Süre (sn)": round(results[name]["time"], 2),
        })
    st.dataframe(pd.DataFrame(satirlar), width="stretch", hide_index=True)
    st.caption("GRU'nun daha az parametresi var çünkü kapı yapısı daha sade. "
               "Test/Train oranı 1'e ne kadar yakınsa model o kadar iyi genelliyor.")

with tab_sozluk:
    terimler = [
        ("RMSE", "Tahminlerin gerçek fiyattan ortalama kaç dolar saptığı. "
                 "Küçük olması iyi. Farklı hisseler arasında karşılaştırılamaz, "
                 "çünkü 50 dolarlık bir hissedeki 5 dolar hata ile 500 dolarlıktaki "
                 "5 dolar aynı şey değil."),
        ("Overfitting (aşırı öğrenme)",
         "Modelin eğitim verisini ezberleyip yeni veride başarısız olması. "
         "Eğitim hatası düşük, test hatası yüksekse bu olmuş demektir. "
         "Modeller sekmesindeki Test/Train oranı 1'e ne kadar yakınsa o kadar iyi."),
        ("Lookback", "Modelin tahmin yaparken geriye baktığı gün sayısı. "
                     "Bu projede varsayılan 20 gün."),
        ("Epoch", "Modelin tüm eğitim verisini bir kez baştan sona görmesi. "
                  "100 epoch, veriyi 100 kez gözden geçirmesi demek."),
        ("LSTM ve GRU", "İkisi de diziler üzerinde çalışan sinir ağı türü. "
                        "Geçmişi bir tür hafızada tutarlar. GRU daha sade bir "
                        "yapıya sahip, bu yüzden daha az parametresi var ve "
                        "genelde daha hızlı eğitiliyor."),
        ("Eğitim / test ayrımı",
         "Veri ikiye bölünüyor: ilk %80 ile model öğreniyor, son %20 ile "
         "sınav oluyor. Zaman serisi olduğu için karıştırma yapılmıyor, "
         "yoksa model geleceği görmüş olurdu."),
    ]
    st.markdown(
        "".join(f'<div class="terim"><b>{ad}</b><span>{aciklama}</span></div>'
                for ad, aciklama in terimler),
        unsafe_allow_html=True,
    )

with tab_veri:
    c1, c2 = st.columns([2, 1])
    c1.markdown("**Son 10 gün**")
    son = df.tail(10).copy()
    son["Date"] = son["Date"].dt.strftime("%Y-%m-%d")  # saat kismi gereksiz
    sayisal = son.select_dtypes("number").columns
    son[sayisal] = son[sayisal].round(2)
    c1.dataframe(son, width="stretch", hide_index=True)

    c2.markdown("**Sütunlar arası korelasyon**")
    # 4 basamak: 3'te fiyat sutunlari 1.000 gorunup birbirinden ayirt edilemiyor
    kor = df[selected_features].corr().round(4)
    kor.columns.name = None
    kor.index.name = None
    c2.dataframe(kor, width="stretch")
    st.caption("Fiyat sütunları birbirine neredeyse birebir bağlı. Bu yüzden hepsini "
               "birden vermek modele beklendiği kadar yeni bilgi katmıyor.")
