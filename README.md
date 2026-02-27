# 🏨 Hotel Price Analytics Dashboard

A professional, bilingual (English/Armenian) data analytics dashboard for analyzing Armenian hotel price trends, seasonality, and market insights.

## 📋 Features

### 🌍 Multi-Language Support
- **English 🇬🇧** and **Armenian 🇦🇲** interface
- Language selector in sidebar
- All UI elements, charts, and messages are fully translated

### 📊 Advanced Analytics
- **Price Trends**: Daily price analysis over time
- **Seasonal Comparison**: Price variations across seasons
- **Weekend vs Weekday**: Pricing differences analysis
- **Year-over-Year**: Long-term price change tracking
- **Value Ranking**: Hotels ranked by price/rating ratio
- **City & Hotel Comparisons**: Multi-dimensional analysis

### 🎯 Key Metrics
- Average, Min, Max prices
- Price change percentage
- Real-time calculations based on filters

### 📈 Interactive Visualizations
- **Price Trend Chart**: Line chart showing price evolution
- **Seasonal Comparison**: Bar chart by season
- **Weekend Analysis**: Weekend vs weekday pricing
- **YoY Chart**: Year-over-year price changes with dual axes
- **Hotel Comparison**: Average prices by hotel
- **City Comparison**: Average prices by city

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this project**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Generate dataset** (if not already generated):
```bash
python generate_realistic_data.py
```

### Running the Application

1. **Start the Streamlit app**:
```bash
streamlit run app.py
```

2. **Open your browser**:
   - The app will automatically open at `http://localhost:8501`
   - If it doesn't, navigate to the URL shown in the terminal

## 📁 Project Structure

```
hotel_data_analyst/
│
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── generate_realistic_data.py # Dataset generator
│
├── data/
│   └── hotels.csv            # Hotel price dataset (2024-2027)
│
├── translations/
│   ├── en.json               # English translations
│   └── hy.json               # Armenian translations
│
├── styles/
│   └── main.css              # Custom CSS styling
│
└── utils/
    ├── data_loader.py        # Data loading and filtering
    ├── analytics.py          # Analytics calculations
    ├── charts.py             # Plotly chart generation
    └── translations.py       # Translation system
```

## 📊 Data Format

The `hotels.csv` file contains the following columns:

- `hotel_name`: Name of the hotel
- `city`: City where the hotel is located (Yerevan, Gyumri)
- `date`: Date in YYYY-MM-DD format
- `price_per_night`: Price per night in USD (numeric)
- `rating`: Hotel rating (numeric, 4.0-4.9)
- `season`: Season (Winter, Spring, Summer, Autumn)

## 🎯 Data Logic

### Realistic Pricing Behavior

The dataset reflects season-aware pricing patterns for Yerevan and Gyumri:

1. **Seasonality**:
   - All four seasons (Winter, Spring, Summer, Autumn) are present in both 2025 and 2026.
   - **Yerevan**:
     - Winter: 110–180 USD
     - Spring: 130–210 USD
     - Summer: 160–260 USD
     - Autumn: 120–200 USD
   - **Gyumri**:
     - Winter: 70–120 USD
     - Spring: 80–140 USD
     - Summer: 100–170 USD
     - Autumn: 80–140 USD

2. **Weekend Premium**:
   - Weekends carry a modest premium on top of the seasonal ranges.

3. **Daily Fluctuations**:
   - Each hotel’s daily price fluctuates slightly (±6%) around its seasonal band, producing realistic but stable behavior.

### Date Range

- **Start**: 2025-01-01
- **End**: 2026-12-31
- **Frequency**: Daily (no gaps)
- **Total Records**: 4,392 rows (6 hotels × 732 days)

## 🎨 Usage

1. **Select Language**: Use the sidebar language selector (EN/HY)

2. **Choose Date Range**: Select check-in and check-out dates

3. **Filter by City**: Select a specific city or "All Cities"

4. **Filter by Hotel**: Select a specific hotel or "All Hotels"

5. **View Metrics**: Key metrics are displayed at the top

6. **Analyze Charts**: Scroll to see interactive visualizations:
   - Price trends over time
   - Seasonal comparisons
   - Weekend vs weekday analysis
   - Year-over-year changes
   - Hotel and city comparisons

7. **Export Data**: Click the download button to export filtered data as CSV

## 🛠️ Customization

### Adding Translations

Edit `translations/en.json` and `translations/hy.json` to add or modify translations.

### Modifying Styles

Edit `styles/main.css` to customize the dashboard appearance.

### Extending Analytics

- Add new metrics in `utils/analytics.py`
- Create new chart types in `utils/charts.py`
- Add new filters in `app.py`

### Regenerating Data

To regenerate the dataset with different parameters:

```bash
python generate_realistic_data.py
```

Modify the script to adjust:
- Hotel lists
- Price ranges
- Seasonal multipliers
- Yearly growth rate

## 📦 Dependencies

- **streamlit**: Web framework for the dashboard
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computations
- **plotly**: Interactive visualizations

## 🐛 Troubleshooting

### Data Not Loading

- Ensure `data/hotels.csv` exists
- Check that the CSV has required columns
- Verify date format is YYYY-MM-DD

### Charts Not Displaying

- Make sure you have selected valid date ranges
- Check that filters return data (not empty)
- Verify Plotly is installed correctly

### Translation Issues

- Ensure `translations/en.json` and `translations/hy.json` exist
- Check JSON syntax is valid
- Verify file encoding is UTF-8

## 📝 Language System

The application uses a centralized translation system:

1. **Translation Files**: JSON files in `translations/` directory
2. **Translation Function**: `t("key")` function for accessing translations
3. **Language State**: Stored in Streamlit session state
4. **Dynamic Updates**: UI updates immediately on language change

### Adding New Translations

1. Add key-value pairs to both `en.json` and `hy.json`
2. Use `t("your_key")` in the code
3. For formatted strings, use `t("key", param=value)`

## 🎯 Project Purpose

This dashboard is designed for:

- **Hotel Managers**: Understanding pricing trends and seasonality
- **Travel Analysts**: Market research and competitive analysis
- **Data Scientists**: Price prediction and demand forecasting
- **Business Intelligence**: Strategic decision-making

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for improvements.

## 📧 Support

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ using Streamlit, Pandas, and Plotly**

**Languages**: English 🇬🇧 | Armenian 🇦🇲
