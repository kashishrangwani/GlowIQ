import streamlit as st
import json
from recommend import get_recommendations, calculate_skin_profile
from products import PRODUCT_DATABASE
from ml_model import ml_predict_categories, get_model_accuracy_report, CATEGORY_LABELS
from scraper import load_data
from eda_page import render_eda

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlowIQ – Personalised Skincare",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=DM+Sans:wght@300;400;500&display=swap');
:root{--sage:#7A9E7E;--sage-light:#B8D4BC;--sage-pale:#EAF2EB;--cream:#FAF8F5;--charcoal:#2C2C2C;--mid:#6B6B6B;--border:#E0EBE1;--white:#FFFFFF;}
html,body,.stApp{background-color:var(--cream)!important;font-family:'DM Sans',sans-serif;color:var(--charcoal);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{padding-top:2rem!important;max-width:960px!important;}
.hero{text-align:center;padding:2.5rem 1rem 1.2rem;border-bottom:1px solid var(--border);margin-bottom:2rem;}
.hero-logo{font-family:'Cormorant Garamond',serif;font-size:3.2rem;font-weight:300;color:var(--charcoal);letter-spacing:.08em;margin:0;}
.hero-logo span{color:var(--sage);}
.hero-tagline{font-size:.9rem;color:var(--mid);letter-spacing:.15em;text-transform:uppercase;margin-top:.3rem;}
.progress-wrap{display:flex;justify-content:center;gap:.5rem;margin-bottom:2rem;}
.step-dot{width:32px;height:4px;border-radius:2px;background:var(--border);}
.step-dot.active{background:var(--sage);}
.step-dot.done{background:var(--sage-light);}
.section-card{background:var(--white);border:1px solid var(--border);border-radius:16px;padding:2rem 2.5rem;margin-bottom:1.5rem;box-shadow:0 2px 12px rgba(122,158,126,.07);}
.section-title{font-family:'Cormorant Garamond',serif;font-size:1.7rem;font-weight:500;color:var(--charcoal);margin-bottom:.3rem;}
.section-sub{font-size:.85rem;color:var(--mid);margin-bottom:1.5rem;}
.stRadio>div{gap:.5rem!important;}
.stRadio label,.stCheckbox label{background:var(--sage-pale);border:1px solid var(--border);border-radius:10px;padding:.55rem 1.1rem!important;font-size:.88rem;cursor:pointer;transition:all .2s;display:flex!important;align-items:center;}
.stRadio label:hover,.stCheckbox label:hover{border-color:var(--sage);background:#deeee0;}
.stButton>button{background:var(--sage)!important;color:white!important;border:none!important;border-radius:10px!important;padding:.65rem 2.2rem!important;font-family:'DM Sans',sans-serif!important;font-size:.9rem!important;letter-spacing:.05em;transition:background .2s!important;box-shadow:0 2px 8px rgba(122,158,126,.25)!important;}
.stButton>button:hover{background:#5f8463!important;}
.product-card{background:var(--white);border:1px solid var(--border);border-radius:14px;padding:1.4rem;margin-bottom:1rem;transition:box-shadow .2s;}
.product-card:hover{box-shadow:0 4px 20px rgba(122,158,126,.15);}
.product-badge{display:inline-block;background:var(--sage-pale);color:var(--sage);border:1px solid var(--sage-light);border-radius:20px;font-size:.72rem;padding:.2rem .7rem;font-weight:500;letter-spacing:.05em;text-transform:uppercase;margin-bottom:.5rem;}
.product-name{font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-weight:600;color:var(--charcoal);margin:.2rem 0;}
.product-brand{font-size:.8rem;color:var(--mid);text-transform:uppercase;letter-spacing:.08em;}
.product-price{font-size:1rem;font-weight:500;color:var(--sage);margin-top:.5rem;}
.product-why{font-size:.83rem;color:var(--mid);margin-top:.4rem;line-height:1.5;border-top:1px solid var(--border);padding-top:.5rem;}
.product-ingredients{font-size:.75rem;color:#9cb89f;margin-top:.3rem;}
.product-tier-budget{border-left:3px solid #A8D5B5;}
.product-tier-midrange{border-left:3px solid #7A9E7E;}
.product-tier-premium{border-left:3px solid #4A7C59;}
.buy-row{display:flex;gap:.6rem;margin-top:.8rem;flex-wrap:wrap;}
.buy-btn{display:inline-block;text-decoration:none;padding:.32rem 1rem;border-radius:8px;font-size:.78rem;font-family:'DM Sans',sans-serif;font-weight:500;letter-spacing:.03em;transition:opacity .2s;}
.buy-btn:hover{opacity:.85;}
.buy-btn-nykaa{background:#FF6B9D;color:white;}
.buy-btn-amazon{background:#FF9900;color:white;}
.routine-step{display:flex;align-items:flex-start;gap:1rem;padding:.9rem 0;border-bottom:1px solid var(--border);}
.step-num{background:var(--sage);color:white;border-radius:50%;width:28px;height:28px;display:flex;align-items:center;justify-content:center;font-size:.8rem;font-weight:500;flex-shrink:0;}
.step-text{font-size:.88rem;color:var(--charcoal);}
.step-text b{color:var(--sage);}
.score-ring{text-align:center;padding:1.2rem;background:var(--sage-pale);border-radius:12px;border:1px solid var(--sage-light);}
.score-number{font-family:'Cormorant Garamond',serif;font-size:2.8rem;font-weight:600;color:var(--sage);line-height:1;}
.score-label{font-size:.78rem;color:var(--mid);margin-top:.3rem;}
.tip-box{background:#F0F7F1;border-left:3px solid var(--sage);border-radius:0 10px 10px 0;padding:.8rem 1.2rem;margin-top:1rem;font-size:.85rem;color:var(--mid);}
.ml-badge{display:inline-block;background:linear-gradient(135deg,#7A9E7E,#4A7C59);color:white;border-radius:20px;font-size:.72rem;padding:.25rem .8rem;margin-left:.5rem;vertical-align:middle;letter-spacing:.04em;}
.conf-bar-wrap{margin:.3rem 0;}
.conf-bar-label{font-size:.78rem;color:var(--mid);margin-bottom:.15rem;}
.conf-bar-bg{background:#eee;border-radius:4px;height:8px;width:100%;}
.conf-bar-fill{background:var(--sage);border-radius:4px;height:8px;}
.stat-box{background:var(--white);border:1px solid var(--border);border-radius:12px;padding:1.2rem;text-align:center;}
.stat-number{font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:600;color:var(--sage);}
.stat-label{font-size:.78rem;color:var(--mid);}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {"step":0,"name":"","age":22,"skin_type":None,"concerns":[],
                "sensitivity":None,"budget":None,"lifestyle":[],"water_intake":None,
                "sun_exposure":None,"experience":"Beginner","avoid":[]}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init_state()


# ── Helpers ───────────────────────────────────────────────────────────────────
def hero():
    st.markdown('<div class="hero"><p class="hero-logo">Glow<span>IQ</span></p><p class="hero-tagline">Science-backed skincare · Personalised for you</p></div>',unsafe_allow_html=True)

def progress_dots(current,total=5):
    dots="".join([f'<div class="step-dot {"active" if i==current else "done" if i<current else "step-dot"}"></div>' for i in range(1,total+1)])
    st.markdown(f'<div class="progress-wrap">{dots}</div>',unsafe_allow_html=True)

def card_open(title,subtitle=""):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>',unsafe_allow_html=True)

def card_close():
    st.markdown("</div>",unsafe_allow_html=True)

def render_product_card(prod):
    tier_class={"Budget":"product-tier-budget","Mid-range":"product-tier-midrange","Premium":"product-tier-premium"}.get(prod.get("tier",""),"")
    nykaa = prod.get("buy_nykaa","")
    amazon = prod.get("buy_amazon","")
    ingredients = prod.get("key_ingredients",[])
    ingr_html = f'<div class="product-ingredients">✦ Key ingredients: {", ".join(ingredients)}</div>' if ingredients else ""
    buy_html = f'<div class="buy-row">'
    if nykaa: buy_html += f'<a class="buy-btn buy-btn-nykaa" href="{nykaa}" target="_blank">🛍 Search on Nykaa</a>'
    if amazon: buy_html += f'<a class="buy-btn buy-btn-amazon" href="{amazon}" target="_blank">📦 Search on Amazon</a>'
    buy_html += "</div>"
    st.markdown(f'''<div class="product-card {tier_class}">
        <div class="product-badge">{prod.get("category","")}</div>
        <div class="product-name">{prod["name"]}</div>
        <div class="product-brand">{prod["brand"]}</div>
        <div class="product-price">{prod["price"]} &nbsp;<span style="font-size:.75rem;color:#aaa;background:#f5f5f5;padding:2px 8px;border-radius:10px;">{prod.get("tier","")}</span></div>
        <div class="product-why">✦ {prod["why"]}</div>
        {ingr_html}{buy_html}
    </div>''',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGES 0-4  (Landing + Quiz steps)
# ══════════════════════════════════════════════════════════════════════════════
def page_landing():
    hero()
    col1,col2,col3=st.columns([1,2,1])
    with col2:
        st.markdown('<div class="section-card" style="text-align:center;padding:2.5rem;"><div class="section-title" style="font-size:2rem;">Your skin deserves<br>a personalised routine.</div><div class="section-sub" style="font-size:.95rem;margin-top:.8rem;margin-bottom:1.5rem;">Answer 4 quick sections — get a full AM/PM routine<br>with hand-picked products for your exact skin needs.<br><br><span style="font-size:.8rem;background:#EAF2EB;padding:4px 12px;border-radius:20px;color:#7A9E7E;">✦ ML-powered recommendations</span></div></div>',unsafe_allow_html=True)
        name=st.text_input("✦  First, what's your name?",placeholder="e.g. Priya",key="name_input")
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("Begin My Skin Quiz →",use_container_width=True):
            if name.strip():
                st.session_state.name=name.strip(); st.session_state.step=1; st.rerun()
            else: st.warning("Please enter your name to begin.")
        st.markdown('<div style="display:flex;justify-content:center;gap:2rem;margin-top:1.5rem;"><div style="text-align:center;"><div style="font-size:1.4rem;">⏱</div><div style="font-size:.75rem;color:#6B6B6B;">3 minutes</div></div><div style="text-align:center;"><div style="font-size:1.4rem;">🤖</div><div style="font-size:.75rem;color:#6B6B6B;">ML model</div></div><div style="text-align:center;"><div style="font-size:1.4rem;">📊</div><div style="font-size:.75rem;color:#6B6B6B;">Data analytics</div></div></div>',unsafe_allow_html=True)


def page_step1():
    hero(); progress_dots(1)
    st.markdown(f"<h3 style='text-align:center;font-family:Cormorant Garamond;font-weight:400;color:#2C2C2C;'>Hello, {st.session_state.name} ✦ Let's start with the basics</h3>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        card_open("🪷 Your Skin Type","How would you describe your skin overall?")
        skin_type=st.radio("",["Normal – balanced, no major issues","Oily – shiny, enlarged pores","Dry – tight, flaky, dull","Combination – oily T-zone, dry cheeks","Sensitive – reacts easily, redness"],key="skin_type_radio",label_visibility="collapsed")
        card_close()
    with col2:
        card_open("📅 Your Age","Skin needs change with age.")
        age=st.slider("Age",13,65,st.session_state.age,label_visibility="collapsed")
        st.markdown(f"<div style='text-align:center;font-size:2rem;color:#7A9E7E;font-family:Cormorant Garamond;'>{age}</div>",unsafe_allow_html=True)
        card_close()
        card_open("🌤 Sun Exposure","Daily time spent outdoors")
        sun=st.radio("",["Mostly indoors","1–2 hours outside","3+ hours outside"],key="sun_radio",label_visibility="collapsed")
        card_close()
    cb,cn=st.columns(2)
    with cb:
        if st.button("← Back",use_container_width=True): st.session_state.step=0; st.rerun()
    with cn:
        if st.button("Next →",use_container_width=True):
            st.session_state.skin_type=skin_type.split(" –")[0]; st.session_state.age=age; st.session_state.sun_exposure=sun; st.session_state.step=2; st.rerun()


def page_step2():
    hero(); progress_dots(2)
    st.markdown("<h3 style='text-align:center;font-family:Cormorant Garamond;font-weight:400;color:#2C2C2C;'>What are your skin concerns?</h3>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6B6B6B;font-size:.88rem;'>Select all that apply — we'll prioritise your top concerns.</p><br>",unsafe_allow_html=True)
    card_open("🔍 Primary Concerns","These drive your product recommendations.")
    concerns_options=[("Acne & Breakouts","🫧"),("Blackheads & Pores","⚫"),("Oiliness","💧"),("Dryness & Flaking","🌵"),("Dullness & Uneven Tone","🌟"),("Dark Spots & Pigmentation","☁️"),("Fine Lines & Wrinkles","🕐"),("Dark Circles","👁"),("Redness & Irritation","🌹"),("Texture Issues","🪨"),("Loss of Firmness","⬆️"),("Sun Damage","☀️")]
    selected=[]
    chunks=[concerns_options[i:i+4] for i in range(0,len(concerns_options),4)]
    for chunk in chunks:
        cols=st.columns(len(chunk))
        for col,(concern,icon) in zip(cols,chunk):
            with col:
                if st.checkbox(f"{icon} {concern}",key=f"concern_{concern}"): selected.append(concern)
    card_close()
    card_open("💆 Sensitivity","Does your skin react to new products?")
    sensitivity=st.radio("",["Not sensitive – I can use almost anything","Mildly sensitive – occasional mild reactions","Quite sensitive – regular redness/stinging","Very sensitive / reactive skin"],key="sensitivity_radio",label_visibility="collapsed")
    card_close()
    cb,cn=st.columns(2)
    with cb:
        if st.button("← Back",use_container_width=True): st.session_state.step=1; st.rerun()
    with cn:
        if st.button("Next →",use_container_width=True):
            if not selected: st.warning("Please select at least one concern.")
            else: st.session_state.concerns=selected; st.session_state.sensitivity=sensitivity.split(" –")[0]; st.session_state.step=3; st.rerun()


def page_step3():
    hero(); progress_dots(3)
    st.markdown("<h3 style='text-align:center;font-family:Cormorant Garamond;font-weight:400;color:#2C2C2C;'>Tell us about your lifestyle</h3>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6B6B6B;font-size:.88rem;'>Lifestyle factors deeply influence skin health.</p><br>",unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        card_open("💧 Water Intake","Daily water consumption")
        water=st.radio("",["Less than 4 glasses","4–6 glasses","7–8 glasses","8+ glasses"],key="water_radio",label_visibility="collapsed")
        card_close()
        card_open("😴 Sleep","Average nightly sleep")
        sleep=st.radio("",["Less than 5 hrs","5–6 hrs","7–8 hrs","8+ hrs"],key="sleep_radio",label_visibility="collapsed")
        card_close()
    with col2:
        card_open("🥗 Diet & Habits","Select all that apply")
        habits=[]
        for h in ["High sugar / junk food diet 🍟","Mostly healthy / balanced diet 🥗","Vegan / plant-based 🌱","Regular smoker 🚬","Regular alcohol drinker 🍷","High stress lifestyle 😓","Exercise 3+ times/week 🏃","Drink lots of caffeine ☕"]:
            if st.checkbox(h,key=f"habit_{h}"): habits.append(h)
        card_close()
    cb,cn=st.columns(2)
    with cb:
        if st.button("← Back",use_container_width=True): st.session_state.step=2; st.rerun()
    with cn:
        if st.button("Next →",use_container_width=True): st.session_state.water_intake=water; st.session_state.lifestyle=habits; st.session_state.step=4; st.rerun()


def page_step4():
    hero(); progress_dots(4)
    st.markdown("<h3 style='text-align:center;font-family:Cormorant Garamond;font-weight:400;color:#2C2C2C;'>Almost there! Budget & experience</h3>",unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#6B6B6B;font-size:.88rem;'>We'll match products to your budget — no compromises.</p><br>",unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        card_open("💰 Monthly Skincare Budget","How much can you comfortably spend?")
        budget=st.radio("",["Under ₹500 – drugstore picks","₹500–₹1500 – mid-range","₹1500–₹4000 – premium","₹4000+ – luxury / no limit"],key="budget_radio",label_visibility="collapsed")
        card_close()
    with col2:
        card_open("🧪 Experience Level","What's your current routine like?")
        experience=st.radio("",["Beginner – just cleanser & moisturiser","Intermediate – use serums occasionally","Advanced – consistent multi-step routine","Expert – know my actives well"],key="exp_radio",label_visibility="collapsed")
        card_close()
        card_open("⚗️ Ingredients to Avoid")
        avoid=[]
        for a in ["Fragrance-free only 🌸","No alcohol","No parabens","Vegan/cruelty-free 🐰","No retinol (pregnant/nursing)"]:
            if st.checkbox(a,key=f"avoid_{a}"): avoid.append(a)
        card_close()
    cb,cn=st.columns(2)
    with cb:
        if st.button("← Back",use_container_width=True): st.session_state.step=3; st.rerun()
    with cn:
        if st.button("✨ Get My Routine →",use_container_width=True):
            st.session_state.budget=budget.split(" –")[0]; st.session_state.experience=experience.split(" –")[0]; st.session_state.avoid=avoid; st.session_state.step=5; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# RESULTS PAGE — 5 Tabs
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# RESULTS PAGE — 4 Natural Tabs
# ══════════════════════════════════════════════════════════════════════════════

def _get_eda_df():
    """Load EDA dataset once per session."""
    if "eda_df" not in st.session_state:
        df, source = load_data()
        st.session_state["eda_df"] = df
        st.session_state["eda_source"] = source
    return st.session_state["eda_df"]


def mini_comparison_chart(df, category, current_product):
    """
    Small inline chart comparing top products in a category
    by price and rating. Shown right below a recommended product.
    """
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        # Filter to this category, get top 6 by review count
        cat_df = df[df["category"].str.lower().str.contains(
            category.lower().split("/")[0].strip()[:6], na=False
        )].copy()

        if len(cat_df) < 3:
            # fallback: use tier data
            cat_df = df.copy()

        top = cat_df.nlargest(6, "review_count")[["brand","price","rating","review_count"]].drop_duplicates("brand")
        if len(top) < 2:
            return

        brands  = top["brand"].tolist()
        prices  = top["price"].tolist()
        ratings = top["rating"].tolist()

        # Highlight the recommended brand if present
        recommended_brand = current_product.get("brand","")
        colors_price  = ["#4A7C59" if b == recommended_brand else "#B8D4BC" for b in brands]
        colors_rating = ["#4A7C59" if b == recommended_brand else "#B8D4BC" for b in brands]

        fig = make_subplots(rows=1, cols=2,
            subplot_titles=("Price Comparison (₹)", "Rating Comparison ⭐"),
            horizontal_spacing=0.12)

        fig.add_trace(go.Bar(
            x=brands, y=prices, marker_color=colors_price,
            text=[f"₹{p:,}" for p in prices], textposition="outside",
            showlegend=False, name="Price"
        ), row=1, col=1)

        fig.add_trace(go.Bar(
            x=brands, y=ratings, marker_color=colors_rating,
            text=[f"{r:.1f}" for r in ratings], textposition="outside",
            showlegend=False, name="Rating"
        ), row=1, col=2)

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=240,
            margin=dict(t=35, b=10, l=10, r=10),
            font=dict(family="DM Sans", size=10, color="#6B6B6B"),
            annotations=[
                dict(text="Price Comparison (₹)", x=0.22, xref="paper",
                     y=1.12, yref="paper", showarrow=False,
                     font=dict(size=11, color="#2C2C2C")),
                dict(text="Rating Comparison ⭐", x=0.78, xref="paper",
                     y=1.12, yref="paper", showarrow=False,
                     font=dict(size=11, color="#2C2C2C")),
            ]
        )
        fig.update_annotations(font_size=11)
        for col_i in [1, 2]:
            fig.update_xaxes(tickangle=-30, tickfont_size=9, row=1, col=col_i,
                             showgrid=False)
            fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0",
                             showticklabels=False, row=1, col=col_i)

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        # Small caption
        if recommended_brand in brands:
            rank_price  = sorted(prices)[brands.index(recommended_brand)] 
            pct_cheaper = round((1 - prices[brands.index(recommended_brand)] / max(prices)) * 100)
            st.markdown(f"<p style='font-size:.75rem;color:#9cb89f;margin-top:-.5rem;'>✦ <b>{recommended_brand}</b> highlighted in dark green · Compared against {len(brands)-1} similar brands</p>",
                        unsafe_allow_html=True)
    except Exception:
        pass  # silently skip if plotly not available


def render_product_with_chart(prod, df, show_chart=True):
    """Render a product card + optional mini comparison chart below it."""
    tier_class = {
        "Budget":    "product-tier-budget",
        "Mid-range": "product-tier-midrange",
        "Premium":   "product-tier-premium",
    }.get(prod.get("tier", ""), "")

    nykaa  = prod.get("buy_nykaa", "")
    amazon = prod.get("buy_amazon", "")
    ingr   = prod.get("key_ingredients", [])
    ingr_html = f'<div class="product-ingredients">✦ Key ingredients: {", ".join(ingr)}</div>' if ingr else ""
    buy_html = '<div class="buy-row">'
    if nykaa:  buy_html += f'<a class="buy-btn buy-btn-nykaa"  href="{nykaa}"  target="_blank">🛍 Search on Nykaa</a>'
    if amazon: buy_html += f'<a class="buy-btn buy-btn-amazon" href="{amazon}" target="_blank">📦 Search on Amazon</a>'
    buy_html += "</div>"

    st.markdown(f"""<div class="product-card {tier_class}">
        <div class="product-badge">{prod.get("category","")}</div>
        <div class="product-name">{prod["name"]}</div>
        <div class="product-brand">{prod["brand"]}</div>
        <div class="product-price">{prod["price"]} &nbsp;
            <span style="font-size:.75rem;color:#aaa;background:#f5f5f5;
            padding:2px 8px;border-radius:10px;">{prod.get("tier","")}</span>
        </div>
        <div class="product-why">✦ {prod["why"]}</div>
        {ingr_html}{buy_html}
    </div>""", unsafe_allow_html=True)

    if show_chart:
        with st.expander(f"📊 How does {prod['brand']} compare to other {prod.get('category','')} brands?", expanded=False):
            mini_comparison_chart(df, prod.get("category", ""), prod)


def page_results():
    hero()
    s       = st.session_state
    profile = calculate_skin_profile(s)
    recs    = get_recommendations(s, profile)
    df      = _get_eda_df()

    # ML predictions (used in Tab 4)
    ml_cats, ml_conf, ml_similar = ml_predict_categories(
        s.skin_type, s.concerns, s.budget, s.sensitivity, s.age
    )

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown(f"""<div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-family:'Cormorant Garamond',serif;font-size:2.2rem;
             font-weight:400;color:#2C2C2C;">
            Your GlowIQ Report, {s.name}
        </div>
        <div style="color:#6B6B6B;font-size:.88rem;margin-top:.3rem;">
            {s.skin_type} skin &nbsp;·&nbsp;
            {", ".join(s.concerns[:2])}{" & more" if len(s.concerns)>2 else ""}
            &nbsp;·&nbsp; {s.budget}
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Top metrics ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, (val, lbl) in zip([c1,c2,c3,c4], [
        (f"{profile['score']}/100", "Skin Health Score"),
        (s.skin_type,               "Your Skin Type"),
        (s.concerns[0] if s.concerns else "—", "Top Concern"),
        (f"{len(recs['am_products'])+len(recs['pm_products'])} picks", "Products Curated"),
    ]):
        with col:
            st.markdown(f"""<div class="score-ring">
                <div class="score-number" style="font-size:1.5rem;">{val}</div>
                <div class="score-label">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4 Tabs ───────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "🌅 Your Routine",
        "🛍 Your Products",
        "📊 Market Insights",
        "🤖 Why These?",
    ])

    # ════════════════════════════════════════════════════════════════════════
    # TAB 1 — YOUR ROUTINE  (clean steps, no clutter)
    # ════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            card_open("🌅 Morning Routine",
                      "Follow these steps every morning — order matters.")
            for i, step in enumerate(recs["am_routine"], 1):
                st.markdown(f"""<div class="routine-step">
                    <div class="step-num">{i}</div>
                    <div class="step-text">
                        <b>{step["step"]}</b><br>{step["description"]}
                    </div>
                </div>""", unsafe_allow_html=True)
            card_close()

        with col2:
            card_open("🌙 Evening Routine",
                      "Night is when your skin repairs — don't skip this.")
            for i, step in enumerate(recs["pm_routine"], 1):
                st.markdown(f"""<div class="routine-step">
                    <div class="step-num">{i}</div>
                    <div class="step-text">
                        <b>{step["step"]}</b><br>{step["description"]}
                    </div>
                </div>""", unsafe_allow_html=True)
            card_close()

        # Lifestyle tips inline at bottom of routine
        st.markdown("<br>", unsafe_allow_html=True)
        card_open("💡 Personal Tips for You",
                  "Based on your lifestyle answers")
        for tip in profile["tips"]:
            st.markdown(f'<div class="tip-box">✦ {tip}</div>',
                        unsafe_allow_html=True)
        card_close()

    # ════════════════════════════════════════════════════════════════════════
    # TAB 2 — YOUR PRODUCTS  (cards + inline comparison charts)
    # ════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)

        # Search + filter bar
        col_s, col_f = st.columns([3, 1])
        with col_s:
            search = st.text_input("🔍 Search by name, ingredient or category",
                                   placeholder="e.g. Vitamin C, sunscreen, ceramide...")
        with col_f:
            time_filter = st.selectbox("Show", ["All Products", "AM Only", "PM Only"])

        # Build unique product list
        all_p = recs["am_products"] + recs["pm_products"]
        seen  = set(); unique = []
        for p in all_p:
            if p["name"] not in seen:
                unique.append(p); seen.add(p["name"])

        if search:
            q = search.lower()
            unique = [p for p in unique if
                      q in p["name"].lower() or
                      q in p.get("category","").lower() or
                      any(q in i.lower() for i in p.get("key_ingredients",[]))]

        if time_filter == "AM Only":
            unique = [p for p in unique if "am" in p.get("time",[])]
        elif time_filter == "PM Only":
            unique = [p for p in unique if "pm" in p.get("time",[])]

        st.markdown(f"<p style='color:#9cb89f;font-size:.82rem;'>"
                    f"Showing {len(unique)} product{'s' if len(unique)!=1 else ''} — "
                    f"click the chart button below any product to compare brands</p>",
                    unsafe_allow_html=True)

        # Group products by category for cleaner display
        from collections import defaultdict
        by_cat = defaultdict(list)
        for p in unique:
            by_cat[p.get("category","Other")].append(p)

        for cat, prods in by_cat.items():
            st.markdown(f"<div style='font-family:Cormorant Garamond,serif;"
                        f"font-size:1.3rem;font-weight:500;color:#2C2C2C;"
                        f"margin:1.2rem 0 .5rem;border-bottom:1px solid #E0EBE1;"
                        f"padding-bottom:.3rem;'>{cat}</div>",
                        unsafe_allow_html=True)
            for prod in prods:
                render_product_with_chart(prod, df, show_chart=True)

        if not unique:
            st.info("No products matched your search.")

        # Estimated total cost
        def parse_price(p):
            try: return int(p["price"].replace("₹","").replace(",","").strip())
            except: return 0
        total = sum(parse_price(p) for p in unique)
        st.markdown(f"""<div style="background:#EAF2EB;border-radius:12px;
            padding:1rem 1.5rem;margin-top:1rem;display:flex;
            justify-content:space-between;align-items:center;">
            <div style="font-size:.88rem;color:#5a8a5e;">
                💰 Estimated one-time cost for your full routine
            </div>
            <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;
                 font-weight:600;color:#4A7C59;">₹{total:,}</div>
        </div>""", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # TAB 3 — MARKET INSIGHTS  (magazine style, no "objectives" language)
    # ════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            import plotly.graph_objects as go
            import plotly.express as px

            SAGE       = "#7A9E7E"
            SAGE_LIGHT = "#B8D4BC"
            SAGE_PALE  = "#EAF2EB"

            # ── Story intro ─────────────────────────────────────────────────
            st.markdown(f"""<div style="background:white;border:1px solid #E0EBE1;
                border-radius:16px;padding:1.8rem 2rem;margin-bottom:1.5rem;">
                <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;
                     font-weight:400;color:#2C2C2C;">
                    What does the skincare market actually look like?
                </div>
                <div style="font-size:.88rem;color:#6B6B6B;margin-top:.5rem;line-height:1.7;">
                    We analysed <b>{len(df):,} skincare products</b> across
                    <b>{df['brand'].nunique()} brands</b> and
                    <b>{df['category'].nunique()} categories</b> listed on Nykaa
                    to understand what people are buying, what's actually well-rated,
                    and how your recommendations compare to the broader market.
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Section 1: What sells ───────────────────────────────────────
            st.markdown("### 🔥 What's most popular right now")

            col1, col2 = st.columns(2)

            with col1:
                # Top categories by review volume (proxy for sales)
                cat_reviews = df.groupby("category")["review_count"].sum()\
                                .sort_values(ascending=True).reset_index()
                cat_reviews.columns = ["category","total_reviews"]
                fig = px.bar(
                    cat_reviews, x="total_reviews", y="category",
                    orientation="h",
                    color="total_reviews",
                    color_continuous_scale=[[0, SAGE_LIGHT],[1,"#2D5A3D"]],
                    text=cat_reviews["total_reviews"].apply(
                        lambda x: f"{x/1000:.0f}k"),
                    labels={"total_reviews":"Total Reviews","category":""}
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    title=dict(text="Most Reviewed Categories",
                               font=dict(family="Cormorant Garamond",
                                         size=17, color="#2C2C2C")),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(showgrid=True, gridcolor="#f0f0f0",
                               showticklabels=False),
                    coloraxis_showscale=False,
                    height=350,
                    margin=dict(t=45,b=20,l=120,r=60),
                    font=dict(family="DM Sans", color="#6B6B6B")
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Price segment share
                seg = df["price_segment"].value_counts().reset_index()
                seg.columns = ["segment","count"]
                colors_map = {
                    "Budget (< ₹500)":        "#A8D5B5",
                    "Mid-range (₹500–1500)":  "#7A9E7E",
                    "Premium (₹1500–4000)":   "#4A7C59",
                    "Luxury (₹4000+)":        "#2D5A3D",
                }
                fig = px.pie(
                    seg, names="segment", values="count",
                    color="segment",
                    color_discrete_map=colors_map,
                    hole=0.5
                )
                fig.update_traces(textinfo="label+percent",
                                  textfont_size=10)
                fig.update_layout(
                    title=dict(text="Market Share by Price Range",
                               font=dict(family="Cormorant Garamond",
                                         size=17, color="#2C2C2C")),
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=350,
                    margin=dict(t=45,b=20,l=20,r=20),
                    font=dict(family="DM Sans", color="#6B6B6B")
                )
                st.plotly_chart(fig, use_container_width=True)

            # ── Key insight callout ─────────────────────────────────────────
            budget_pct = round(
                (df["price_segment"]=="Budget (< ₹500)").mean()*100, 0)
            top_cat    = df.groupby("category")["review_count"]\
                           .sum().idxmax()
            st.markdown(f"""<div style="display:flex;gap:1rem;flex-wrap:wrap;
                margin-bottom:1.5rem;">
                <div style="flex:1;min-width:200px;background:#EAF2EB;
                     border-radius:12px;padding:1rem 1.3rem;font-size:.88rem;
                     color:#3d5c40;line-height:1.6;">
                    💡 <b>{budget_pct:.0f}% of skincare products</b> are priced
                    under ₹500 — the Indian market is driven by
                    affordable, accessible products.
                </div>
                <div style="flex:1;min-width:200px;background:#EAF2EB;
                     border-radius:12px;padding:1rem 1.3rem;font-size:.88rem;
                     color:#3d5c40;line-height:1.6;">
                    💡 <b>{top_cat}</b> is the most purchased skincare category,
                    with the highest total customer reviews across all brands.
                </div>
            </div>""", unsafe_allow_html=True)

            # ── Section 2: Does price = quality? ───────────────────────────
            st.markdown("### 💸 Does a higher price mean better quality?")

            col1, col2 = st.columns(2)

            with col1:
                # Avg rating per price segment
                seg_rating = df.groupby("price_segment", observed=True)\
                               ["rating"].mean().reset_index()
                seg_rating.columns = ["segment","avg_rating"]
                fig = px.bar(
                    seg_rating, x="segment", y="avg_rating",
                    color="segment",
                    color_discrete_map=colors_map,
                    text=seg_rating["avg_rating"].round(2),
                    labels={"avg_rating":"Avg Rating","segment":""}
                )
                fig.update_traces(textposition="outside")
                fig.update_layout(
                    title=dict(text="Average Rating by Price Segment",
                               font=dict(family="Cormorant Garamond",
                                         size=17, color="#2C2C2C")),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[3.5,5.0], showgrid=True,
                               gridcolor="#f0f0f0"),
                    xaxis=dict(tickangle=-15, showgrid=False),
                    showlegend=False,
                    height=350,
                    margin=dict(t=45,b=70,l=40,r=20),
                    font=dict(family="DM Sans", color="#6B6B6B")
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Scatter: price vs rating coloured by tier
                df_plot = df[df["price"] < 8000].copy()
                fig = px.scatter(
                    df_plot, x="price", y="rating",
                    color="tier",
                    color_discrete_map={
                        "Budget":   SAGE_LIGHT,
                        "Mid-range": SAGE,
                        "Premium":  "#4A7C59"
                    },
                    size="review_count", size_max=20,
                    opacity=0.7,
                    labels={"price":"Price (₹)","rating":"Rating","tier":"Tier"},
                    hover_data=["brand","product_name"]
                )
                fig.update_layout(
                    title=dict(text="Price vs Rating — Each Dot is a Product",
                               font=dict(family="Cormorant Garamond",
                                         size=17, color="#2C2C2C")),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(range=[0.8,5.2], showgrid=True,
                               gridcolor="#f0f0f0"),
                    xaxis=dict(showgrid=False),
                    legend=dict(title="Tier"),
                    height=350,
                    margin=dict(t=45,b=40,l=40,r=20),
                    font=dict(family="DM Sans", color="#6B6B6B")
                )
                st.plotly_chart(fig, use_container_width=True)

            corr = round(df["price"].corr(df["rating"]), 2)
            verdict = "weakly positive" if corr > 0 else "weakly negative"
            st.markdown(f"""<div style="background:#EAF2EB;border-left:4px solid
                {SAGE};border-radius:0 12px 12px 0;padding:1rem 1.5rem;
                font-size:.88rem;color:#3d5c40;line-height:1.8;
                margin-bottom:1.5rem;">
                📌 <b>Verdict:</b> The correlation between price and rating is
                <b>{verdict} ({corr:+.2f})</b>. Expensive products are
                <i>slightly</i> better rated on average — but many budget products
                outperform luxury ones. <b>Price alone is not a reliable
                indicator of quality.</b>
            </div>""", unsafe_allow_html=True)

            # ── Section 3: Brand landscape ──────────────────────────────────
            # ── Section 4: Your skin concern in the market ──────────────────
            st.markdown("### 🎯 How popular is your skin concern?")

            concern_counts = df["skin_concern"].value_counts().reset_index()
            concern_counts.columns = ["concern","products"]

            # Highlight user's concerns
            user_concerns_short = [c.split(" &")[0].split("/")[0]
                                   for c in s.concerns]
            bar_colors = []
            for c in concern_counts["concern"]:
                matched = any(uc.lower() in c.lower()
                              for uc in user_concerns_short)
                bar_colors.append("#4A7C59" if matched else SAGE_LIGHT)

            fig = go.Figure(go.Bar(
                x=concern_counts["concern"],
                y=concern_counts["products"],
                marker_color=bar_colors,
                text=concern_counts["products"],
                textposition="outside"
            ))
            fig.update_layout(
                title=dict(
                    text="Products Available per Skin Concern "
                         "(dark green = your concerns)",
                    font=dict(family="Cormorant Garamond",
                              size=17, color="#2C2C2C")
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickangle=-25, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                height=370,
                margin=dict(t=50,b=100,l=40,r=20),
                font=dict(family="DM Sans", color="#6B6B6B")
            )
            st.plotly_chart(fig, use_container_width=True)

        except ImportError:
            st.warning("Install plotly to see charts: `pip install plotly`")

    # ════════════════════════════════════════════════════════════════════════
    # TAB 4 — WHY THESE? (ML explanation — kept clean from before)
    # ════════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""<div class="section-card">
            <div class="section-title">🤖 Why did you get these recommendations?</div>
            <div class="section-sub">
                The ML model compared your profile against 600 similar skin
                profiles to decide what <i>you specifically</i> need.
            </div>
            <p style="font-size:.9rem;color:#444;line-height:1.9;">
                The model found <b>{len(ml_similar)} people with skin similar
                to yours</b> — same skin type, similar concerns and budget.
                It looked at what product categories helped the majority of
                them, and recommended those same categories for you.
            </p>
            <div style="background:#EAF2EB;border-radius:10px;padding:.8rem
                 1.2rem;font-size:.85rem;color:#5a8a5e;">
                ✦ Think of it like asking 9 people who have the same skin as
                you: <i>"What actually worked for you?"</i> — and following
                the majority answer.
            </div>
        </div>""", unsafe_allow_html=True)

        def ml_reason(category, conf, st2):
            skin     = st2.skin_type
            concerns = st2.concerns
            age      = st2.age
            votes    = max(1, round(conf / 100 * 9))
            reasons  = {
                "Cleanser": f"{votes}/9 similar profiles used a gentle cleanser daily. Cleansing is non-negotiable for {skin} skin — it removes pollution, sunscreen, and sebum that block pores.",
                "Toner / Exfoliant": f"{votes}/9 profiles benefited from a toner. {'Your oily skin produces excess sebum — a toner rebalances pH and keeps pores clear.' if skin in ['Oily','Combination'] else 'A hydrating toner adds moisture before your serum.'}",
                "Exfoliant": f"{votes}/9 profiles used chemical exfoliation. {'Blackheads respond best to BHA acids that dissolve dead-skin plugs inside pores.' if 'Blackheads & Pores' in concerns else 'Regular exfoliation removes dull cells that block other products from absorbing.'}",
                "Vitamin C Serum": f"{votes}/9 profiles used Vitamin C. {'Dark spots are caused by excess melanin — Vitamin C directly blocks melanin production.' if 'Dark Spots & Pigmentation' in concerns else 'Vitamin C protects against UV and pollution damage that causes premature ageing.'}",
                "Niacinamide Serum": f"{votes}/9 profiles with {skin} skin used niacinamide. {'It reduces sebum at the source — recommended for your oily skin and breakout concerns.' if skin in ['Oily','Combination'] else 'Niacinamide fades dark spots, strengthens the barrier, and reduces redness.'}",
                "Retinol Serum": f"{votes}/9 profiles at age {age}+ used retinol. {'Fine lines respond to retinol, which speeds cell turnover.' if age >= 26 or 'Fine Lines & Wrinkles' in concerns else 'Starting retinol now builds long-term resistance to ageing.'}",
                "Hydrating Serum": f"{votes}/9 profiles with {skin} skin needed extra hydration. {'Dry skin lacks lipids to retain moisture — hyaluronic acid fills that gap.' if skin in ['Dry','Sensitive'] else 'Even oily skin can be dehydrated. A water-based serum hydrates without adding grease.'}",
                "Eye Treatment": f"{votes}/9 profiles needed an eye treatment. {'Dark circles signal poor micro-circulation — caffeine products directly target this.' if 'Dark Circles' in concerns else f'The eye area shows ageing first — protecting it at age {age} prevents visible damage later.'}",
                "Moisturiser": f"9/9 — every profile used a moisturiser. All skin types need one.",
                "Sunscreen": f"9/9 — every profile needs SPF. Sunscreen is the most evidence-backed anti-ageing product. {'Your dark spots will worsen without SPF — UV triggers melanin production.' if 'Dark Spots & Pigmentation' in concerns else 'UV is the #1 cause of premature ageing.'}",
                "Spot Treatment": f"{votes}/9 profiles with acne used a spot treatment. It kills acne bacteria at the source faster than any full-face product.",
                "Face Mask": f"{votes}/9 profiles used a weekly mask for a deeper treatment than daily routine can provide.",
            }
            return reasons.get(category,
                f"{votes}/9 people with similar skin found this effective.")

        # ── Recommended categories ───────────────────────────────────────────
        st.markdown("### ✅ Why the model chose each product type for you")
        all_rec_prods = recs["am_products"] + recs["pm_products"]
        seen_cat_names = set()
        rec_categories = []
        for p in all_rec_prods:
            cat     = p.get("category","")
            cat_key = cat.split("/")[0].strip()
            if cat_key not in seen_cat_names:
                rec_categories.append(
                    (cat, ml_conf.get(cat_key, ml_conf.get(cat, 70))))
                seen_cat_names.add(cat_key)

        for cat, conf in rec_categories:
            votes       = max(1, round(conf / 100 * 9))
            reason_text = ml_reason(cat, conf, s)
            st.markdown(f"""<div style="background:white;border:1px solid
                #E0EBE1;border-radius:14px;padding:1.2rem 1.5rem;
                margin-bottom:.9rem;border-left:4px solid #7A9E7E;">
                <div style="display:flex;justify-content:space-between;
                     align-items:center;margin-bottom:.5rem;">
                    <div style="font-family:'Cormorant Garamond',serif;
                         font-size:1.15rem;font-weight:600;color:#2C2C2C;">
                        ✅ {cat}
                    </div>
                    <div style="background:#EAF2EB;color:#7A9E7E;
                         border-radius:20px;padding:.2rem .8rem;
                         font-size:.78rem;font-weight:600;">
                        {votes}/9 similar users
                    </div>
                </div>
                <div style="background:#eee;border-radius:4px;height:6px;
                     margin-bottom:.7rem;">
                    <div style="width:{conf}%;background:#7A9E7E;
                         border-radius:4px;height:6px;"></div>
                </div>
                <div style="font-size:.85rem;color:#555;line-height:1.6;">
                    💬 {reason_text}
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Not recommended ──────────────────────────────────────────────────
        st.markdown("### ❌ What the model decided you don't need right now")
        not_recommended = {
            "Retinol Serum":     f"Only {round(ml_conf.get('Retinol Serum',20)/100*9)}/9 similar profiles needed retinol at age {s.age}. Powerful — starting without skin prep causes irritation without benefit.",
            "Spot Treatment":    f"Only {round(ml_conf.get('Spot Treatment',20)/100*9)}/9 profiles needed a spot treatment. Active acne isn't your primary concern.",
            "Eye Treatment":     f"Only {round(ml_conf.get('Eye Treatment',20)/100*9)}/9 profiles at your age needed an eye treatment. Other concerns are higher priority.",
            "Exfoliant":         f"Only {round(ml_conf.get('Exfoliant',20)/100*9)}/9 profiles used a chemical exfoliant. For your sensitivity level, this can compromise your barrier.",
            "Toner / Exfoliant": f"Only {round(ml_conf.get('Toner / Exfoliant',20)/100*9)}/9 profiles used a toner at the beginner stage.",
            "Vitamin C Serum":   f"Only {round(ml_conf.get('Vitamin C Serum',20)/100*9)}/9 profiles prioritised Vitamin C — hydration or acne control comes first for you.",
            "Face Mask":         f"Only {round(ml_conf.get('Face Mask',20)/100*9)}/9 profiles used a weekly mask. Your daily routine covers the essentials.",
        }
        skipped = [(c, r) for c, r in not_recommended.items()
                   if c not in seen_cat_names]
        for cat, reason in skipped[:4]:
            votes = max(0, round(ml_conf.get(cat, 20) / 100 * 9))
            st.markdown(f"""<div style="background:white;border:1px solid
                #E0EBE1;border-radius:14px;padding:1.1rem 1.5rem;
                margin-bottom:.8rem;border-left:4px solid #ddd;opacity:.8;">
                <div style="display:flex;justify-content:space-between;
                     align-items:center;">
                    <div style="font-family:'Cormorant Garamond',serif;
                         font-size:1.05rem;font-weight:500;color:#999;">
                        ❌ {cat}
                    </div>
                    <div style="background:#f5f5f5;color:#bbb;
                         border-radius:20px;padding:.2rem .8rem;
                         font-size:.75rem;">{votes}/9 similar users</div>
                </div>
                <div style="font-size:.83rem;color:#bbb;margin-top:.4rem;
                     line-height:1.5;">💬 {reason}</div>
            </div>""", unsafe_allow_html=True)

        # ── Similar profiles ─────────────────────────────────────────────────
        st.markdown("### 👥 The 9 people the model compared you to")
        cols = st.columns(3)
        skin_emojis = {"Oily":"💧","Dry":"🌵","Combination":"🌓",
                       "Sensitive":"🌹","Normal":"✨"}
        for i, sim in enumerate(ml_similar):
            with cols[i % 3]:
                emoji   = skin_emojis.get(sim["skin_type"], "🧴")
                match   = sim["similarity"]
                bar_col = "#7A9E7E" if match >= 70 else "#B8D4BC"
                st.markdown(f"""<div style="background:white;border:1px solid
                    #E0EBE1;border-radius:12px;padding:1rem;
                    margin-bottom:.8rem;text-align:center;">
                    <div style="font-size:1.8rem;">{emoji}</div>
                    <div style="font-family:'Cormorant Garamond',serif;
                         font-size:1rem;font-weight:600;margin:.3rem 0;">
                         {sim['skin_type']} skin</div>
                    <div style="font-size:.78rem;color:#6B6B6B;">
                        Age ~{sim['age']}</div>
                    <div style="background:#eee;border-radius:4px;
                         height:5px;margin:.6rem 0;">
                        <div style="width:{match}%;background:{bar_col};
                             border-radius:4px;height:5px;"></div>
                    </div>
                    <div style="font-size:.75rem;color:#7A9E7E;font-weight:600;">
                        {match:.0f}% match to you</div>
                </div>""", unsafe_allow_html=True)

    # ── Retake button ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🔄 Retake Quiz", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
# ── Router ────────────────────────────────────────────────────────────────────
step = st.session_state.step
if   step==0: page_landing()
elif step==1: page_step1()
elif step==2: page_step2()
elif step==3: page_step3()
elif step==4: page_step4()
elif step==5: page_results()
