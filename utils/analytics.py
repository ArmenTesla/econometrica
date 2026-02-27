"""
Analytics utilities for hotel price analysis.
Calculates metrics, trends, and statistical measures.
"""

import pandas as pd
from typing import Dict, Optional
import numpy as np


USD_TO_AMD_RATE = 400.0  # Adjust if you want a different FX rate

# Central, deterministic season definitions.
# These values are shared across analytics so season logic is never duplicated.
SEASON_WINTER = "Winter"
SEASON_SPRING = "Spring"
SEASON_SUMMER = "Summer"
SEASON_AUTUMN = "Autumn"

SEASONS = [SEASON_WINTER, SEASON_SPRING, SEASON_SUMMER, SEASON_AUTUMN]
SEASON_ORDER_MAP = {season: index for index, season in enumerate(SEASONS)}


def get_season_from_month(month: int) -> str:
  """
  Map a 1-based calendar month to a canonical season name.

  This is the single source of truth for season assignment logic.
  """
  if month in (12, 1, 2):
    return SEASON_WINTER
  if month in (3, 4, 5):
    return SEASON_SPRING
  if month in (6, 7, 8):
    return SEASON_SUMMER
  return SEASON_AUTUMN


def ensure_season_column(df: pd.DataFrame) -> pd.DataFrame:
  """
  Ensure that the DataFrame has a canonical ``season`` column derived from ``date``.

  Existing ``season`` values are left as-is if the column already exists.
  This helper is available for future extensions but is intentionally not
  invoked automatically to avoid surprising mutations.
  """
  if df.empty or "date" not in df.columns or "season" in df.columns:
    return df

  df_with_season = df.copy()
  df_with_season["season"] = df_with_season["date"].dt.month.map(get_season_from_month)
  return df_with_season


def apply_currency(df: pd.DataFrame, currency: str) -> pd.DataFrame:
    """
    Return a copy of df with price_per_night converted to the target currency.
    Assumes source prices are in USD.
    """
    if df.empty or 'price_per_night' not in df.columns:
        return df
    
    if currency == 'AMD':
        factor = USD_TO_AMD_RATE
    else:
        factor = 1.0
    
    df_converted = df.copy()
    df_converted['price_per_night'] = df_converted['price_per_night'] * factor
    df_converted['currency'] = currency
    return df_converted


def calculate_average_price(df: pd.DataFrame) -> float:
    """
    Calculate average price per night.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        Average price (0.0 if no data)
    """
    if df.empty or 'price_per_night' not in df.columns:
        return 0.0
    
    return float(df['price_per_night'].mean())


def calculate_min_price(df: pd.DataFrame) -> float:
    """
    Calculate minimum price per night.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        Minimum price (0.0 if no data)
    """
    if df.empty or 'price_per_night' not in df.columns:
        return 0.0
    
    return float(df['price_per_night'].min())


def calculate_max_price(df: pd.DataFrame) -> float:
    """
    Calculate maximum price per night.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        Maximum price (0.0 if no data)
    """
    if df.empty or 'price_per_night' not in df.columns:
        return 0.0
    
    return float(df['price_per_night'].max())


def calculate_price_change_percentage(df: pd.DataFrame) -> float:
    """
    Calculate price change percentage from first to last date.
    
    Args:
        df: DataFrame with hotel data sorted by date
        
    Returns:
        Price change percentage (0.0 if insufficient data)
    """
    if df.empty or 'price_per_night' not in df.columns or 'date' not in df.columns:
        return 0.0
    
    # Sort by date
    df_sorted = df.sort_values('date')
    
    if len(df_sorted) < 2:
        return 0.0
    
    first_price = df_sorted['price_per_night'].iloc[0]
    last_price = df_sorted['price_per_night'].iloc[-1]
    
    if first_price == 0:
        return 0.0
    
    change_percent = ((last_price - first_price) / first_price) * 100
    return float(change_percent)


def calculate_all_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calculate all price metrics at once.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        Dictionary with all calculated metrics
    """
    return {
        'average': calculate_average_price(df),
        'min': calculate_min_price(df),
        'max': calculate_max_price(df),
        'change_percent': calculate_price_change_percentage(df)
    }


def get_price_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get price trend over time (daily average prices).
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with date and average price columns
    """
    if df.empty or 'date' not in df.columns or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['date', 'average_price'])
    
    # Group by date and calculate average price
    trend_df = df.groupby('date')['price_per_night'].mean().reset_index()
    trend_df.columns = ['date', 'average_price']
    trend_df = trend_df.sort_values('date')
    
    return trend_df


def get_hotel_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average price comparison across hotels.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with hotel_name and average_price columns
    """
    if df.empty or 'hotel_name' not in df.columns or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['hotel_name', 'average_price'])
    
    # Group by hotel and calculate average price
    comparison_df = df.groupby('hotel_name')['price_per_night'].mean().reset_index()
    comparison_df.columns = ['hotel_name', 'average_price']
    comparison_df = comparison_df.sort_values('average_price', ascending=False)
    
    return comparison_df


def get_city_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average price comparison across cities.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with city and average_price columns
    """
    if df.empty or 'city' not in df.columns or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['city', 'average_price'])
    
    # Group by city and calculate average price
    comparison_df = df.groupby('city')['price_per_night'].mean().reset_index()
    comparison_df.columns = ['city', 'average_price']
    comparison_df = comparison_df.sort_values('average_price', ascending=False)
    
    return comparison_df


def get_price_distribution(df: pd.DataFrame, bins: int = 20) -> pd.DataFrame:
    """
    Get price distribution for histogram.
    
    Args:
        df: DataFrame with hotel data
        bins: Number of bins for distribution
        
    Returns:
        DataFrame with price ranges and counts
    """
    if df.empty or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['price_range', 'count'])
    
    prices = df['price_per_night'].dropna()
    
    if len(prices) == 0:
        return pd.DataFrame(columns=['price_range', 'count'])
    
    # Create bins
    min_price = prices.min()
    max_price = prices.max()
    
    if min_price == max_price:
        return pd.DataFrame({
            'price_range': [f'${min_price:.2f}'],
            'count': [len(prices)]
        })
    
    bin_edges = np.linspace(min_price, max_price, bins + 1)
    bin_labels = [f'${bin_edges[i]:.0f}-${bin_edges[i+1]:.0f}' 
                  for i in range(len(bin_edges) - 1)]
    
    # Calculate counts per bin
    counts, _ = np.histogram(prices, bins=bin_edges)
    
    distribution_df = pd.DataFrame({
        'price_range': bin_labels,
        'count': counts
    })
    
    return distribution_df


def get_seasonal_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average price comparison across seasons.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with season and average_price columns
    """
    if df.empty or "season" not in df.columns or "price_per_night" not in df.columns:
        return pd.DataFrame(columns=["season", "average_price"])
    
    seasonal_df = (
        df.groupby("season")["price_per_night"]
        .mean()
        .reset_index()
    )
    seasonal_df.columns = ["season", "average_price"]
    
    # Order seasons using the shared definition so visuals are consistent.
    seasonal_df["season_order"] = seasonal_df["season"].apply(
        lambda season: SEASON_ORDER_MAP.get(season, len(SEASON_ORDER_MAP))
    )
    seasonal_df = seasonal_df.sort_values("season_order").drop("season_order", axis=1)
    
    return seasonal_df


def get_weekend_weekday_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get average price comparison between weekends and weekdays.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with is_weekend and average_price columns
    """
    if df.empty or 'is_weekend' not in df.columns or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['is_weekend', 'average_price'])
    
    # Group by weekend/weekday and calculate average price
    comparison_df = df.groupby('is_weekend')['price_per_night'].mean().reset_index()
    comparison_df.columns = ['is_weekend', 'average_price']
    
    # Calculate difference percentage
    comparison_df['difference_percent'] = 0.0  # Default value
    
    if len(comparison_df) == 2:
        weekday_rows = comparison_df[comparison_df['is_weekend'] == 'Weekday']
        weekend_rows = comparison_df[comparison_df['is_weekend'] == 'Weekend']
        
        if len(weekday_rows) > 0 and len(weekend_rows) > 0:
            weekday_price = weekday_rows['average_price'].iloc[0]
            weekend_price = weekend_rows['average_price'].iloc[0]
            if weekday_price > 0:
                diff_percent = ((weekend_price - weekday_price) / weekday_price) * 100
                # Set the same diff_percent for both rows
                comparison_df.loc[comparison_df['is_weekend'] == 'Weekend', 'difference_percent'] = diff_percent
                comparison_df.loc[comparison_df['is_weekend'] == 'Weekday', 'difference_percent'] = diff_percent
    
    return comparison_df


def get_year_over_year_change(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get year-over-year price change percentage.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with year, average_price, and yoy_change columns
    """
    if df.empty or 'year' not in df.columns or 'price_per_night' not in df.columns:
        return pd.DataFrame(columns=['year', 'average_price', 'yoy_change'])
    
    # Group by year and calculate average price
    yearly_df = df.groupby('year')['price_per_night'].mean().reset_index()
    yearly_df.columns = ['year', 'average_price']
    yearly_df = yearly_df.sort_values('year')
    
    # Calculate YoY change
    yearly_df['yoy_change'] = yearly_df['average_price'].pct_change() * 100
    yearly_df['yoy_change'] = yearly_df['yoy_change'].fillna(0.0)
    
    return yearly_df


def get_value_ranking(
    df: pd.DataFrame,
    selected_season: Optional[str] = None
) -> pd.DataFrame:
    """
    Get hotel ranking by value (price / rating ratio).
    Lower ratio = better value.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        DataFrame with hotel_name, average_price, rating, and value_score columns.
        When ``selected_season`` is provided and a ``season`` column exists,
        additional seasonal comparison columns are included:
        - avg_price_selected_season
        - avg_price_other_seasons
        - seasonal_difference_percent
    """
    base_columns = ["hotel_name", "average_price", "rating", "value_score"]
    has_required = (
        not df.empty
        and "hotel_name" in df.columns
        and "price_per_night" in df.columns
        and "rating" in df.columns
    )
    if not has_required:
        return pd.DataFrame(columns=base_columns)
    
    # Group by hotel and calculate averages
    hotel_stats = (
        df.groupby("hotel_name")
        .agg(
            {
                "price_per_night": "mean",
                "rating": "mean",
            }
        )
        .reset_index()
    )
    hotel_stats.columns = ["hotel_name", "average_price", "rating"]
    
    # Calculate value score (price per rating point)
    hotel_stats["value_score"] = hotel_stats["average_price"] / hotel_stats["rating"]
    
    if selected_season and "season" in df.columns:
        # Compute seasonal and non-seasonal averages on the already-filtered dataset.
        seasonal_df = df[df["season"] == selected_season]
        other_df = df[df["season"] != selected_season]
        
        seasonal_avg = (
            seasonal_df.groupby("hotel_name")["price_per_night"].mean()
            if not seasonal_df.empty
            else pd.Series(dtype=float)
        )
        other_avg = (
            other_df.groupby("hotel_name")["price_per_night"].mean()
            if not other_df.empty
            else pd.Series(dtype=float)
        )
        
        # Align on full hotel index so every hotel has a row.
        seasonal_avg = seasonal_avg.reindex(hotel_stats["hotel_name"]).astype(float)
        other_avg = other_avg.reindex(hotel_stats["hotel_name"]).astype(float)
        
        hotel_stats["avg_price_selected_season"] = seasonal_avg.values
        hotel_stats["avg_price_other_seasons"] = other_avg.values
        
        # Avoid division by zero; where there is no meaningful baseline,
        # report a neutral 0.0 difference rather than NaN or inf.
        with np.errstate(divide="ignore", invalid="ignore"):
            diff_percent = np.where(
                hotel_stats["avg_price_other_seasons"] > 0,
                (
                    (
                        hotel_stats["avg_price_selected_season"]
                        - hotel_stats["avg_price_other_seasons"]
                    )
                    / hotel_stats["avg_price_other_seasons"]
                )
                * 100.0,
                0.0,
            )
        hotel_stats["seasonal_difference_percent"] = diff_percent
    
    # Sort by value score (lower is better)
    hotel_stats = hotel_stats.sort_values("value_score", ascending=True)
    
    return hotel_stats

