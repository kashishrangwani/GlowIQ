# ml_model.py — GlowIQ Machine Learning Engine
# Uses K-Nearest Neighbours trained on synthetic skincare profiles
# to predict the most effective product categories for a user

import numpy as np
import json

# ── Synthetic Training Data Generator ────────────────────────────────────────
# We generate 500 synthetic skin profiles with labels (which product categories
# are most effective for them). In a real production app this would come from
# user feedback data collected over time.

SKIN_TYPE_MAP   = {"Normal": 0, "Oily": 1, "Dry": 2, "Combination": 3, "Sensitive": 4}
BUDGET_MAP      = {"Under ₹500": 0, "₹500–₹1500": 1, "₹1500–₹4000": 2, "₹4000+": 3}
SENSITIVITY_MAP = {"Not sensitive": 0, "Mildly sensitive": 1, "Quite sensitive": 2, "Very sensitive": 3}

ALL_CONCERNS = [
    "Acne & Breakouts", "Blackheads & Pores", "Oiliness",
    "Dryness & Flaking", "Dullness & Uneven Tone", "Dark Spots & Pigmentation",
    "Fine Lines & Wrinkles", "Dark Circles", "Redness & Irritation",
    "Texture Issues", "Loss of Firmness", "Sun Damage",
]

CATEGORY_LABELS = [
    "Cleanser", "Toner/Exfoliant", "Vitamin C Serum",
    "Niacinamide Serum", "Retinol Serum", "Hydrating Serum",
    "Eye Treatment", "Moisturiser", "Sunscreen",
    "Spot Treatment", "Face Mask",
]

def _encode_user(skin_type, concerns, budget, sensitivity, age):
    """Convert user inputs into a numeric feature vector."""
    features = []
    features.append(SKIN_TYPE_MAP.get(skin_type, 0) / 4.0)
    features.append(BUDGET_MAP.get(budget, 0) / 3.0)
    features.append(SENSITIVITY_MAP.get(sensitivity, 0) / 3.0)
    features.append(min(age, 65) / 65.0)
    for c in ALL_CONCERNS:
        features.append(1.0 if c in concerns else 0.0)
    return np.array(features)


def _generate_training_data(n=600):
    """Generate synthetic labelled training data."""
    np.random.seed(42)
    X, y = [], []

    skin_types   = list(SKIN_TYPE_MAP.keys())
    budgets      = list(BUDGET_MAP.keys())
    sensitivities = list(SENSITIVITY_MAP.keys())

    for _ in range(n):
        st   = np.random.choice(skin_types)
        bud  = np.random.choice(budgets)
        sens = np.random.choice(sensitivities)
        age  = int(np.clip(np.random.normal(28, 10), 14, 65))

        # Randomly pick 1-4 concerns, weighted by skin type
        if st == "Oily":
            pool = ["Acne & Breakouts","Blackheads & Pores","Oiliness","Dullness & Uneven Tone","Dark Spots & Pigmentation"]
        elif st == "Dry":
            pool = ["Dryness & Flaking","Texture Issues","Dullness & Uneven Tone","Fine Lines & Wrinkles","Redness & Irritation"]
        elif st == "Sensitive":
            pool = ["Redness & Irritation","Dryness & Flaking","Texture Issues","Dark Circles"]
        else:
            pool = ALL_CONCERNS

        n_concerns = np.random.randint(1, 5)
        concerns = list(np.random.choice(pool, min(n_concerns, len(pool)), replace=False))

        feat = _encode_user(st, concerns, bud, sens, age)

        # Rule-based label generation (what would a dermatologist recommend?)
        labels = [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0]  # always: cleanser, moisturiser, SPF

        if st in ["Oily", "Combination"] or "Acne & Breakouts" in concerns or "Blackheads & Pores" in concerns:
            labels[3] = 1  # niacinamide
            labels[10] = 1  # face mask
        if "Acne & Breakouts" in concerns:
            labels[9] = 1  # spot treatment
        if st in ["Dry", "Sensitive"] or "Dryness & Flaking" in concerns:
            labels[5] = 1  # hydrating serum
        if "Dullness & Uneven Tone" in concerns or "Dark Spots & Pigmentation" in concerns or "Sun Damage" in concerns:
            labels[2] = 1  # vitamin C
        if age >= 28 or "Fine Lines & Wrinkles" in concerns or "Loss of Firmness" in concerns:
            labels[4] = 1  # retinol
        if "Dark Circles" in concerns or age >= 27:
            labels[6] = 1  # eye treatment
        if st in ["Oily", "Combination"] or "Blackheads & Pores" in concerns or "Texture Issues" in concerns:
            labels[1] = 1  # toner/exfoliant
        if st not in ["Very sensitive"] and age >= 25:
            labels[2] = 1  # add vitamin C for most

        # Add noise
        for i in range(len(labels)):
            if np.random.random() < 0.05:
                labels[i] = 1 - labels[i]

        X.append(feat)
        y.append(labels)

    return np.array(X), np.array(y)


# ── Simple KNN Implementation (no sklearn needed) ────────────────────────────
class SimpleKNN:
    """
    Hand-coded K-Nearest Neighbours classifier.
    Works for multi-label classification.
    No external ML libraries needed — just numpy.
    """
    def __init__(self, k=7):
        self.k = k
        self.X_train = None
        self.y_train = None

    def fit(self, X, y):
        self.X_train = X
        self.y_train = y

    def _euclidean(self, a, b):
        return np.sqrt(np.sum((a - b) ** 2))

    def predict(self, x):
        distances = [self._euclidean(x, xt) for xt in self.X_train]
        k_indices = np.argsort(distances)[:self.k]
        k_labels  = self.y_train[k_indices]
        # Vote: if majority of neighbours have label=1, predict 1
        votes = k_labels.mean(axis=0)
        return (votes >= 0.5).astype(int), votes


# ── Public Interface ──────────────────────────────────────────────────────────
_model = None
_X_train = None
_y_train = None

def get_model():
    global _model, _X_train, _y_train
    if _model is None:
        X, y = _generate_training_data(600)
        _X_train = X
        _y_train = y
        _model = SimpleKNN(k=9)
        _model.fit(X, y)
    return _model


def ml_predict_categories(skin_type, concerns, budget, sensitivity, age):
    """
    Returns (predicted_labels list, confidence_scores list, similar_profiles list).
    predicted_labels: list of recommended CATEGORY_LABELS
    confidence_scores: dict of {category: confidence%}
    similar_profiles: list of dicts describing nearest neighbours
    """
    model = get_model()
    x = _encode_user(skin_type, concerns, budget, sensitivity, age)
    labels, votes = model.predict(x)

    recommended = [CATEGORY_LABELS[i] for i, v in enumerate(labels) if v == 1]
    confidence  = {CATEGORY_LABELS[i]: round(float(votes[i]) * 100, 1) for i in range(len(CATEGORY_LABELS))}

    # Find similar profiles from training set for display
    distances = [np.sqrt(np.sum((x - xt) ** 2)) for xt in _X_train]
    top5_idx  = np.argsort(distances)[:5]

    similar = []
    skin_types_rev = {v: k for k, v in SKIN_TYPE_MAP.items()}
    for idx in top5_idx:
        feat = _X_train[idx]
        similar.append({
            "skin_type":   skin_types_rev.get(round(feat[0] * 4), "Normal"),
            "age":         int(feat[3] * 65),
            "similarity":  round((1 - distances[idx] / (distances[-1] + 1e-6)) * 100, 1),
        })

    return recommended, confidence, similar


def get_model_accuracy_report():
    """
    Run a simple hold-out validation and return accuracy metrics.
    Used in the Data Science Analytics tab.
    """
    X, y = _generate_training_data(800)
    split = int(0.8 * len(X))
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = SimpleKNN(k=9)
    model.fit(X_train, y_train)

    correct_exact = 0
    per_label_correct = np.zeros(len(CATEGORY_LABELS))

    for i in range(len(X_test)):
        preds, _ = model.predict(X_test[i])
        if np.array_equal(preds, y_test[i]):
            correct_exact += 1
        per_label_correct += (preds == y_test[i]).astype(int)

    exact_acc = correct_exact / len(X_test)
    per_label_acc = per_label_correct / len(X_test)

    return {
        "exact_match_accuracy": round(exact_acc * 100, 1),
        "per_label_accuracy": {
            CATEGORY_LABELS[i]: round(per_label_acc[i] * 100, 1)
            for i in range(len(CATEGORY_LABELS))
        },
        "n_train": split,
        "n_test": len(X_test),
        "k": 9,
    }
