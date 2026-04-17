import streamlit as st
import json
from recommend import get_recommendations, calculate_skin_profile
from products import PRODUCT_DATABASE
from ml_model import ml_predict_categories, get_model_accuracy_report, CATEGORY_LABELS

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
def page_results():
    hero()
    s = st.session_state
    profile = calculate_skin_profile(s)
    recs    = get_recommendations(s, profile)

    # ── Run ML model ──
    ml_cats, ml_conf, ml_similar = ml_predict_categories(
        s.skin_type, s.concerns,
        s.budget, s.sensitivity, s.age
    )

    # ── Header ──
    st.markdown(f'''<div style="text-align:center;margin-bottom:1.5rem;">
        <div style="font-family:Cormorant Garamond;font-size:2.2rem;font-weight:400;color:#2C2C2C;">Your GlowIQ Report, {s.name}</div>
        <div style="color:#6B6B6B;font-size:.88rem;margin-top:.3rem;">
            Personalised for {s.skin_type} skin · {", ".join(s.concerns[:2])}{" and more" if len(s.concerns)>2 else ""}
            <span class="ml-badge">🤖 ML-enhanced</span>
        </div></div>''', unsafe_allow_html=True)

    # ── Top metrics ──
    c1,c2,c3,c4=st.columns(4)
    for col,(val,lbl) in zip([c1,c2,c3,c4],[
        (f"{profile['score']}/100","Skin Score"),
        (s.skin_type,"Skin Type"),
        (s.concerns[0] if s.concerns else "—","Top Concern"),
        (s.budget.replace("Under ",""),"Budget Tier"),
    ]):
        with col:
            st.markdown(f'<div class="score-ring"><div class="score-number" style="font-size:1.5rem;">{val}</div><div class="score-label">{lbl}</div></div>',unsafe_allow_html=True)

    st.markdown("<br>",unsafe_allow_html=True)

    # ── 5 Tabs ──
    tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "🌅 AM Routine", "🌙 PM Routine", "🛍 All Products",
        "🤖 ML Insights", "📊 Data Analytics"
    ])

    # ─── TAB 1: AM ───────────────────────────────────────────────────────────
    with tab1:
        st.markdown("<br>",unsafe_allow_html=True)
        card_open("Morning Routine","Complete these steps every morning for best results.")
        for i,step in enumerate(recs["am_routine"],1):
            st.markdown(f'<div class="routine-step"><div class="step-num">{i}</div><div class="step-text"><b>{step["step"]}</b><br>{step["description"]}</div></div>',unsafe_allow_html=True)
        card_close()
        st.markdown("#### 🌅 Recommended AM Products")
        for p in recs["am_products"]: render_product_card(p)

    # ─── TAB 2: PM ───────────────────────────────────────────────────────────
    with tab2:
        st.markdown("<br>",unsafe_allow_html=True)
        card_open("Evening Routine","Night is when skin repairs itself — don't skip this.")
        for i,step in enumerate(recs["pm_routine"],1):
            st.markdown(f'<div class="routine-step"><div class="step-num">{i}</div><div class="step-text"><b>{step["step"]}</b><br>{step["description"]}</div></div>',unsafe_allow_html=True)
        card_close()
        st.markdown("#### 🌙 Recommended PM Products")
        for p in recs["pm_products"]: render_product_card(p)

    # ─── TAB 3: ALL PRODUCTS ─────────────────────────────────────────────────
    with tab3:
        st.markdown("<br>",unsafe_allow_html=True)
        search=st.text_input("🔍 Search products",placeholder="e.g. Vitamin C, Niacinamide, moisturiser...")
        tier_filter=st.selectbox("Filter by budget tier",["All Tiers","Budget","Mid-range","Premium"])
        all_p=recs["am_products"]+recs["pm_products"]
        seen=set(); unique=[]
        for p in all_p:
            if p["name"] not in seen: unique.append(p); seen.add(p["name"])
        if search: unique=[p for p in unique if search.lower() in p["name"].lower() or search.lower() in p.get("category","").lower() or any(search.lower() in i.lower() for i in p.get("key_ingredients",[]))]
        if tier_filter!="All Tiers": unique=[p for p in unique if p.get("tier")==tier_filter]
        st.markdown(f"<p style='color:#6B6B6B;font-size:.85rem;'>{len(unique)} products found</p>",unsafe_allow_html=True)
        for p in unique: render_product_card(p)
        if not unique: st.info("No products matched your search.")

    # ─── TAB 4: ML INSIGHTS ──────────────────────────────────────────────────
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)

        # Plain-English intro
        st.markdown(f"""<div class="section-card">
            <div class="section-title">🤖 Why did you get these recommendations?</div>
            <div class="section-sub">The ML model compared your profile to 600 similar skin profiles to decide what <i>you specifically</i> need — and what you don't.</div>
            <p style="font-size:.9rem;color:#444;line-height:1.9;">
            The model found <b>{len(ml_similar)} people with skin similar to yours</b> — same skin type, similar concerns and budget.
            It then looked at what product categories helped the majority of them, and recommended those for you.
            </p>
            <div style="background:#EAF2EB;border-radius:10px;padding:.8rem 1.2rem;font-size:.85rem;color:#5a8a5e;">
            ✦ Think of it like asking 9 people who have the same skin as you: <i>"What actually worked for you?"</i> — and following the majority answer.
            </div>
        </div>""", unsafe_allow_html=True)

        # Why each product category was recommended
        st.markdown("### ✅ Why the model recommended each product type for you")

        all_rec_prods = recs["am_products"] + recs["pm_products"]

        def ml_reason(category, conf, st2):
            skin = st2.skin_type
            concerns = st2.concerns
            age = st2.age
            votes = max(1, round(conf / 100 * 9))
            reasons = {
                "Cleanser": f"{votes}/9 similar profiles used a gentle cleanser daily. Cleansing is non-negotiable for {skin} skin — it removes pollution, sunscreen, and sebum that block pores.",
                "Toner / Exfoliant": f"{votes}/9 profiles benefited from a toner. {'Your oily skin produces excess sebum — a toner rebalances pH and keeps pores clear.' if skin in ['Oily','Combination'] else 'A hydrating toner adds moisture before your serum, which your dry skin needs.'}",
                "Exfoliant": f"{votes}/9 profiles with your concerns used chemical exfoliation. {'Blackheads respond best to BHA acids that dissolve dead-skin plugs inside pores.' if 'Blackheads & Pores' in concerns else 'Regular exfoliation removes dull cells that block other products from absorbing properly.'}",
                "Vitamin C Serum": f"{votes}/9 similar profiles used a Vitamin C serum. {'Dark spots are caused by excess melanin — Vitamin C directly blocks melanin production.' if 'Dark Spots & Pigmentation' in concerns or 'Dullness & Uneven Tone' in concerns else 'Vitamin C protects against UV and pollution damage that causes premature ageing.'}",
                "Niacinamide Serum": f"{votes}/9 profiles with {skin} skin used niacinamide. {'Niacinamide reduces sebum at the source — recommended for your oily skin and breakout concerns.' if skin in ['Oily','Combination'] or 'Acne & Breakouts' in concerns else 'Niacinamide fades dark spots, strengthens the barrier, and reduces redness simultaneously.'}",
                "Retinol Serum": f"{votes}/9 profiles at age {age}+ used retinol. {'Fine lines respond to retinol, which speeds cell turnover. Your age group benefits most from starting now.' if age >= 26 or 'Fine Lines & Wrinkles' in concerns else 'Starting retinol at a low dose now builds long-term resistance to ageing.'}",
                "Hydrating Serum": f"{votes}/9 profiles with {skin} skin needed extra hydration. {'Dry skin lacks lipids to retain moisture — hyaluronic acid fills that gap from within skin layers.' if skin in ['Dry','Sensitive'] or 'Dryness & Flaking' in concerns else 'Even oily skin can be dehydrated. A water-based serum hydrates without adding grease.'}",
                "Eye Treatment": f"{votes}/9 similar profiles needed an eye treatment. {'Dark circles signal poor micro-circulation under the eye — caffeine products directly target this.' if 'Dark Circles' in concerns else f'The eye area has thinner skin that shows ageing first — protecting it at age {age} prevents visible damage later.'}",
                "Moisturiser": f"9/9 — every profile used a moisturiser. All skin types need one. {'For {skin} skin, a lightweight gel formula hydrates without adding shine.' if skin in ['Oily','Combination'] else 'For {skin} skin, a cream-based formula seals in hydration and repairs the barrier.'}",
                "Sunscreen": f"9/9 — every profile needs SPF. Sunscreen is the most evidence-backed anti-ageing product. {'Your dark spots will not improve without daily SPF — UV triggers melanin that makes them worse.' if 'Dark Spots & Pigmentation' in concerns or 'Sun Damage' in concerns else 'UV is the #1 cause of premature ageing and dark spots — there is no substitute.'}",
                "Spot Treatment": f"{votes}/9 profiles with acne concerns used a spot treatment. It kills acne bacteria at the source — faster than any full-face product.",
                "Face Mask": f"{votes}/9 profiles used a weekly mask. It gives your skin a deeper treatment than daily routine can — clearing buildup or hydrating intensely depending on your skin type.",
            }
            return reasons.get(category, f"{votes}/9 people with similar skin found this category effective for their concerns.")

        seen_cat_names = set()
        rec_categories = []
        for p in all_rec_prods:
            cat = p.get("category", "")
            cat_key = cat.split("/")[0].strip()
            if cat_key not in seen_cat_names:
                rec_categories.append((cat, ml_conf.get(cat_key, ml_conf.get(cat, 70))))
                seen_cat_names.add(cat_key)
        for ml_cat in ml_cats:
            if ml_cat not in seen_cat_names:
                rec_categories.append((ml_cat, ml_conf.get(ml_cat, 70)))
                seen_cat_names.add(ml_cat)

        for cat, conf in rec_categories:
            votes = max(1, round(conf / 100 * 9))
            reason_text = ml_reason(cat, conf, s)
            st.markdown(f"""<div style="background:white;border:1px solid #E0EBE1;border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:.9rem;border-left:4px solid #7A9E7E;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.5rem;">
                    <div style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;font-weight:600;color:#2C2C2C;">✅ {cat}</div>
                    <div style="background:#EAF2EB;color:#7A9E7E;border-radius:20px;padding:.2rem .8rem;font-size:.78rem;font-weight:600;">{votes}/9 similar users</div>
                </div>
                <div style="background:#eee;border-radius:4px;height:6px;margin-bottom:.7rem;">
                    <div style="width:{conf}%;background:#7A9E7E;border-radius:4px;height:6px;"></div>
                </div>
                <div style="font-size:.85rem;color:#555;line-height:1.6;">💬 {reason_text}</div>
            </div>""", unsafe_allow_html=True)

        # What was NOT recommended
        st.markdown("### ❌ What the model decided you don't need right now")

        not_recommended = {
            "Retinol Serum": f"Only {round(ml_conf.get('Retinol Serum',20)/100*9)}/9 similar profiles needed retinol at age {s.age}. It's powerful — starting without the right skin prep can irritate without benefit.",
            "Spot Treatment": f"Only {round(ml_conf.get('Spot Treatment',20)/100*9)}/9 profiles needed a spot treatment. Since active acne isn't your primary concern, it would be unnecessary.",
            "Eye Treatment": f"Only {round(ml_conf.get('Eye Treatment',20)/100*9)}/9 profiles at your age needed an eye treatment. Your other concerns are higher priority right now.",
            "Exfoliant": f"Only {round(ml_conf.get('Exfoliant',20)/100*9)}/9 profiles used a chemical exfoliant. For your sensitivity level, starting exfoliation too soon can compromise your skin barrier.",
            "Toner / Exfoliant": f"Only {round(ml_conf.get('Toner / Exfoliant',20)/100*9)}/9 profiles used a toner. At the beginner stage, adding a toner before mastering the basics can overcomplicate your routine.",
            "Vitamin C Serum": f"Only {round(ml_conf.get('Vitamin C Serum',20)/100*9)}/9 profiles with your concerns prioritised Vitamin C. Hydration or acne control takes precedence first.",
            "Face Mask": f"Only {round(ml_conf.get('Face Mask',20)/100*9)}/9 similar profiles used a weekly mask. Your daily routine covers the essentials — a mask is optional at this stage.",
        }

        skipped = [(cat, reason) for cat, reason in not_recommended.items() if cat not in seen_cat_names]
        if not skipped:
            st.markdown("<p style='color:#6B6B6B;font-size:.88rem;'>The model recommended a broad set of categories for your profile — great news!</p>", unsafe_allow_html=True)
        for cat, reason in skipped[:4]:
            votes = max(0, round(ml_conf.get(cat, 20) / 100 * 9))
            st.markdown(f"""<div style="background:white;border:1px solid #E0EBE1;border-radius:14px;padding:1.2rem 1.5rem;margin-bottom:.9rem;border-left:4px solid #ddd;opacity:.85;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;">
                    <div style="font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:500;color:#888;">❌ {cat}</div>
                    <div style="background:#f5f5f5;color:#999;border-radius:20px;padding:.2rem .8rem;font-size:.78rem;">{votes}/9 similar users</div>
                </div>
                <div style="font-size:.85rem;color:#999;line-height:1.6;">💬 {reason}</div>
            </div>""", unsafe_allow_html=True)

        # People like you
        st.markdown("### 👥 The 9 people the model compared you to")
        st.markdown("<p style='color:#6B6B6B;font-size:.85rem;margin-bottom:1rem;'>These are the most similar skin profiles found in our training data. Their outcomes shaped your recommendations.</p>", unsafe_allow_html=True)
        cols = st.columns(3)
        skin_emojis = {"Oily":"💧","Dry":"🌵","Combination":"🌓","Sensitive":"🌹","Normal":"✨"}
        for i, sim in enumerate(ml_similar):
            with cols[i % 3]:
                emoji = skin_emojis.get(sim["skin_type"], "🧴")
                match = sim["similarity"]
                bar_col = "#7A9E7E" if match >= 70 else "#B8D4BC"
                st.markdown(f"""<div style="background:white;border:1px solid #E0EBE1;border-radius:12px;padding:1rem;margin-bottom:.8rem;text-align:center;">
                    <div style="font-size:1.8rem;">{emoji}</div>
                    <div style="font-family:'Cormorant Garamond',serif;font-size:1rem;font-weight:600;margin:.3rem 0;">{sim['skin_type']} skin</div>
                    <div style="font-size:.78rem;color:#6B6B6B;">Age ~{sim['age']}</div>
                    <div style="background:#eee;border-radius:4px;height:5px;margin:.6rem 0;">
                        <div style="width:{match}%;background:{bar_col};border-radius:4px;height:5px;"></div>
                    </div>
                    <div style="font-size:.75rem;color:#7A9E7E;font-weight:600;">{match:.0f}% match to you</div>
                </div>""", unsafe_allow_html=True)


    # ─── TAB 5: DATA ANALYTICS ───────────────────────────────────────────────
    with tab5:
        st.markdown("<br>",unsafe_allow_html=True)
        try:
            import plotly.graph_objects as go
            import plotly.express as px

            sage = "#7A9E7E"
            sage_light = "#B8D4BC"
            sage_pale = "#EAF2EB"
            colors_tier = {"Budget":"#A8D5B5","Mid-range":"#7A9E7E","Premium":"#4A7C59"}

            # ── Chart 1: Concern Priority Radar ──────────────────────────────
            all_concerns_list = ["Acne & Breakouts","Blackheads & Pores","Oiliness","Dryness & Flaking",
                "Dullness & Uneven Tone","Dark Spots & Pigmentation","Fine Lines & Wrinkles",
                "Dark Circles","Redness & Irritation","Texture Issues","Loss of Firmness","Sun Damage"]
            concern_scores = [3 if c in s.concerns else 0 for c in all_concerns_list]

            fig_radar = go.Figure(go.Scatterpolar(
                r=concern_scores + [concern_scores[0]],
                theta=all_concerns_list + [all_concerns_list[0]],
                fill='toself',
                line_color=sage,
                fillcolor=sage_pale,
                name="Your Concerns"
            ))
            fig_radar.update_layout(
                title=dict(text="Your Skin Concern Profile", font=dict(family="Cormorant Garamond",size=20,color="#2C2C2C"), x=0.5),
                polar=dict(radialaxis=dict(visible=True,range=[0,3],showticklabels=False),
                           bgcolor=sage_pale,
                           angularaxis=dict(tickfont=dict(size=11,family="DM Sans"))),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False, height=420,
                margin=dict(t=60,b=20,l=80,r=80)
            )

            # ── Chart 2: ML Confidence Bar Chart ─────────────────────────────
            cats = list(ml_conf.keys())
            confs = list(ml_conf.values())
            bar_colors = [sage if v>=50 else sage_light for v in confs]

            fig_conf = go.Figure(go.Bar(
                x=confs, y=cats, orientation='h',
                marker_color=bar_colors,
                text=[f"{v:.0f}%" for v in confs],
                textposition='outside',
                hovertemplate="%{y}: %{x:.1f}%<extra></extra>"
            ))
            fig_conf.update_layout(
                title=dict(text="ML Model Confidence per Product Category", font=dict(family="Cormorant Garamond",size=20,color="#2C2C2C"), x=0.5),
                xaxis=dict(title="Confidence (%)", range=[0,120], showgrid=True, gridcolor="#eee"),
                yaxis=dict(autorange="reversed"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=420, margin=dict(t=60,b=40,l=160,r=60),
                font=dict(family="DM Sans",color="#6B6B6B")
            )

            # ── Chart 3: Budget Distribution Pie ─────────────────────────────
            all_prods = []
            for cat_prods in PRODUCT_DATABASE.values():
                all_prods.extend(cat_prods)
            tier_counts = {}
            for p in all_prods:
                t = p.get("tier","Budget")
                tier_counts[t] = tier_counts.get(t,0)+1

            fig_pie = go.Figure(go.Pie(
                labels=list(tier_counts.keys()),
                values=list(tier_counts.values()),
                marker_colors=[colors_tier.get(t,"#ccc") for t in tier_counts.keys()],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate="%{label}: %{value} products<extra></extra>"
            ))
            fig_pie.update_layout(
                title=dict(text="Product Database — Budget Distribution", font=dict(family="Cormorant Garamond",size=20,color="#2C2C2C"), x=0.5),
                paper_bgcolor="rgba(0,0,0,0)",
                height=360, margin=dict(t=60,b=20,l=20,r=20),
                font=dict(family="DM Sans",color="#6B6B6B"),
                showlegend=True
            )

            # ── Chart 4: Product Category Breakdown ──────────────────────────
            cat_counts = {}
            for p in all_prods:
                c = p.get("category","Other")
                cat_counts[c] = cat_counts.get(c,0)+1
            cat_counts = dict(sorted(cat_counts.items(),key=lambda x:x[1],reverse=True))

            fig_cat = go.Figure(go.Bar(
                x=list(cat_counts.keys()),
                y=list(cat_counts.values()),
                marker_color=sage,
                text=list(cat_counts.values()),
                textposition='outside',
            ))
            fig_cat.update_layout(
                title=dict(text="Products per Category in Database", font=dict(family="Cormorant Garamond",size=20,color="#2C2C2C"), x=0.5),
                xaxis=dict(tickangle=-30, tickfont=dict(size=11)),
                yaxis=dict(title="Count", showgrid=True, gridcolor="#eee"),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=380, margin=dict(t=60,b=100,l=40,r=20),
                font=dict(family="DM Sans",color="#6B6B6B")
            )

            # ── Chart 5: Skin Score Gauge ─────────────────────────────────────
            score = profile["score"]
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score,
                delta={"reference":70,"increasing":{"color":sage},"decreasing":{"color":"#e76f51"}},
                gauge={
                    "axis":{"range":[0,100],"tickwidth":1},
                    "bar":{"color":sage,"thickness":0.3},
                    "bgcolor":"white",
                    "steps":[
                        {"range":[0,40],"color":"#fde8e8"},
                        {"range":[40,65],"color":"#fff3e0"},
                        {"range":[65,80],"color":sage_pale},
                        {"range":[80,100],"color":"#d4edda"},
                    ],
                    "threshold":{"line":{"color":"#4A7C59","width":4},"thickness":0.75,"value":score}
                },
                title={"text":f"Your Skin Health Score<br><span style='font-size:.8em;color:#6B6B6B'>Based on lifestyle factors</span>", "font":{"family":"Cormorant Garamond","size":20}}
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=320,
                margin=dict(t=60,b=20,l=40,r=40),
                font=dict(family="DM Sans",color="#2C2C2C")
            )

            # ── Render all charts ─────────────────────────────────────────────
            st.markdown("### 📊 Your Personalised Analytics Dashboard")

            col1, col2 = st.columns(2)
            with col1: st.plotly_chart(fig_gauge, use_container_width=True)
            with col2: st.plotly_chart(fig_pie, use_container_width=True)

            st.plotly_chart(fig_radar, use_container_width=True)
            st.plotly_chart(fig_conf, use_container_width=True)
            st.plotly_chart(fig_cat, use_container_width=True)

            # ── Summary stats ─────────────────────────────────────────────────
            st.markdown("### 📋 Routine Summary")
            am_p = recs["am_products"]; pm_p = recs["pm_products"]
            all_rec = am_p + pm_p
            seen_s = set(); all_rec_u = []
            for p in all_rec:
                if p["name"] not in seen_s: all_rec_u.append(p); seen_s.add(p["name"])

            def parse_price(p):
                try: return int(p.replace("₹","").replace(",","").strip())
                except: return 0

            total_cost = sum(parse_price(p["price"]) for p in all_rec_u)
            tier_dist = {}
            for p in all_rec_u: tier_dist[p.get("tier","Budget")] = tier_dist.get(p.get("tier","Budget"),0)+1

            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(f'<div class="stat-box"><div class="stat-number">{len(all_rec_u)}</div><div class="stat-label">Products Recommended</div></div>',unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-box"><div class="stat-number">₹{total_cost:,}</div><div class="stat-label">Est. Total Cost</div></div>',unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-box"><div class="stat-number">{len(recs["am_routine"])}</div><div class="stat-label">AM Routine Steps</div></div>',unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="stat-box"><div class="stat-number">{len(recs["pm_routine"])}</div><div class="stat-label">PM Routine Steps</div></div>',unsafe_allow_html=True)

        except ImportError:
            st.warning("⚠️ Plotly not installed. Run `pip install plotly` to see the analytics dashboard.")
            st.info("All other features (AM/PM routine, products, ML insights) are fully working!")

    # ── Lifestyle Tips ────────────────────────────────────────────────────────
    st.markdown("<br>",unsafe_allow_html=True)
    card_open("💡 Personalised Lifestyle Tips","Based on your quiz answers")
    for tip in profile["tips"]:
        st.markdown(f'<div class="tip-box">✦ {tip}</div>',unsafe_allow_html=True)
    card_close()

    st.markdown("<br>",unsafe_allow_html=True)
    col1,col2,col3=st.columns([1,1,1])
    with col2:
        if st.button("🔄 Retake Quiz",use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
step = st.session_state.step
if   step==0: page_landing()
elif step==1: page_step1()
elif step==2: page_step2()
elif step==3: page_step3()
elif step==4: page_step4()
elif step==5: page_results()
