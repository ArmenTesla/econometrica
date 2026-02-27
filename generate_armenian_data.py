"""
Generate a fresh Armenian hotel dataset for 2026-01-01 to 2027-12-31.
Pure standard library (no pandas) so it can run in any Python environment.
"""

import csv
import os
from datetime import date, timedelta
import random


def generate_dataset() -> None:
    """Generate data/hotels.csv with Armenian hotels only."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Define hotels: (city, hotel_name, min_price, max_price)
    # Yerevan luxury: 150–280 USD
    yerevan_hotels = [
        ("Yerevan", "The Alexander, a Luxury Collection Hotel, Yerevan", 220, 280),
        ("Yerevan", "Republica Hotel Yerevan", 170, 230),
        ("Yerevan", "DoubleTree by Hilton Yerevan", 180, 250),
        ("Yerevan", "Ani Grand Hotel Yerevan", 160, 220),
        ("Yerevan", "Metropol Hotel Yerevan", 150, 210),
    ]

    # Regional hotels: 70–160 USD
    regional_hotels = [
        ("Tsaghkadzor", "Marriott Tsaghkadzor", 110, 160),
        ("Tsaghkadzor", "Kecharis Hotel & Resort", 90, 150),
        ("Tsaghkadzor", "Ararat Resort Tsaghkadzor", 80, 140),
        ("Dilijan", "Tufenkian Old Dilijan Complex", 90, 150),
        ("Dilijan", "Best Western Plus Paradise Hotel Dilijan", 90, 150),
        ("Jermuk", "Jermuk Olympia Sanatorium", 80, 140),
        ("Jermuk", "Jermuk Ashkharh Health Center", 70, 130),
        ("Gyumri", "Grand Hotel Gyumri", 80, 140),
        ("Gyumri", "Berlin Art Hotel Gyumri", 75, 130),
    ]

    hotels = yerevan_hotels + regional_hotels

    # Stable rating per hotel: 4.0–4.9
    random.seed(42)
    ratings = {
        hotel_name: round(random.uniform(4.0, 4.9), 1)
        for (_, hotel_name, _, _) in hotels
    }

    # Date range: 2026-01-01 → 2027-12-31 (inclusive, daily, no gaps)
    start = date(2026, 1, 1)
    end = date(2027, 12, 31)

    rows = []
    current = start
    while current <= end:
        # Simple seasonal factor: slightly higher in summer and around New Year
        for city, hotel_name, min_price, max_price in hotels:
            base_price = random.uniform(min_price, max_price)

            month = current.month
            if month in (6, 7, 8):  # Summer
                seasonal = 1.15
            elif month in (12, 1):  # New Year / winter holidays
                seasonal = 1.10
            else:
                seasonal = 1.0

            # Daily fluctuation around base (±10%)
            fluctuation = random.uniform(-0.10, 0.10)
            price = base_price * seasonal * (1.0 + fluctuation)

            # Clamp price to a reasonable range around [min_price, max_price]
            floor = min_price * 0.9
            ceil = max_price * 1.1
            price = max(floor, min(price, ceil))

            rows.append(
                [
                    hotel_name,
                    city,
                    current.isoformat(),  # YYYY-MM-DD
                    f"{price:.2f}",
                    f"{ratings[hotel_name]:.1f}",
                ]
            )

        current += timedelta(days=1)

    output_path = os.path.join("data", "hotels.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["hotel_name", "city", "date", "price_per_night", "rating"])
        writer.writerows(rows)

    print(f"Created {output_path} with {len(rows)} rows")


if __name__ == "__main__":
    generate_dataset()

