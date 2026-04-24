# scraper.py — GlowIQ Nykaa Data Collector
# Attempts to scrape Nykaa skincare products.
# Falls back to realistic synthetic dataset if blocked (Cloudflare / JS rendering).
#
# NOTE: Nykaa uses JavaScript rendering + bot protection.
# A real production scraper would require Selenium + rotating proxies.
# This module documents the attempt and provides clean fallback data.

import requests
import pandas as pd
import numpy as np
import json
import os
import time
import random
from datetime import datetime, timedelta

DATA_PATH = os.path.join(os.path.dirname(__file__), "nykaa_products.csv")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — NYKAA SCRAPER ATTEMPT
# ─────────────────────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en;q=0.9",
    "Referer": "https://www.nykaa.com/",
    "Origin": "https://www.nykaa.com",
}

NYKAA_API_ENDPOINTS = [
    "https://www.nykaa.com/api/product/search?q=skincare&category=skin&sort=popularity&ptype=ptype&offset=0&limit=50",
    "https://www.nykaa.com/api/product/search?q=face+serum&sort=popularity&offset=0&limit=50",
    "https://www.nykaa.com/api/product/search?q=moisturizer&sort=popularity&offset=0&limit=50",
]

def attempt_nykaa_scrape():
    """
    Attempt to fetch product data from Nykaa's internal API.
    Returns a DataFrame if successful, None if blocked.
    """
    print("[Scraper] Attempting Nykaa API connection...")
    results = []

    for url in NYKAA_API_ENDPOINTS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8)
            print(f"[Scraper] Status {resp.status_code} for {url[:60]}...")

            if resp.status_code == 200:
                data = resp.json()
                products = data.get("response", {}).get("products", [])
                for p in products:
                    results.append({
                        "product_name":  p.get("name", ""),
                        "brand":         p.get("brandName", ""),
                        "category":      p.get("categoryPath", ["Skincare"])[-1] if p.get("categoryPath") else "Skincare",
                        "price":         p.get("price", {}).get("label", "0").replace("₹","").replace(",",""),
                        "mrp":           p.get("price", {}).get("mrp", 0),
                        "rating":        p.get("rating", 0),
                        "review_count":  p.get("reviewCount", 0),
                        "discount_pct":  p.get("discount", 0),
                        "is_bestseller": p.get("isBestSeller", False),
                        "source":        "nykaa_api",
                    })
                print(f"[Scraper] Got {len(products)} products from this endpoint.")
            elif resp.status_code in [403, 429, 503]:
                print(f"[Scraper] Blocked ({resp.status_code}) — Cloudflare/bot protection active.")
                return None
            time.sleep(1.5)
        except requests.exceptions.ConnectionError:
            print("[Scraper] Connection failed — no internet or domain blocked.")
            return None
        except Exception as e:
            print(f"[Scraper] Error: {e}")
            return None

    if results:
        df = pd.DataFrame(results)
        df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0)
        return df
    return None


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — SYNTHETIC DATASET GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def generate_synthetic_dataset(n=500, seed=42):
    """
    Generate a realistic synthetic Nykaa skincare product dataset.
    Prices, ratings, reviews, and discount patterns are modelled on
    real Nykaa data distributions observed in public research.
    """
    np.random.seed(seed)
    random.seed(seed)

    # ── Brand universe with realistic tier mapping ──
    brands = {
        # Budget Indian
        "Minimalist": {"tier": "Budget", "avg_price": 450, "popularity": 0.92},
        "Mamaearth":  {"tier": "Budget", "avg_price": 380, "popularity": 0.88},
        "Plum":       {"tier": "Budget", "avg_price": 420, "popularity": 0.85},
        "Dot & Key":  {"tier": "Budget", "avg_price": 650, "popularity": 0.82},
        "mCaffeine":  {"tier": "Budget", "avg_price": 400, "popularity": 0.80},
        "Wow Skin":   {"tier": "Budget", "avg_price": 350, "popularity": 0.75},
        "Biotique":   {"tier": "Budget", "avg_price": 280, "popularity": 0.70},
        "Lotus":      {"tier": "Budget", "avg_price": 310, "popularity": 0.68},
        # Mid-range Global
        "The Ordinary":     {"tier": "Mid-range", "avg_price": 700,  "popularity": 0.90},
        "Cetaphil":         {"tier": "Mid-range", "avg_price": 850,  "popularity": 0.87},
        "Neutrogena":       {"tier": "Mid-range", "avg_price": 950,  "popularity": 0.83},
        "CeraVe":           {"tier": "Mid-range", "avg_price": 1100, "popularity": 0.86},
        "La Roche-Posay":   {"tier": "Mid-range", "avg_price": 1400, "popularity": 0.84},
        "Innisfree":        {"tier": "Mid-range", "avg_price": 1200, "popularity": 0.79},
        "Olay":             {"tier": "Mid-range", "avg_price": 1100, "popularity": 0.78},
        "Garnier":          {"tier": "Mid-range", "avg_price": 600,  "popularity": 0.74},
        # Premium / Luxury
        "Kiehl's":          {"tier": "Premium", "avg_price": 3200,  "popularity": 0.75},
        "The Body Shop":    {"tier": "Premium", "avg_price": 1800,  "popularity": 0.72},
        "Forest Essentials": {"tier": "Premium", "avg_price": 2400, "popularity": 0.70},
        "Clinique":         {"tier": "Premium", "avg_price": 2800,  "popularity": 0.68},
        "Estee Lauder":     {"tier": "Premium", "avg_price": 6500,  "popularity": 0.65},
        "SK-II":            {"tier": "Premium", "avg_price": 9000,  "popularity": 0.55},
        "La Mer":           {"tier": "Premium", "avg_price": 14000, "popularity": 0.40},
        "Paula's Choice":   {"tier": "Premium", "avg_price": 2500,  "popularity": 0.73},
    }

    categories = {
        "Face Serum":        {"weight": 0.20, "price_mult": 1.3},
        "Moisturiser":       {"weight": 0.18, "price_mult": 1.0},
        "Face Wash":         {"weight": 0.16, "price_mult": 0.7},
        "Sunscreen":         {"weight": 0.12, "price_mult": 0.9},
        "Toner":             {"weight": 0.08, "price_mult": 0.85},
        "Eye Cream":         {"weight": 0.07, "price_mult": 1.6},
        "Face Mask":         {"weight": 0.07, "price_mult": 1.1},
        "Spot Treatment":    {"weight": 0.05, "price_mult": 0.95},
        "Face Oil":          {"weight": 0.04, "price_mult": 1.5},
        "Exfoliant / Scrub": {"weight": 0.03, "price_mult": 1.0},
    }

    skin_concerns = ["Acne", "Anti-Ageing", "Brightening", "Hydration",
                     "Pigmentation", "Pore Care", "Sensitive Skin", "Oil Control"]

    key_ingredients_pool = [
        "Niacinamide", "Hyaluronic Acid", "Salicylic Acid", "Vitamin C",
        "Retinol", "AHA/BHA", "Ceramides", "Peptides", "Glycerin",
        "Benzoyl Peroxide", "Zinc", "Green Tea Extract", "Centella Asiatica",
        "Kojic Acid", "Alpha Arbutin", "SPF 50", "Bakuchiol", "Squalane",
    ]

    brand_names = list(brands.keys())
    brand_weights = [brands[b]["popularity"] for b in brand_names]
    brand_weights = np.array(brand_weights) / sum(brand_weights)

    cat_names = list(categories.keys())
    cat_weights = [categories[c]["weight"] for c in cat_names]

    records = []
    base_date = datetime(2023, 1, 1)

    for i in range(n):
        brand_name = np.random.choice(brand_names, p=brand_weights)
        brand_info = brands[brand_name]
        cat_name   = np.random.choice(cat_names, p=cat_weights)
        cat_info   = categories[cat_name]

        # Price — log-normal around brand avg * category multiplier
        base_price = brand_info["avg_price"] * cat_info["price_mult"]
        price = max(99, int(np.random.lognormal(
            np.log(base_price), 0.35
        )))

        # MRP (before discount)
        discount_pct = np.random.choice(
            [0, 5, 10, 15, 20, 25, 30, 35, 40],
            p=[0.15, 0.10, 0.20, 0.20, 0.15, 0.10, 0.05, 0.03, 0.02]
        )
        mrp = int(price / (1 - discount_pct / 100)) if discount_pct > 0 else price

        # Rating — higher-priced premium products rated slightly higher
        tier = brand_info["tier"]
        if tier == "Budget":
            rating = round(np.random.normal(3.9, 0.5), 1)
        elif tier == "Mid-range":
            rating = round(np.random.normal(4.1, 0.4), 1)
        else:
            rating = round(np.random.normal(4.3, 0.35), 1)
        rating = float(np.clip(rating, 1.0, 5.0))

        # Review count — budget brands get more reviews (mass market)
        if tier == "Budget":
            reviews = int(np.random.lognormal(6.5, 1.2))
        elif tier == "Mid-range":
            reviews = int(np.random.lognormal(5.5, 1.1))
        else:
            reviews = int(np.random.lognormal(4.2, 1.0))
        reviews = max(1, min(reviews, 85000))

        # Ingredients (1-3 per product)
        n_ing = random.randint(1, 3)
        ingredients = ", ".join(random.sample(key_ingredients_pool, n_ing))

        # Concern
        concern = random.choice(skin_concerns)

        # Bestseller — popular brands + high reviews + good rating
        is_bestseller = (
            brand_info["popularity"] > 0.80 and
            rating >= 4.0 and
            reviews > 1000 and
            random.random() < 0.35
        )

        # Date added (spread over 2 years)
        days_offset = random.randint(0, 730)
        date_added = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")

        # Product name
        product_suffixes = {
            "Face Serum":        ["Serum", "Booster Serum", "Brightening Serum", "Repair Serum"],
            "Moisturiser":       ["Cream", "Gel Moisturiser", "Water Cream", "Night Cream"],
            "Face Wash":         ["Face Wash", "Cleanser", "Foaming Cleanser", "Gel Cleanser"],
            "Sunscreen":         ["Sunscreen SPF 50", "SPF 50 PA++++", "Sunblock", "UV Shield"],
            "Toner":             ["Toner", "Essence Toner", "Clarifying Toner", "Hydra Toner"],
            "Eye Cream":         ["Eye Cream", "Under Eye Serum", "Eye Repair Cream"],
            "Face Mask":         ["Face Mask", "Sheet Mask", "Clay Mask", "Sleeping Mask"],
            "Spot Treatment":    ["Spot Gel", "Acne Gel", "Blemish Serum", "Pimple Patch"],
            "Face Oil":          ["Face Oil", "Facial Oil", "Night Oil", "Glow Oil"],
            "Exfoliant / Scrub": ["Exfoliant", "Face Scrub", "AHA Exfoliator", "Peel"],
        }
        suffix = random.choice(product_suffixes[cat_name])
        ingredient_tag = random.choice(ingredients.split(", "))
        product_name = f"{brand_name} {ingredient_tag} {suffix}"

        records.append({
            "product_id":    f"NYK{1000 + i}",
            "product_name":  product_name,
            "brand":         brand_name,
            "category":      cat_name,
            "tier":          tier,
            "price":         price,
            "mrp":           mrp,
            "discount_pct":  discount_pct,
            "rating":        rating,
            "review_count":  reviews,
            "key_ingredients": ingredients,
            "skin_concern":  concern,
            "is_bestseller": is_bestseller,
            "date_added":    date_added,
            "source":        "synthetic_nykaa_model",
        })

    df = pd.DataFrame(records)

    # ── Preprocessing steps (documented for EDA page) ──
    df["price"]        = pd.to_numeric(df["price"], errors="coerce")
    df["rating"]       = pd.to_numeric(df["rating"], errors="coerce").clip(1, 5)
    df["review_count"] = pd.to_numeric(df["review_count"], errors="coerce").fillna(0).astype(int)
    df["date_added"]   = pd.to_datetime(df["date_added"])
    df["price_segment"] = pd.cut(
        df["price"],
        bins=[0, 500, 1500, 4000, 99999],
        labels=["Budget (< ₹500)", "Mid-range (₹500–1500)", "Premium (₹1500–4000)", "Luxury (₹4000+)"]
    )
    df["is_bestseller"] = df["is_bestseller"].astype(bool)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — MAIN LOADER (scrape → fallback)
# ─────────────────────────────────────────────────────────────────────────────

def load_data(force_refresh=False):
    """
    Load product data. Priority:
    1. Cached CSV if it exists and force_refresh=False
    2. Nykaa scrape (attempt)
    3. Synthetic fallback
    Returns (df, source_message)
    """
    if not force_refresh and os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH, parse_dates=["date_added"])
        df["price_segment"] = pd.cut(
            df["price"],
            bins=[0, 500, 1500, 4000, 99999],
            labels=["Budget (< ₹500)", "Mid-range (₹500–1500)", "Premium (₹1500–4000)", "Luxury (₹4000+)"]
        )
        return df, "cached"

    # Try scraping
    scraped = attempt_nykaa_scrape()
    if scraped is not None and len(scraped) >= 50:
        scraped.to_csv(DATA_PATH, index=False)
        return scraped, "scraped"

    # Fallback
    print("[Scraper] Using synthetic dataset (Nykaa blocked or unavailable).")
    df = generate_synthetic_dataset(500)
    df.to_csv(DATA_PATH, index=False)
    return df, "synthetic"


if __name__ == "__main__":
    print("Running data collection...")
    df, source = load_data(force_refresh=True)
    print(f"Source: {source}")
    print(f"Shape: {df.shape}")
    print(df.head())
    print(df.dtypes)
