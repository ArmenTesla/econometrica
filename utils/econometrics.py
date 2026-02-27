"""
Econometric analysis utilities for hotel price data.

Implements:
- Multiple linear regression (OLS) of price_per_night on season, city,
  hotel fixed effects, and a time trend.
- One-way ANOVA for seasonal differences in mean prices.
- Lightweight, human-readable interpretation helpers.

This module is deliberately classical-econometrics only (no ML).
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

from analytics import SEASONS


OLSResult = Dict[str, Any]
ANOVAResult = Dict[str, Any]


def _prepare_econometric_sample(df: pd.DataFrame) -> pd.DataFrame:
  """
  Return a clean sample suitable for econometric analysis.

  Requirements:
  - Non-missing price_per_night, season, city, hotel_name, date.
  - Adds a numeric time_trend variable (days since first observation).
  """
  required_cols = ["price_per_night", "season", "city", "hotel_name", "date"]
  missing = [col for col in required_cols if col not in df.columns]
  if missing:
    return pd.DataFrame()

  if df.empty:
    return df

  sample = df.copy()

  # Drop rows with missing required fields
  sample = sample.dropna(subset=required_cols)

  if sample.empty:
    return sample

  # Ensure date is datetime
  if not pd.api.types.is_datetime64_any_dtype(sample["date"]):
    sample["date"] = pd.to_datetime(sample["date"], errors="coerce")
    sample = sample.dropna(subset=["date"])

  if sample.empty:
    return sample

  # Time trend: days since first available observation
  first_date = sample["date"].min()
  sample["time_trend"] = (sample["date"] - first_date).dt.days.astype(float)

  return sample


def run_ols_price_model(df: pd.DataFrame) -> Optional[OLSResult]:
  """
  Run a multiple linear regression for price_per_night.

  Model:
    price_per_night =
      α
      + β_season * season dummies (Winter as reference)
      + β_city   * city dummies   (Yerevan as reference)
      + hotel fixed effects
      + γ * time_trend (days)
      + ε

  Estimation:
  - OLS via statsmodels.
  - Heteroskedasticity-robust standard errors (HC1).

  Returns None when there is not enough usable data.
  """
  sample = _prepare_econometric_sample(df)
  if sample.empty or sample["price_per_night"].nunique() <= 1:
    return None

  # Defensive: require a minimum number of observations to avoid noisy output.
  if len(sample) < 30:
    return None

  # Reference categories are fixed explicitly for interpretability.
  # - Winter is the baseline for season
  # - Yerevan is the baseline for city
  # - One hotel is left as the omitted category automatically
  formula = (
      "price_per_night ~ "
      "C(season, Treatment(reference='Winter')) + "
      "C(city, Treatment(reference='Yerevan')) + "
      "C(hotel_name) + "
      "time_trend"
  )

  model = smf.ols(formula=formula, data=sample)
  results = model.fit(cov_type="HC1")

  params = results.params
  bse = results.bse
  tvalues = results.tvalues
  pvalues = results.pvalues

  coef_df = pd.DataFrame(
      {
          "term": params.index,
          "coef": params.values,
          "std_err": bse.values,
          "t_stat": tvalues.values,
          "p_value": pvalues.values,
      }
  )

  # Basic ordering: baseline + key dimensions first, then hotel fixed effects.
  def _sort_key(row: pd.Series) -> Tuple[int, str]:
    term = row["term"]
    if term == "Intercept":
      return (0, term)
    if term.startswith("C(season"):
      return (1, term)
    if term.startswith("C(city"):
      return (2, term)
    if term == "time_trend":
      return (3, term)
    if term.startswith("C(hotel_name"):
      return (4, term)
    return (5, term)

  coef_df = coef_df.sort_values(by=["term"], key=lambda s: s.map(lambda x: _sort_key(pd.Series({"term": x}))))  # type: ignore[arg-type]

  baseline_season_mean = float(
      sample.loc[sample["season"] == "Winter", "price_per_night"].mean()
  ) if (sample["season"] == "Winter").any() else float("nan")
  baseline_city_mean = float(
      sample.loc[sample["city"] == "Yerevan", "price_per_night"].mean()
  ) if (sample["city"] == "Yerevan").any() else float("nan")
  overall_mean = float(sample["price_per_night"].mean())

  return {
      "coef_table": coef_df,
      "r_squared": float(results.rsquared),
      "n_obs": int(results.nobs),
      "baseline": {
          "baseline_season": "Winter",
          "baseline_city": "Yerevan",
          "baseline_season_mean": baseline_season_mean,
          "baseline_city_mean": baseline_city_mean,
          "overall_mean": overall_mean,
      },
  }


def run_season_anova(df: pd.DataFrame) -> Optional[ANOVAResult]:
  """
  Perform a one-way ANOVA to test whether mean prices differ across seasons.

  Returns:
  - f_stat
  - p_value
  - season_means: dict[season -> mean price]
  """
  if df.empty or "season" not in df.columns or "price_per_night" not in df.columns:
    return None

  sample = df[["season", "price_per_night"]].dropna()
  if sample.empty:
    return None

  groups: List[np.ndarray] = []
  season_means: Dict[str, float] = {}

  for season in SEASONS:
    season_prices = sample.loc[sample["season"] == season, "price_per_night"]
    if not season_prices.empty:
      season_means[season] = float(season_prices.mean())
      if len(season_prices) >= 2:
        groups.append(season_prices.values)
    else:
      season_means[season] = float("nan")

  # Need at least two non-empty groups with more than one observation
  if len(groups) < 2:
    return None

  f_stat, p_value = stats.f_oneway(*groups)

  return {
      "f_stat": float(f_stat),
      "p_value": float(p_value),
      "season_means": season_means,
  }


def build_econometric_insights(
    ols_result: Optional[OLSResult],
    anova_result: Optional[ANOVAResult],
    t: Callable[[str], str],
) -> Dict[str, List[str]]:
  """
  Build short, human-readable interpretation strings for the UI.

  Notes:
  - Percent effects are computed by scaling dollar coefficients relative
    to appropriate baseline averages; they are interpretable but approximate.
  """
  insights: Dict[str, List[str]] = {"regression": [], "anova": []}

  if ols_result is not None:
    coef_df = ols_result["coef_table"]
    baseline = ols_result["baseline"]
    baseline_season_mean = baseline.get("baseline_season_mean")
    baseline_city_mean = baseline.get("baseline_city_mean")
    overall_mean = baseline.get("overall_mean")

    # Seasonal effect: pick the largest seasonal uplift relative to Winter.
    season_rows = coef_df[coef_df["term"].str.startswith("C(season")]
    if (
        not season_rows.empty
        and isinstance(baseline_season_mean, (int, float))
        and np.isfinite(baseline_season_mean)
        and baseline_season_mean > 0
    ):
      best_idx = season_rows["coef"].idxmax()
      best_row = season_rows.loc[best_idx]
      raw_term = best_row["term"]
      if "[T." in raw_term:
        season_raw = raw_term.split("[T.", 1)[1].rstrip("]")
      else:
        season_raw = raw_term
      season_name = t(season_raw.lower())
      baseline_season_name = t("winter")
      percent = (best_row["coef"] / baseline_season_mean) * 100.0
      if percent >= 0:
        insights["regression"].append(
            t(
                "econ_insight_season_increase",
                season=season_name,
                percent=percent,
                baseline_season=baseline_season_name,
            )
        )
      else:
        insights["regression"].append(
            t(
                "econ_insight_season_reduce",
                season=season_name,
                percent=percent,
                baseline_season=baseline_season_name,
            )
        )

    # City effect: compare each city to Yerevan.
    city_rows = coef_df[coef_df["term"].str.startswith("C(city")]
    if (
        not city_rows.empty
        and isinstance(baseline_city_mean, (int, float))
        and np.isfinite(baseline_city_mean)
        and baseline_city_mean > 0
    ):
      for _, row in city_rows.iterrows():
        raw_term = str(row["term"])
        if "[T." in raw_term:
          city_raw = raw_term.split("[T.", 1)[1].rstrip("]")
        else:
          city_raw = raw_term
        city_key = f"city_name_{city_raw.lower()}"
        city_name = t(city_key)
        baseline_city_name = t("city_name_yerevan")
        percent = (row["coef"] / baseline_city_mean) * 100.0
        direction_key = "econ_direction_higher" if percent >= 0 else "econ_direction_lower"
        direction_word = t(direction_key)
        insights["regression"].append(
            t(
                "econ_insight_city",
                city=city_name,
                percent=abs(percent),
                direction=direction_word,
                baseline_city=baseline_city_name,
            )
        )

    # Time trend: convert daily change into an annual percent movement.
    trend_rows = coef_df[coef_df["term"] == "time_trend"]
    if (
        not trend_rows.empty
        and isinstance(overall_mean, (int, float))
        and np.isfinite(overall_mean)
        and overall_mean > 0
    ):
      beta = float(trend_rows["coef"].iloc[0])
      annual_change = beta * 365.0
      annual_pct = (annual_change / overall_mean) * 100.0
      direction_key = "econ_direction_upward" if annual_change >= 0 else "econ_direction_downward"
      direction_word = t(direction_key)
      insights["regression"].append(
          t(
              "econ_insight_trend",
              annual_change=annual_change,
              annual_pct=annual_pct,
              direction=direction_word,
          )
      )

    # Overall significance snapshot: how many explanatory terms are clearly non-zero.
    non_intercept = coef_df[coef_df["term"] != "Intercept"]
    sig_terms = non_intercept[non_intercept["p_value"] < 0.05]
    if not non_intercept.empty:
      insights["regression"].append(
          t(
              "econ_insight_significance",
              sig_count=len(sig_terms),
              total_count=len(non_intercept),
          )
      )

  if anova_result is not None:
    f_stat = anova_result.get("f_stat")
    p_value = anova_result.get("p_value")
    season_means = anova_result.get("season_means", {})

    if isinstance(p_value, (int, float)) and np.isfinite(p_value):
      if p_value < 0.05:
        insights["anova"].append(t("econ_insight_anova_sig"))
      else:
        insights["anova"].append(t("econ_insight_anova_nonsig"))

    # Identify cheapest and most expensive seasons by average price level.
    clean_means = {
        season: mean
        for season, mean in season_means.items()
        if isinstance(mean, (int, float)) and np.isfinite(mean)
    }
    if clean_means:
      max_season_raw = max(clean_means, key=clean_means.get)
      min_season_raw = min(clean_means, key=clean_means.get)
      max_mean = clean_means[max_season_raw]
      min_mean = clean_means[min_season_raw]
      if min_mean > 0:
        diff_pct = (max_mean - min_mean) / min_mean * 100.0
        insights["anova"].append(
            t(
                "econ_insight_season_pattern",
                max_season=t(max_season_raw.lower()),
                min_season=t(min_season_raw.lower()),
                diff_pct=diff_pct,
            )
        )

  return insights



