# GlowIQ — Personalised Skincare Recommender
### Final Semester Project

---

## 🌿 About
GlowIQ is a web application that recommends personalised skincare routines and products based on:
- Skin type & age
- Skin concerns (acne, dark spots, dryness, etc.)
- Lifestyle factors (diet, sleep, stress, sun exposure)
- Monthly budget

Built with **Python + Streamlit**. Clean & minimal UI inspired by premium skincare brands.

---

## 📁 Project Structure
```
skincare_app/
│
├── app.py              ← Main Streamlit app (UI, pages, routing)
├── recommend.py        ← Quiz scoring + recommendation engine
├── products.py         ← Product database (40+ real products)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🚀 How to Run

### Step 1: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the app
```bash
streamlit run app.py
```

### Step 3: Open in browser
The app will open automatically at: **http://localhost:8501**

---

## 🧠 How the Recommendation Engine Works

1. **Quiz Scoring**: Each product is scored against the user's profile using a weighted algorithm:
   - Skin type match (+4 pts)
   - Each matching concern (+3 pts per concern)
   - Budget tier fit (+2 pts, -5 pts if over budget)
   - Sensitivity adjustments
   - Age-based weighting

2. **Routine Building**: Best-scored products are selected per category (cleanser, serum, moisturiser, SPF) for AM and PM routines

3. **Skin Score**: A 0–100 score is calculated based on lifestyle factors (hydration, sleep, diet, sun exposure, stress)

---

## ✨ Features
- 4-step interactive quiz with progress indicator
- AM & PM routine generator
- Tabbed results view (AM / PM / All Products)
- Product cards with tier badges (Budget / Mid-range / Premium)
- Personalised lifestyle tips
- Product search/filter
- Mobile-friendly layout
- Fully restartable (Retake Quiz button)

---

## 🛍 Product Database
40+ real products across 8 categories:
- Cleansers, Toners/Exfoliants, Serums, Moisturisers
- Sunscreens, Eye Creams, Spot Treatments, Face Masks

Brands include: Minimalist, Cetaphil, The Ordinary, CeraVe, La Roche-Posay, Kiehl's, SkinCeuticals, Estée Lauder, La Mer, SK-II, and more.

---

## 🎓 Academic Note
This project demonstrates:
- Python OOP and data structures
- Weighted scoring algorithms
- Multi-page web app development
- UI/UX design principles
- Real-world product database management

---

*Made with 🌿 and Python*

