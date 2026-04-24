# recommend.py — GlowIQ Recommendation Engine
# Quiz-based scoring system: weights concerns, skin type, budget, and lifestyle

from products import PRODUCT_DATABASE


# ══════════════════════════════════════════════════════════════════════════════
#  SKIN PROFILE CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════

def calculate_skin_profile(state) -> dict:
    """
    Score the user's skin health 0–100 and derive lifestyle tips.
    Higher score = healthier skin baseline.
    """
    score = 70  # starting point

    # ── Water Intake ──
    water_map = {
        "Less than 4 glasses": -10,
        "4–6 glasses": -3,
        "7–8 glasses": +5,
        "8+ glasses": +8,
    }
    score += water_map.get(state.get("water_intake", ""), 0)

    # ── Sun Exposure ──
    sun_map = {
        "Mostly indoors": +3,
        "1–2 hours outside": 0,
        "3+ hours outside": -8,
    }
    score += sun_map.get(state.get("sun_exposure", ""), 0)

    # ── Lifestyle Habits ──
    lifestyle = state.get("lifestyle", [])
    bad_habits = ["High sugar / junk food diet 🍟", "Regular smoker 🚬", "Regular alcohol drinker 🍷", "High stress lifestyle 😓"]
    good_habits = ["Mostly healthy / balanced diet 🥗", "Vegan / plant-based 🌱", "Exercise 3+ times/week 🏃"]
    score -= sum(5 for h in lifestyle if any(b in h for b in bad_habits))
    score += sum(4 for h in lifestyle if any(g in h for g in good_habits))

    # ── Number of Concerns ──
    concern_count = len(state.get("concerns", []))
    score -= min(concern_count * 2, 12)

    # ── Sensitivity penalty ──
    sensitivity = state.get("sensitivity", "")
    if "Very sensitive" in sensitivity:
        score -= 6
    elif "Quite sensitive" in sensitivity:
        score -= 3

    score = max(20, min(score, 98))

    # ── Personalised Tips ──
    tips = []
    if state.get("water_intake") in ["Less than 4 glasses", "4–6 glasses"]:
        tips.append("Drink at least 8 glasses of water daily — dehydration shows up as dull, tight skin before you feel thirsty.")
    if state.get("sun_exposure") == "3+ hours outside":
        tips.append("Reapply your SPF every 2 hours when outdoors. Sun damage is the #1 cause of premature ageing and dark spots.")
    if any("stress" in h for h in lifestyle):
        tips.append("High stress raises cortisol, which triggers breakouts and slows skin healing. Even 10 min of mindfulness helps.")
    if any("sugar" in h for h in lifestyle):
        tips.append("High-glycaemic diets cause insulin spikes that worsen acne. Try swapping refined carbs for whole grains for 4 weeks.")
    if any("smoker" in h for h in lifestyle):
        tips.append("Smoking reduces collagen production and causes premature wrinkles — no serum can fully counteract this.")
    if "Dark Circles" in state.get("concerns", []):
        tips.append("Dark circles are often genetic, but 7–8 hrs sleep + a cold compress each morning can visibly reduce puffiness.")
    if state.get("age", 22) >= 30 and "Fine Lines & Wrinkles" not in state.get("concerns", []):
        tips.append("In your 30s+, adding a retinol (0.1–0.3%) 2×/week proactively prevents fine lines — start early for best results.")
    if not tips:
        tips.append("Your skin habits look solid! Consistency is the real secret — stick to your routine for 8–12 weeks for full results.")

    return {
        "score": score,
        "tips": tips,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  CORE SCORING FUNCTION
# ══════════════════════════════════════════════════════════════════════════════

def score_product(product: dict, state: dict) -> float:
    """
    Return a relevance score for a product given user state.
    Higher = more relevant.
    """
    score = 0.0
    skin_type = state.get("skin_type", "Normal")
    concerns = state.get("concerns", [])
    budget_tier = _budget_to_tier(state.get("budget", "Under ₹500"))
    sensitivity = state.get("sensitivity", "Not sensitive")

    # ── Skin type match ──
    product_types = product.get("skin_types", [])
    if skin_type in product_types or "All" in product_types:
        score += 4.0
    else:
        score -= 2.0  # penalise mismatches

    # ── Concern match ──
    product_concerns = product.get("concerns", [])
    for concern in concerns:
        if concern in product_concerns:
            score += 3.0  # each matched concern adds weight

    # ── Budget tier alignment ──
    tier_order = {"Budget": 1, "Mid-range": 2, "Premium": 3}
    user_max = tier_order.get(budget_tier, 1)
    prod_tier = tier_order.get(product.get("tier", "Budget"), 1)
    if prod_tier <= user_max:
        score += 2.0
    else:
        score -= 5.0  # hard penalty for over-budget

    # ── Sensitivity handling ──
    if "Very sensitive" in sensitivity or "Quite sensitive" in sensitivity:
        name = product.get("name", "").lower()
        why = product.get("why", "").lower()
        if "fragrance" in why or "sensitive" in why or "soothing" in why or "ceramide" in why:
            score += 2.0
        if "aha" in name or "bha" in name or "retinol" in name or "benzoyl" in name:
            score -= 3.0  # active acids can irritate sensitive skin

    # ── Age-based scoring ──
    age = state.get("age", 22)
    name_lower = product.get("name", "").lower()
    if age < 25 and ("anti-ageing" in product.get("why", "").lower() or "retinol" in name_lower):
        score -= 1.0  # de-prioritise anti-ageing for young users
    if age >= 30 and ("fine lines" in product.get("why", "").lower() or "wrinkle" in product.get("why", "").lower()):
        score += 2.0

    return score


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTINE BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def get_recommendations(state: dict, profile: dict) -> dict:
    """
    Build a complete AM/PM routine with products.
    """
    skin_type = state.get("skin_type", "Normal")
    concerns = state.get("concerns", [])
    budget_tier = _budget_to_tier(state.get("budget", "Under ₹500"))
    sensitivity = state.get("sensitivity", "Not sensitive")
    experience = state.get("experience", "Beginner")
    age = state.get("age", 22)

    # Flatten all products
    all_products = []
    for category_products in PRODUCT_DATABASE.values():
        all_products.extend(category_products)

    # Score all products
    scored = [(p, score_product(p, state)) for p in all_products]
    scored.sort(key=lambda x: x[1], reverse=True)

    # ── Select best product per category per time of day ──
    def best_for_category(category_key, time_of_day, top_n=1):
        candidates = [
            (p, s) for p, s in scored
            if p.get("category", "").lower().startswith(category_key.lower())
            and time_of_day in p.get("time", [])
        ]
        return [p for p, _ in candidates[:top_n]]

    # AM products
    am_products = []
    am_products += best_for_category("Cleanser", "am")
    am_products += best_for_category("Toner", "am") if experience not in ["Beginner"] else []
    am_products += best_for_category("Serum", "am", top_n=2)
    am_products += best_for_category("Eye", "am") if "Dark Circles" in concerns or "Fine Lines" in str(concerns) else []
    am_products += best_for_category("Moisturiser", "am")
    am_products += best_for_category("Sunscreen", "am")

    # PM products
    pm_products = []
    pm_products += best_for_category("Cleanser", "pm")
    pm_products += best_for_category("Exfoliant", "pm") if experience not in ["Beginner"] else []
    pm_products += best_for_category("Serum", "pm", top_n=2)
    pm_products += best_for_category("Spot Treatment", "pm") if "Acne & Breakouts" in concerns else []
    pm_products += best_for_category("Eye Cream", "pm") if "Dark Circles" in concerns or age >= 28 else []
    pm_products += best_for_category("Moisturiser", "pm")
    pm_products += best_for_category("Face Mask", "pm", top_n=1)  # weekly

    # Remove None/duplicates
    def dedup(lst):
        seen = set()
        out = []
        for p in lst:
            if p and p["name"] not in seen:
                out.append(p)
                seen.add(p["name"])
        return out

    am_products = dedup(am_products)
    pm_products = dedup(pm_products)

    # ── AM Routine Steps ──
    am_routine = _build_am_routine(skin_type, concerns, experience)
    pm_routine = _build_pm_routine(skin_type, concerns, experience, age)

    return {
        "am_products": am_products,
        "pm_products": pm_products,
        "am_routine": am_routine,
        "pm_routine": pm_routine,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTINE STEP GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

def _build_am_routine(skin_type, concerns, experience):
    steps = [
        {"step": "Cleanse", "description": "Wash with a gentle cleanser using lukewarm water. Pat dry — never rub."},
    ]
    if experience not in ["Beginner"]:
        steps.append({"step": "Tone / Essence", "description": "Apply toner on a cotton pad or press into skin with clean hands. Balances pH before serums."})

    if "Dark Circles" in concerns:
        steps.append({"step": "Eye Serum", "description": "Use ring finger to gently tap eye serum around the orbital bone — never drag."})

    steps.append({"step": "Vitamin C Serum", "description": "Apply 3–4 drops of antioxidant serum and press into skin. This protects from free radicals all day."})

    if "Acne & Breakouts" in concerns or "Oiliness" in concerns:
        steps.append({"step": "Niacinamide Serum", "description": "Layer niacinamide after Vitamin C — it controls sebum and shrinks pores."})

    steps.append({"step": "Moisturise", "description": "Apply moisturiser while skin is slightly damp to seal in hydration."})
    steps.append({"step": "SPF 50+", "description": "NEVER skip sunscreen — apply 1/4 tsp on face + neck. Reapply every 2 hrs outdoors. This is the most powerful anti-ageing product."})
    return steps


def _build_pm_routine(skin_type, concerns, experience, age):
    steps = [
        {"step": "Double Cleanse", "description": "Start with micellar water or oil cleanser to remove sunscreen/makeup, then follow with your regular cleanser."},
    ]
    if experience not in ["Beginner"]:
        steps.append({"step": "Exfoliate (2–3×/week)", "description": "Apply AHA/BHA exfoliant and leave for 10 min before next steps. Never exfoliate and use retinol on the same night."})

    if "Acne & Breakouts" in concerns or "Dark Spots & Pigmentation" in concerns or (age >= 28):
        steps.append({"step": "Retinol (2–3×/week)", "description": "Apply a pea-sized amount of retinol to clean, dry skin. Wait 20 min before moisturiser. Start slowly — 2 nights/week."})

    if "Dryness & Flaking" in concerns or age >= 30:
        steps.append({"step": "Hydrating Serum", "description": "Apply hyaluronic acid serum on slightly damp skin for maximum water absorption."})

    if "Acne & Breakouts" in concerns:
        steps.append({"step": "Spot Treatment", "description": "Dab spot treatment only on active blemishes with a clean cotton swab. Do not spread across whole face."})

    if "Dark Circles" in concerns or age >= 28:
        steps.append({"step": "Eye Cream", "description": "Rich eye cream at night nourishes the delicate eye area while you sleep. Apply gently with ring finger."})

    steps.append({"step": "Moisturise", "description": "Apply your night moisturiser or a thicker cream. PM is when skin absorbs rich ingredients best."})
    steps.append({"step": "Weekly Mask (1×/week)", "description": "Once weekly, add a face mask after cleansing. Oily skin: clay mask. Dry/sensitive: hydrating gel mask."})
    return steps


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _budget_to_tier(budget_str: str) -> str:
    if "500" in budget_str and "Under" in budget_str:
        return "Budget"
    elif "500–₹1500" in budget_str or "500" in budget_str:
        return "Mid-range"
    elif "1500" in budget_str:
        return "Mid-range"
    elif "4000" in budget_str or "luxury" in budget_str.lower():
        return "Premium"
    return "Budget"
