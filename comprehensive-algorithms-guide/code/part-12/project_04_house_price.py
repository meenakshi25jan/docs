"""Project 04 — House price prediction with multiple regressors."""

from __future__ import annotations

import numpy as np
from lightgbm import LGBMRegressor
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

RNG = np.random.default_rng(42)


def generate_housing_data(n: int = 800) -> tuple[np.ndarray, np.ndarray]:
    x, y = make_regression(n_samples=n, n_features=8, noise=15.0, random_state=42)
    y = np.abs(y) * 100 + 50_000
    return x, y


def evaluate(name: str, model, x_test: np.ndarray, y_test: np.ndarray) -> float:
    preds = model.predict(x_test)
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))
    print(f"{name:18s} RMSE={rmse:10.2f}  R2={r2:.3f}")
    return r2


def main() -> float:
    x, y = generate_housing_data()
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    models = {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(n_estimators=50, random_state=42),
        "XGBoost": XGBRegressor(n_estimators=50, random_state=42, verbosity=0),
        "LightGBM": LGBMRegressor(n_estimators=50, random_state=42, verbosity=-1),
    }

    scores: dict[str, float] = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        scores[name] = evaluate(name, model, x_test, y_test)

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    print(f"Best model: {best}")
    print("SUCCESS: House price prediction completed")
    return scores[best]


if __name__ == "__main__":
    main()
