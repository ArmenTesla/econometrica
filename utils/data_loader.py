"""
Data loading utilities for hotel price analysis.
Handles CSV loading, data validation, and filtering.
"""

import pandas as pd
from datetime import datetime
from typing import Optional, Tuple


def load_hotel_data(file_path: str = "data/hotels.csv") -> pd.DataFrame:
    """
    Load hotel data from CSV file.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with hotel data
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
    """
    try:
        df = pd.read_csv(file_path)
        
        # Convert date column to datetime if it exists
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            # Drop rows with invalid dates
            df = df.dropna(subset=["date"])
        
        # Ensure price_per_night is numeric
        if "price_per_night" in df.columns:
            df["price_per_night"] = pd.to_numeric(df["price_per_night"], errors="coerce")
            # Drop rows with invalid prices
            df = df.dropna(subset=["price_per_night"])
        
        # Derive year and weekend flag from the canonical date column so that
        # analytics functions can operate on a minimal CSV schema.
        if "date" in df.columns:
            df["year"] = df["date"].dt.year
            df["is_weekend"] = df["date"].dt.weekday >= 5
            df["is_weekend"] = df["is_weekend"].map(
                lambda is_weekend: "Weekend" if is_weekend else "Weekday"
            )
        
        # Keep only Yerevan and Gyumri hotels in the dataset
        if "city" in df.columns:
            allowed_cities = ["Yerevan", "Gyumri"]
            df = df[df["city"].isin(allowed_cities)].copy()
        
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"Data file not found at {file_path}. Please ensure the file exists.")


def filter_by_date_range(
    df: pd.DataFrame,
    check_in: datetime,
    check_out: datetime,
) -> pd.DataFrame:
    """
    Filter hotel data by date range (inclusive: check-in <= date <= check-out).
    
    Args:
        df: DataFrame with hotel data
        check_in: Check-in date (inclusive)
        check_out: Check-out date (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or "date" not in df.columns:
        return df
    
    # Validate date range
    if check_out < check_in:
        return pd.DataFrame()
    
    # Ensure dates are pandas Timestamps for proper comparison
    if not isinstance(check_in, pd.Timestamp):
        check_in = pd.Timestamp(check_in)
    if not isinstance(check_out, pd.Timestamp):
        check_out = pd.Timestamp(check_out)
    
    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])
    
    # Filter data within date range (inclusive on both ends)
    mask = (df["date"] >= check_in) & (df["date"] <= check_out)
    return df[mask].copy()


def filter_by_hotel(df: pd.DataFrame, hotel_name: Optional[str] = None) -> pd.DataFrame:
    """
    Filter hotel data by hotel name.
    
    Args:
        df: DataFrame with hotel data
        hotel_name: Name of the hotel to filter (None for all hotels)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or "hotel_name" not in df.columns:
        return df
    
    if hotel_name is None or hotel_name == "All Hotels":
        return df
    
    return df[df["hotel_name"] == hotel_name].copy()


def filter_by_city(df: pd.DataFrame, city: Optional[str] = None) -> pd.DataFrame:
    """
    Filter hotel data by city.
    
    Args:
        df: DataFrame with hotel data
        city: Name of the city to filter (None for all cities)
        
    Returns:
        Filtered DataFrame
    """
    if df.empty or "city" not in df.columns:
        return df
    
    if city is None or city == "All Cities":
        return df
    
    return df[df["city"] == city].copy()


def get_unique_hotels(df: pd.DataFrame) -> list:
    """
    Get list of unique hotel names from the dataset.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        List of unique hotel names
    """
    if df.empty or "hotel_name" not in df.columns:
        return []
    
    hotels = ["All Hotels"] + sorted(df["hotel_name"].unique().tolist())
    return hotels


def get_unique_cities(df: pd.DataFrame) -> list:
    """
    Get list of unique cities from the dataset.
    
    Args:
        df: DataFrame with hotel data
        
    Returns:
        List of unique city names
    """
    if df.empty or "city" not in df.columns:
        return []
    
    cities = ["All Cities"] + sorted(df["city"].unique().tolist())
    return cities


def validate_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that the DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_columns = ["hotel_name", "city", "date", "price_per_night"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    if df.empty:
        return False, "DataFrame is empty"
    
    return True, ""

