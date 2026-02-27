"""
Generate a clean, season-aware hotel dataset (2025-2026) for Yerevan and Gyumri.

This script performs a full rebuild of ``data/hotels.csv`` with:
- Only the specified cities and hotels
- Daily coverage from 2025-01-01 to 2026-12-31 (no gaps)
- Explicit season column with all four seasons populated
- Season-aware, city-specific price ranges
- Stable per-hotel ratings

Final CSV schema:
hotel_name, city, date, price_per_night, rating, season
"""

import csv
import os
from datetime import date, timedelta
import random


def get_season(current_date: date) -> str:
    """Map a calendar date to its canonical season."""
    month = current_date.month
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def is_weekend(current_date: date) -> bool:
    """Return True if the given date falls on Saturday or Sunday."""
    return current_date.weekday() >= 5


def generate_dataset() -> None:
    """Generate a fresh, season-complete dataset for 2025-01-01 → 2026-12-31."""
    os.makedirs("data", exist_ok=True)

    # Hotels restricted to Yerevan and Gyumri with stable ratings.
    hotels = [
        # Yerevan
        ("Yerevan", "The Alexander, a Luxury Collection Hotel, Yerevan", 4.8),
        ("Yerevan", "Republica Hotel Yerevan", 4.6),
        ("Yerevan", "DoubleTree by Hilton Yerevan", 4.7),
        ("Yerevan", "Ani Grand Hotel Yerevan", 4.4),
        # Gyumri
        ("Gyumri", "Grand Hotel Gyumri", 4.3),
        ("Gyumri", "Berlin Art Hotel Gyumri", 4.2),
    ]

    # Price bands by city and season (USD, before weekend/daily adjustments).
    price_ranges = {
        "Yerevan": {
            "Winter": (110, 180),
            "Spring": (130, 210),
            "Summer": (160, 260),
            "Autumn": (120, 200),
        },
        "Gyumri": {
            "Winter": (70, 120),
            "Spring": (80, 140),
            "Summer": (100, 170),
            "Autumn": (80, 140),
        },
    }

    start = date(2025, 1, 1)
    end = date(2026, 12, 31)

    rows = []
    current = start

    # Deterministic but realistic noise.
    random.seed(42)

    while current <= end:
        season = get_season(current)
        weekend = is_weekend(current)

        for city, hotel_name, rating in hotels:
            season_min, season_max = price_ranges[city][season]

            # Base price within the seasonal band.
            base_price = random.uniform(season_min, season_max)

            # Weekend premium: modest but consistent uplift.
            weekend_mult = 1.10 if weekend else 1.0

            # Daily fluctuation around the base (±6%).
            fluctuation = random.uniform(-0.06, 0.06)

            price = base_price * weekend_mult * (1.0 + fluctuation)

            # Clamp back into a tight band around the seasonal range.
            floor = season_min * 0.95
            ceil = season_max * 1.05
            price = max(floor, min(price, ceil))

            rows.append(
                [
                    hotel_name,
                    city,
                    current.isoformat(),
                    f"{price:.2f}",
                    f"{rating:.1f}",
                    season,
                ]
            )

        current += timedelta(days=1)

    output_path = os.path.join("data", "hotels.csv")
    # Hard reset: overwrite any existing dataset.
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "hotel_name",
                "city",
                "date",
                "price_per_night",
                "rating",
                "season",
            ]
        )
        writer.writerows(rows)

    print(f"Created {output_path} with {len(rows)} rows")
    print(f"Date range: {start} to {end}")
    print(f"Hotels: {len(hotels)}")
    print(f"Cities: {len(set(city for city, _, _ in hotels))}")


if __name__ == "__main__":
    generate_dataset()

