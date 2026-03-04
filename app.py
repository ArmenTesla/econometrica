"""
Hotel Price Analytics Dashboard
Professional bilingual (EN/HY) analytics dashboard for Armenian hotel price analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import sys
import os

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from data_loader import (
    load_hotel_data,
    filter_by_date_range,
    filter_by_hotel,
    filter_by_city,
    get_unique_hotels,
    get_unique_cities,
    validate_data,
)
from analytics import (
    apply_currency,
    calculate_all_metrics,
    get_price_trend,
    get_hotel_comparison,
    get_city_comparison,
    get_seasonal_comparison,
    get_weekend_weekday_comparison,
    get_year_over_year_change,
    get_value_ranking,
    SEASONS,
)
from econometrics import (
    run_ols_price_model,
    run_season_anova,
    build_econometric_insights,
)
from charts import (
    create_price_trend_chart,
    create_hotel_comparison_chart,
    create_city_comparison_chart,
    create_seasonal_comparison_chart,
    create_weekend_comparison_chart,
    create_yoy_chart,
)
from translations import load_translations, get_translation_function

# Page configuration
st.set_page_config(
    page_title="Hotel Price Analytics",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAV_TAB_ANALYTICS = "analytics"
NAV_TAB_ECONOMETRICS = "econometrics"
NAV_TAB_FORECASTS = "forecasts"
NAV_TAB_ABOUT_MODEL = "about_model"


# Initialize session state
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.filtered_df = None

if "language" not in st.session_state:
    st.session_state.language = "en"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def load_css():
    """Load custom CSS styles."""
    css_path = os.path.join(os.path.dirname(__file__), 'styles', 'main.css')
    try:
        with open(css_path, 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # Use default styles


def load_data():
    """Load hotel data and validate it."""
    try:
        df = load_hotel_data('data/hotels.csv')
        is_valid, error_msg = validate_data(df)
        
        if not is_valid:
            return None, error_msg
        
        st.session_state.df = df
        st.session_state.data_loaded = True
        return df, None
    except FileNotFoundError:
        return None, "missing_file"
    except Exception:
        return None, "unexpected_error"


def display_metric_card(title: str, value: str, color_class: str = ""):
    """Display a metric card with custom styling."""
    card_class = f"metric-card {color_class}" if color_class else "metric-card"
    st.markdown(
        f"""
        <div class="{card_class}">
            <h4>{title}</h4>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def require_authentication(t):
    """Guard the application behind a simple password check."""
    if st.session_state.authenticated:
        return

    st.title(t("login_title"))

    with st.form("auth_form"):
        password = st.text_input(t("login_password_label"), type="password")
        submitted = st.form_submit_button(t("login_button_label"))

    if not submitted:
        st.stop()

    expected_password = st.secrets.get("APP_PASSWORD")
    if not expected_password:
        st.error(t("login_error_missing_secret"))
        st.stop()

    if password == expected_password:
        st.session_state.authenticated = True
        st.rerun()

    st.error(t("login_error_invalid"))
    st.stop()


def render_sidebar(t):
    """Render the persistent sidebar: app title, language selector, navigation."""
    st.sidebar.markdown(f"### {t('app_title')}")
    st.sidebar.markdown("---")

    st.sidebar.subheader(t("language"))
    selected_language = st.sidebar.radio(
        "",
        options=["en", "hy"],
        index=0 if st.session_state.language == "en" else 1,
        format_func=lambda x: t("english") if x == "en" else t("armenian"),
        label_visibility="collapsed",
    )

    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        translations = load_translations(st.session_state.language)
        get_translation_function(translations)
        st.rerun()

    st.sidebar.subheader(t("navigation"))
    tab_options = [NAV_TAB_ANALYTICS, NAV_TAB_ECONOMETRICS, NAV_TAB_FORECASTS, NAV_TAB_ABOUT_MODEL]
    tab_labels = {
        NAV_TAB_ANALYTICS: t("nav_analytics"),
        NAV_TAB_ECONOMETRICS: t("nav_econometrics"),
        NAV_TAB_FORECASTS: t("nav_forecasts"),
        NAV_TAB_ABOUT_MODEL: t("nav_about_model"),
    }
    selected_tab = st.sidebar.radio(
        "",
        options=tab_options,
        index=0,
        format_func=lambda key: tab_labels[key],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    return selected_tab


def _format_econometric_term(term: str, t) -> str:
    """Map raw statsmodels term names to human-readable labels via translations."""
    if term == "Intercept":
        return t(
            "econ_term_intercept",
            season=t("winter"),
            city=t("city_name_yerevan"),
        )
    if term.startswith("C(season"):
        # Example: C(season, Treatment(reference='Winter'))[T.Summer]
        if "[T." in term:
            season_raw = term.split("[T.", 1)[1].rstrip("]")
        else:
            season_raw = term
        return t(
            "econ_term_season",
            season=t(season_raw.lower()),
            baseline_season=t("winter"),
        )
    if term.startswith("C(city"):
        # Example: C(city, Treatment(reference='Yerevan'))[T.Gyumri]
        if "[T." in term:
            city_raw = term.split("[T.", 1)[1].rstrip("]")
        else:
            city_raw = term
        city_key = f"city_name_{city_raw.lower()}"
        return t(
            "econ_term_city",
            city=t(city_key),
            baseline_city=t("city_name_yerevan"),
        )
    if term.startswith("C(hotel_name"):
        # Example: C(hotel_name)[T.Some Hotel]
        if "[T." in term:
            hotel_name = term.split("[T.", 1)[1].rstrip("]")
        else:
            hotel_name = term
        return t("econ_term_hotel", hotel=hotel_name)
    if term == "time_trend":
        return t("econ_term_time_trend")
    return term


def _extract_seasonal_coefficient(coef_df, season_name, t):
    """Extract seasonal coefficient value."""
    season_rows = coef_df[coef_df["term"].str.startswith("C(season")]
    for _, row in season_rows.iterrows():
        term = row["term"]
        if "[T." in term:
            raw_season = term.split("[T.", 1)[1].rstrip("]")
            if raw_season == season_name:
                return float(row["coef"])
    return None


def _extract_city_coefficient(coef_df, t):
    """Extract city coefficient value."""
    city_rows = coef_df[coef_df["term"].str.startswith("C(city")]
    if not city_rows.empty:
        return float(city_rows.iloc[0]["coef"])
    return None


def _extract_time_trend_coefficient(coef_df):
    """Extract time trend coefficient value."""
    trend_rows = coef_df[coef_df["term"] == "time_trend"]
    if not trend_rows.empty:
        return float(trend_rows.iloc[0]["coef"])
    return None


def _extract_hotel_examples(coef_df, n_examples=3):
    """Extract example hotels with their fixed effect coefficients."""
    hotel_rows = coef_df[coef_df["term"].str.startswith("C(hotel_name")]
    if hotel_rows.empty:
        return []
    
    # Sort by absolute coefficient value and take top examples
    hotel_rows = hotel_rows.copy()
    hotel_rows["abs_coef"] = hotel_rows["coef"].abs()
    hotel_rows = hotel_rows.sort_values("abs_coef", ascending=False).head(n_examples)
    
    examples = []
    for _, row in hotel_rows.iterrows():
        term = row["term"]
        if "[T." in term:
            hotel_name = term.split("[T.", 1)[1].rstrip("]")
            coef = float(row["coef"])
            examples.append({"hotel": hotel_name, "coef": coef})
    return examples


def _interpret_f_statistic(f_stat):
    """Interpret F-statistic strength."""
    if f_stat > 10:
        return "strong"
    elif f_stat > 5:
        return "moderate"
    else:
        return "weak"


def _interpret_p_value(p_value):
    """Interpret p-value significance."""
    if p_value < 0.05:
        return "significant"
    else:
        return "nonsignificant"


def render_analytics_section(
    t,
    display_df,
    base_display_df,
    filtered_df,
    effective_check_in_ts,
    effective_check_out_ts,
    currency_code,
):
    """Render the main analytics (charts, metrics, tables)."""
    # Display data summary
    st.info(t("showing_records", count=len(filtered_df)))
    st.header(t("key_metrics"))

    metrics = calculate_all_metrics(display_df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        display_metric_card(
            t("average_price"),
            f"{metrics['average']:.2f} {currency_code}",
            "metric-card-blue",
        )

    with col2:
        display_metric_card(
            t("min_price"),
            f"{metrics['min']:.2f} {currency_code}",
            "metric-card-green",
        )

    with col3:
        display_metric_card(
            t("max_price"),
            f"{metrics['max']:.2f} {currency_code}",
            "metric-card-orange",
        )

    with col4:
        change_color = (
            "metric-card-red" if metrics["change_percent"] < 0 else "metric-card-green"
        )
        change_symbol = "📉" if metrics["change_percent"] < 0 else "📈"
        display_metric_card(
            t("price_change"),
            f"{change_symbol} {metrics['change_percent']:.2f}%",
            change_color,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts section
    st.header(t("visualizations"))

    # Price trend chart (full width)
    st.subheader(t("price_trend_over_time"))
    trend_df = get_price_trend(display_df)
    if not trend_df.empty and len(trend_df) > 0:
        trend_chart = create_price_trend_chart(
            trend_df,
            t(
                "price_trend_title",
                start=effective_check_in_ts.strftime("%Y-%m-%d"),
                end=effective_check_out_ts.strftime("%Y-%m-%d"),
            ),
            currency_label=currency_code,
            labels={
                "no_data": t("no_trend_data"),
                "series_name": t("average_price"),
                "x_axis_title": t("axis_date"),
                "y_axis_title": t(
                    "axis_price_per_night", currency=currency_code
                ),
                "hover_x_label": t("axis_date"),
                "hover_y_label": t("average_price"),
            },
        )
        st.plotly_chart(trend_chart, use_container_width=True)
    else:
        st.warning(t("no_trend_data"))

    # Advanced analytics section
    st.markdown("<br>", unsafe_allow_html=True)

    # Seasonal and Weekend comparison in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t("seasonal_comparison"))
        seasonal_df = get_seasonal_comparison(display_df)
        if not seasonal_df.empty and len(seasonal_df) > 0:
            seasonal_display_df = seasonal_df.copy()
            if "season" in seasonal_display_df.columns:
                seasonal_display_df["season"] = seasonal_display_df[
                    "season"
                ].apply(lambda s: t(str(s).lower()))
            seasonal_chart = create_seasonal_comparison_chart(
                seasonal_display_df,
                t("seasonal_comparison"),
                currency_label=currency_code,
                labels={
                    "no_data": t("no_trend_data"),
                    "series_name": t("average_price"),
                    "x_axis_title": t("axis_season"),
                    "y_axis_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                    "hover_x_label": t("axis_season"),
                    "hover_y_label": t("average_price"),
                    "colorbar_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                },
            )
            st.plotly_chart(seasonal_chart, use_container_width=True)
        else:
            st.warning(t("no_trend_data"))

    with col2:
        st.subheader(t("weekend_vs_weekday"))
        weekend_df = get_weekend_weekday_comparison(display_df)
        if not weekend_df.empty and len(weekend_df) > 0:
            weekend_display_df = weekend_df.copy()
            if "is_weekend" in weekend_display_df.columns:
                def _map_day_type(val):
                    if val == "Weekend":
                        return t("weekend")
                    if val == "Weekday":
                        return t("weekday")
                    return val

                weekend_display_df["is_weekend"] = weekend_display_df[
                    "is_weekend"
                ].apply(_map_day_type)

            weekend_chart = create_weekend_comparison_chart(
                weekend_display_df,
                t("weekend_vs_weekday"),
                currency_label=currency_code,
                labels={
                    "no_data": t("no_trend_data"),
                    "series_name": t("average_price"),
                    "x_axis_title": t("axis_day_type"),
                    "y_axis_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                    "hover_x_label": t("axis_day_type"),
                    "hover_y_label": t("average_price"),
                    "difference_label": t(
                        "seasonal_difference_percent_short"
                    ),
                    "weekend_label": t("weekend"),
                },
            )
            st.plotly_chart(weekend_chart, use_container_width=True)
        else:
            st.warning(t("no_trend_data"))

    # Year-over-year chart (full width)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(t("year_over_year"))
    yoy_df = get_year_over_year_change(display_df)
    if not yoy_df.empty and len(yoy_df) > 1:
        yoy_chart = create_yoy_chart(
            yoy_df,
            t("year_over_year"),
            currency_label=currency_code,
            labels={
                "no_data": t("no_trend_data"),
                "price_series_name": t("average_price"),
                "change_series_name": t("axis_yoy_change_percent"),
                "x_axis_title": t("axis_year"),
                "y_axis_title": t(
                    "axis_price_per_night", currency=currency_code
                ),
                "y2_axis_title": t("axis_yoy_change_percent"),
                "hover_x_label": t("axis_year"),
                "hover_y_price_label": t("average_price"),
                "hover_y_change_label": t("axis_yoy_change_percent"),
            },
        )
        st.plotly_chart(yoy_chart, use_container_width=True)
    else:
        st.info(t("yoy_requires_multiple_years"))

    # Comparison charts in columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(t("price_comparison_by_hotel"))
        hotel_comparison_df = get_hotel_comparison(display_df)
        if not hotel_comparison_df.empty and len(hotel_comparison_df) > 0:
            hotel_chart = create_hotel_comparison_chart(
                hotel_comparison_df,
                t("price_comparison_by_hotel"),
                currency_label=currency_code,
                labels={
                    "no_data": t("no_hotel_comparison"),
                    "series_name": t("average_price"),
                    "x_axis_title": t("axis_hotel"),
                    "y_axis_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                    "hover_x_label": t("axis_hotel"),
                    "hover_y_label": t("average_price"),
                    "colorbar_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                },
            )
            st.plotly_chart(hotel_chart, use_container_width=True)
        else:
            st.warning(t("no_hotel_comparison"))

    with col2:
        st.subheader(t("price_comparison_by_city"))
        city_comparison_df = get_city_comparison(display_df)
        if not city_comparison_df.empty and len(city_comparison_df) > 0:
            city_display_df = city_comparison_df.copy()
            if "city" in city_display_df.columns:
                def _map_city(val):
                    key = f"city_name_{str(val).lower()}"
                    return t(key)

                city_display_df["city"] = city_display_df["city"].apply(
                    _map_city
                )

            city_chart = create_city_comparison_chart(
                city_display_df,
                t("price_comparison_by_city"),
                currency_label=currency_code,
                labels={
                    "no_data": t("no_city_comparison"),
                    "series_name": t("average_price"),
                    "x_axis_title": t("axis_city"),
                    "y_axis_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                    "hover_x_label": t("axis_city"),
                    "hover_y_label": t("average_price"),
                    "colorbar_title": t(
                        "axis_price_per_night", currency=currency_code
                    ),
                },
            )
            st.plotly_chart(city_chart, use_container_width=True)
        else:
            st.warning(t("no_city_comparison"))

    # Value ranking table
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader(t("value_ranking"))

    value_df = get_value_ranking(
        base_display_df, None
    )
    if not value_df.empty:
        value_display_df = value_df.copy()
        rename_map = {
            "hotel_name": t("col_hotel_name"),
            "average_price": t("average_price"),
            "rating": t("col_rating"),
            "value_score": t("col_value_score"),
        }
        value_display_df = value_display_df.rename(columns=rename_map)
        st.dataframe(
            value_display_df.head(10),
            use_container_width=True,
            hide_index=True,
        )

    # Data table section
    st.header(t("data_table"))

    display_table_df = display_df.copy()
    rename_map = {
        "hotel_name": t("col_hotel_name"),
        "city": t("col_city"),
        "date": t("col_date"),
        "price_per_night": t("col_price_per_night", currency=currency_code),
        "rating": t("col_rating"),
        "season": t("col_season"),
        "is_weekend": t("col_is_weekend"),
        "year": t("col_year"),
        "value_score": t("col_value_score"),
    }
    display_table_df = display_table_df.rename(
        columns={k: v for k, v in rename_map.items() if k in display_table_df.columns}
    )
    if "city" in display_table_df.columns:
        display_table_df["city"] = display_table_df["city"].apply(
            lambda c: t(f"city_name_{str(c).lower()}")
        )
    if "season" in display_table_df.columns:
        display_table_df["season"] = display_table_df["season"].apply(
            lambda s: t(str(s).lower())
        )
    if "is_weekend" in display_table_df.columns:
        def _map_day_type(val):
            if val == "Weekend":
                return t("weekend")
            if val == "Weekday":
                return t("weekday")
            return val

        display_table_df["is_weekend"] = display_table_df["is_weekend"].apply(
            _map_day_type
        )

    st.dataframe(
        display_table_df,
        use_container_width=True,
        hide_index=True,
    )

    csv = display_df.to_csv(index=False)
    st.download_button(
        label=t("download_filtered_data"),
        data=csv,
        file_name=(
            f"hotel_data_"
            f"{effective_check_in_ts.strftime('%Y%m%d')}"
            f"_{effective_check_out_ts.strftime('%Y%m%d')}.csv"
        ),
        mime="text/csv",
    )


def render_econometric_section(t, filtered_df):
    """Render the econometric analysis tab with comprehensive academic explanation."""
    st.header(t("econometric_analysis"))

    econ_df = filtered_df.copy()

    ols_result = run_ols_price_model(econ_df)
    anova_result = run_season_anova(econ_df)

    # ===================================================================
    # ACADEMIC INTERPRETATION SECTIONS
    # ===================================================================
    
    if ols_result is not None:
        coef_df = ols_result["coef_table"].copy()
        baseline = ols_result["baseline"]
        
        # Academic Title
        st.markdown("---")
        st.subheader(t("econ_academic_title"))
        st.markdown(t("econ_academic_intro"))
        
        # 1. Model Purpose and Role
        st.markdown("---")
        st.subheader(t("econ_section_purpose_title"))
        st.markdown(t("econ_section_purpose_why_model"))
        st.markdown(t("econ_section_purpose_question"))
        st.markdown(t("econ_section_purpose_ceteris"))
        
        # 2. Model Specification
        st.markdown("---")
        st.subheader(t("econ_section_specification_title"))
        st.markdown(t("econ_section_specification_dependent"))
        st.markdown(t("econ_section_specification_independent"))
        st.markdown(f"- {t('econ_section_specification_season')}")
        st.markdown(f"- {t('econ_section_specification_city')}")
        st.markdown(f"- {t('econ_section_specification_hotel')}")
        st.markdown(f"- {t('econ_section_specification_trend')}")
        st.markdown(t("econ_section_specification_levels"))
        
        # 3. Interpreting Regression Coefficients
        st.markdown("---")
        st.subheader(t("econ_section_coefficients_title"))
        
        # A. Intercept
        st.markdown(f"**{t('econ_section_coefficients_intercept_title')}**")
        st.markdown(t("econ_section_coefficients_intercept_explanation"))
        
        # B. Seasonal Coefficients
        st.markdown(f"**{t('econ_section_coefficients_seasonal_title')}**")
        summer_coef = _extract_seasonal_coefficient(coef_df, "Summer", t)
        if summer_coef is not None:
            st.markdown(t("econ_section_coefficients_seasonal_explanation", coef=summer_coef))
        else:
            st.markdown(t("econ_section_coefficients_seasonal_explanation", coef=0.0))
        st.markdown(t("econ_section_coefficients_seasonal_baseline"))
        
        # C. City Effect
        st.markdown(f"**{t('econ_section_coefficients_city_title')}**")
        st.markdown(t("econ_section_coefficients_city_explanation"))
        st.markdown(t("econ_section_coefficients_city_interpretation"))
        
        # D. Hotel Fixed Effects
        st.markdown(f"**{t('econ_section_coefficients_hotel_title')}**")
        st.markdown(t("econ_section_coefficients_hotel_why"))
        st.markdown(f"- {t('econ_section_coefficients_hotel_quality')}")
        st.markdown(f"- {t('econ_section_coefficients_hotel_reputation')}")
        st.markdown(f"- {t('econ_section_coefficients_hotel_location')}")
        st.markdown(f"- {t('econ_section_coefficients_hotel_amenities')}")
        st.markdown(t("econ_section_coefficients_hotel_comparison"))
        st.markdown(t("econ_section_coefficients_hotel_interpretation"))
        
        # 4. Concrete Comparison Between Hotels
        st.markdown("---")
        st.subheader(t("econ_section_comparison_title"))
        st.markdown(t("econ_section_comparison_intro"))
        
        hotel_examples = _extract_hotel_examples(coef_df, n_examples=3)
        if hotel_examples:
            for example in hotel_examples:
                direction = t("econ_section_comparison_direction_higher") if example["coef"] >= 0 else t("econ_section_comparison_direction_lower")
                st.markdown(t("econ_section_comparison_example", 
                             hotel=example["hotel"], 
                             coef=abs(example["coef"]),
                             direction=direction))
        st.markdown(t("econ_section_comparison_economic"))
        st.markdown(t("econ_section_comparison_controlled"))
        
        # 5. Statistical Significance and Reliability
        st.markdown("---")
        st.subheader(t("econ_section_significance_title"))
        st.markdown(t("econ_section_significance_pvalue"))
        st.markdown(t("econ_section_significance_threshold"))
        st.markdown(t("econ_section_significance_difference"))
        st.markdown(f"- **{t('econ_section_significance_statistical')}**")
        st.markdown(f"- **{t('econ_section_significance_economic')}**")
        st.markdown(t("econ_section_significance_insignificant"))
        st.markdown(f"- {t('econ_section_significance_low_variation')}")
        st.markdown(f"- {t('econ_section_significance_limited_sample')}")
        st.markdown(f"- {t('econ_section_significance_collinearity')}")
        
        # 6. Why Winter is Most Reliable
        st.markdown("---")
        st.subheader(t("econ_section_winter_title"))
        st.markdown(f"**{t('econ_section_winter_emphasis')}**")
        st.markdown(t("econ_section_winter_stability"))
        st.markdown(t("econ_section_winter_tourism"))
        st.markdown(t("econ_section_winter_predictable"))
        st.markdown(t("econ_section_winter_strategic"))
        st.markdown(t("econ_section_winter_conclusion"))
        
        # 7. ANOVA Results Interpretation
        if anova_result is not None:
            st.markdown("---")
            st.subheader(t("econ_section_anova_title"))
            st.markdown(t("econ_section_anova_what"))
            st.markdown(t("econ_section_anova_why"))
            
            f_stat = anova_result["f_stat"]
            p_value = anova_result["p_value"]
            f_interp = _interpret_f_statistic(f_stat)
            p_interp = _interpret_p_value(p_value)
            
            f_interp_key = f"econ_section_anova_fstat_{f_interp}"
            p_interp_key = f"econ_section_anova_pvalue_{p_interp}"
            
            st.markdown(t("econ_section_anova_fstat", 
                         f_stat=f_stat,
                         interpretation=t(f_interp_key)))
            st.markdown(t("econ_section_anova_pvalue",
                         p_value=p_value,
                         interpretation=t(p_interp_key)))
        
        # 8. Common Defense Questions
        st.markdown("---")
        st.subheader(t("econ_section_questions_title"))
        st.markdown("**Q: Why regression instead of averages?**")
        st.markdown(t("econ_section_questions_regression"))
        st.markdown("**Q: Why Winter as baseline?**")
        st.markdown(t("econ_section_questions_winter"))
        st.markdown("**Q: What does a hotel fixed effect mean?**")
        st.markdown(t("econ_section_questions_fixed_effect"))
        st.markdown("**Q: Is this model causal?**")
        st.markdown(t("econ_section_questions_causal"))
        st.markdown("**Q: What are the limitations?**")
        st.markdown(t("econ_section_questions_limitations"))
        
        # ===================================================================
        # REGRESSION TABLE AND RESULTS
        # ===================================================================
        
        st.markdown("---")
        st.subheader(t("econometric_regression_title"))
        st.caption(t("econometric_regression_description"))

        coef_table = coef_df.copy()
        coef_table["Term"] = coef_table["term"].apply(
            lambda term: _format_econometric_term(term, t)
        )
        display_cols = ["Term", "coef", "std_err", "p_value"]
        coef_table = coef_table[display_cols].rename(
            columns={
                "coef": t("econometric_col_coefficient"),
                "std_err": t("econometric_col_std_err"),
                "p_value": t("econometric_col_p_value"),
                "Term": t("econometric_col_term"),
            }
        )
        coef_table[t("econometric_col_coefficient")] = coef_table[
            t("econometric_col_coefficient")
        ].round(2)
        coef_table[t("econometric_col_std_err")] = coef_table[
            t("econometric_col_std_err")
        ].round(2)
        coef_table[t("econometric_col_p_value")] = coef_table[
            t("econometric_col_p_value")
        ].round(4)

        st.markdown(f"**{t('econometric_regression_table_title')}**")
        st.dataframe(
            coef_table,
            use_container_width=True,
            hide_index=True,
        )

        r_squared = ols_result["r_squared"]
        n_obs = ols_result["n_obs"]
        col_r2, col_n = st.columns(2)
        with col_r2:
            st.metric(
                label=t("econometric_r_squared_label"),
                value=f"{r_squared:.3f}",
            )
        with col_n:
            st.metric(
                label=t("econometric_n_obs_label"),
                value=f"{int(n_obs)}",
            )

    # ANOVA Section
    if anova_result is not None:
        st.markdown("---")
        st.subheader(t("econometric_anova_title"))
        st.caption(t("econometric_anova_description"))
        st.write(
            t(
                "econometric_anova_stats",
                f_stat=anova_result["f_stat"],
                p_value=anova_result["p_value"],
            )
        )

    # Key Insights
    insights = build_econometric_insights(ols_result, anova_result, t)
    if insights["regression"] or insights["anova"]:
        st.markdown("---")
        st.subheader(t("econometric_insights_title"))
        for text in insights["regression"]:
            st.markdown(f"- {text}")
        for text in insights["anova"]:
            st.markdown(f"- {text}")


def render_forecast_placeholder(t):
    """Render the placeholder for future forecasting models."""
    st.header(t("forecasts_title"))
    st.info(t("forecasts_placeholder"))


def render_about_model_section(t, filtered_df):
    """Render the comprehensive explanation of the econometric model."""
    st.header(t("about_model_title"))
    
    # Introduction
    st.markdown(t("about_model_intro"))
    st.markdown("---")
    
    # Model Specification
    st.subheader(t("about_model_specification"))
    st.markdown(t("about_model_type"))
    
    st.markdown(f"**{t('about_model_formula_title')}:**")
    st.code(t("about_model_formula"), language=None)
    st.markdown(t("about_model_formula_explanation"))
    st.markdown("---")
    
    # Dependent Variable
    st.subheader(t("about_model_dependent"))
    st.markdown(f"**{t('about_model_dependent_title')}**")
    st.markdown(t("about_model_dependent_explanation"))
    st.markdown("---")
    
    # Independent Variables
    st.subheader(t("about_model_independent"))
    st.markdown(t("about_model_independent_intro"))
    
    # Season
    st.markdown(f"**{t('about_model_season_title')}**")
    st.markdown(f"- {t('about_model_season_baseline')}")
    st.markdown(f"- {t('about_model_season_interpretation')}")
    st.markdown(f"- {t('about_model_season_reference')}")
    
    # City
    st.markdown(f"**{t('about_model_city_title')}**")
    st.markdown(f"- {t('about_model_city_baseline')}")
    st.markdown(f"- {t('about_model_city_interpretation')}")
    st.markdown(f"- {t('about_model_city_importance')}")
    
    # Hotel Fixed Effects
    st.markdown(f"**{t('about_model_hotel_title')}**")
    st.markdown(f"- {t('about_model_hotel_explanation')}")
    st.markdown(f"- {t('about_model_hotel_controls')}")
    st.markdown(f"- {t('about_model_hotel_reference')}")
    
    # Time Trend
    st.markdown(f"**{t('about_model_trend_title')}**")
    st.markdown(f"- {t('about_model_trend_explanation')}")
    st.markdown(f"- {t('about_model_trend_purpose')}")
    st.markdown(f"- {t('about_model_trend_interpretation')}")
    st.markdown("---")
    
    # Winter Reliability
    st.subheader(t("about_model_winter_reliability"))
    st.markdown(f"**{t('about_model_winter_title')}**")
    st.markdown(t("about_model_winter_stable"))
    
    st.markdown(f"**{t('about_model_winter_stable_demand')}**")
    st.markdown(f"**{t('about_model_winter_less_volatility')}**")
    st.markdown(f"**{t('about_model_winter_predictable')}**")
    
    st.markdown(t("about_model_summer_challenges"))
    st.markdown(f"- {t('about_model_summer_tourism')}")
    st.markdown(f"- {t('about_model_summer_events')}")
    st.markdown(f"- {t('about_model_summer_capacity')}")
    
    st.markdown(f"**{t('about_model_winter_conclusion')}**")
    st.markdown("---")
    
    # Statistical Significance
    st.subheader(t("about_model_significance"))
    st.markdown(f"**{t('about_model_significance_title')}**")
    st.markdown(t("about_model_significance_explanation"))
    st.markdown(t("about_model_significance_threshold"))
    
    st.markdown(f"**{t('about_model_significance_meaningful')}**")
    st.markdown(t("about_model_significance_nonmeaningful"))
    st.markdown("---")
    
    # ANOVA
    st.subheader(t("about_model_anova"))
    st.markdown(f"**{t('about_model_anova_title')}**")
    st.markdown(t("about_model_anova_explanation"))
    st.markdown(f"- {t('about_model_anova_fstat')}")
    st.markdown(f"- {t('about_model_anova_pvalue')}")
    st.markdown(t("about_model_anova_complement"))
    st.markdown("---")
    
    # Practical Interpretation
    st.subheader(t("about_model_practical"))
    st.markdown(f"**{t('about_model_practical_title')}**")
    
    st.markdown(t("about_model_practical_hotel"))
    st.markdown(f"- {t('about_model_practical_hotel_season')}")
    st.markdown(f"- {t('about_model_practical_hotel_city')}")
    st.markdown(f"- {t('about_model_practical_hotel_trend')}")
    
    st.markdown(t("about_model_practical_analyst"))
    st.markdown(f"- {t('about_model_practical_analyst_rigor')}")
    st.markdown(f"- {t('about_model_practical_analyst_quantification')}")
    st.markdown(f"- {t('about_model_practical_analyst_validation')}")
    
    st.markdown("---")
    st.markdown(f"**{t('about_model_practical_serious')}**")


def main():
    """Main application function."""
    load_css()

    translations = load_translations(st.session_state.language)
    t = get_translation_function(translations)

    require_authentication(t)

    selected_tab = render_sidebar(t)

    st.title(f"🏨 {t('app_title')}")
    st.markdown("---")

    if not st.session_state.data_loaded:
        with st.spinner(t("loading_data")):
            df, error_key = load_data()
            if df is None:
                if error_key:
                    st.error(t(error_key))
                else:
                    st.error(t("error_loading_data"))
                st.stop()
    else:
        df = st.session_state.df

    st.sidebar.header(t("filters"))
    
    # Date range picker
    st.sidebar.subheader(t("date_range"))
    
    # Get available date range from data dynamically
    if not df.empty and 'date' in df.columns:
        data_min_date = df['date'].min().date()
        data_max_date = df['date'].max().date()
        
        # Restrict visible date range to 2025-01-01 → 2026-12-31
        restricted_min = date(2025, 1, 1)
        restricted_max = date(2026, 12, 31)
        
        # Use intersection of data range and restricted range
        # This ensures we only show dates that exist in data AND are in 2025-2026
        min_date = max(data_min_date, restricted_min)
        max_date = min(data_max_date, restricted_max)
        
        # Safety: If intersection is invalid, fall back to data range
        if min_date > max_date:
            min_date = data_min_date
            max_date = data_max_date
        
        # Set safe defaults: check_in = min_date, check_out = min_date + 3 days
        default_check_in = min_date
        default_check_out = min_date + timedelta(days=3)
        
        # Clamp check_out to never exceed max_date
        if default_check_out > max_date:
            default_check_out = max_date
        
        # Final safety: Ensure check_out is always after check_in
        if default_check_out <= default_check_in:
            if max_date > min_date:
                default_check_out = min(min_date + timedelta(days=1), max_date)
            else:
                # Edge case: only one day available
                default_check_out = max_date
    else:
        # Fallback if no data (should not happen, but safety check)
        restricted_min = date(2025, 1, 1)
        restricted_max = date(2026, 12, 31)
        min_date = restricted_min
        max_date = restricted_max
        default_check_in = min_date
        default_check_out = min_date + timedelta(days=3)
        if default_check_out > max_date:
            default_check_out = max_date
    
    # Date input for check-in (no hardcoded values, all derived from data)
    check_in = st.sidebar.date_input(
        t("check_in_date"),
        value=default_check_in,
        min_value=min_date,
        max_value=max_date
    )
    
    # Calculate safe min for check-out (must be after check-in)
    check_out_min = check_in + timedelta(days=1)
    if check_out_min > max_date:
        check_out_min = max_date
    
    # Calculate safe default for check-out
    safe_check_out_default = default_check_out
    if safe_check_out_default <= check_in:
        safe_check_out_default = check_out_min
    if safe_check_out_default > max_date:
        safe_check_out_default = max_date
    
    # Date input for check-out
    check_out = st.sidebar.date_input(
        t("check_out_date"),
        value=safe_check_out_default,
        min_value=check_out_min,
        max_value=max_date
    )
    
    # Final safety: Auto-adjust check_out if it's <= check_in
    if check_out <= check_in:
        check_out = min(check_in + timedelta(days=1), max_date)
        if check_out <= check_in:
            st.sidebar.error(t("checkout_after_checkin"))
            st.stop()
    
    # Add caption showing available data range
    st.sidebar.caption(f"Available data: {min_date.year}–{max_date.year}")
    
    # City filter
    cities = get_unique_cities(df)
    # Create display options with translated "All Cities"
    city_display_options = [t("all_cities")] + cities[1:]  # First item is "All Cities", replace with translation
    
    selected_city_idx = st.sidebar.selectbox(
        t("select_city"),
        options=range(len(city_display_options)),
        format_func=lambda x: city_display_options[x],
        index=0
    )
    selected_city = cities[selected_city_idx]  # Use actual value from cities list
    
    # Hotel filter
    hotels = get_unique_hotels(df)
    # Create display options with translated "All Hotels"
    hotel_display_options = [t("all_hotels")] + hotels[1:]  # First item is "All Hotels", replace with translation
    
    selected_hotel_idx = st.sidebar.selectbox(
        t("select_hotel"),
        options=range(len(hotel_display_options)),
        format_func=lambda x: hotel_display_options[x],
        index=0
    )
    selected_hotel = hotels[selected_hotel_idx]  # Use actual value from hotels list
    
    # Season selector (works together with date/city/hotel filters, but is applied first in logic).
    st.sidebar.subheader(t("select_season"))
    season_options = ["all"] + SEASONS
    selected_season = st.sidebar.selectbox(
        "",
        options=season_options,
        format_func=lambda season: (
            t("all_seasons") if season == "all" else t(season.lower())
        ),
        index=0,
        label_visibility="collapsed",
    )

    # ------------------------------------------------------------------
    # Season-aware filtering pipeline
    # 1) Apply season filter (logical scope of data)
    # 2) Apply date range filter *inside* that season, with auto-correction
    # 3) Apply city / hotel filters
    # ------------------------------------------------------------------

    # Convert UI dates to pandas Timestamps
    check_in_ts = pd.Timestamp(check_in) if not isinstance(check_in, pd.Timestamp) else check_in
    check_out_ts = pd.Timestamp(check_out) if not isinstance(check_out, pd.Timestamp) else check_out

    # Effective date range actually used for filtering (may be auto-adjusted for seasons)
    effective_check_in_ts = check_in_ts
    effective_check_out_ts = check_out_ts

    # Determine season scope and auto-correct date range when it does not intersect
    if selected_season != "all" and "season" in df.columns and "date" in df.columns:
        season_df = df[df["season"] == selected_season].copy()
        if not season_df.empty:
            season_start = season_df["date"].min().normalize()
            season_end = season_df["date"].max().normalize()

            # Check if the user-selected date range intersects the season window
            if (check_out_ts < season_start) or (check_in_ts > season_end):
                # Auto-correct to a 7-day window starting at the first available
                # date of the season, clamped by the season's actual end.
                effective_check_in_ts = season_start
                seven_days_after_start = season_start + pd.Timedelta(days=7)
                effective_check_out_ts = min(seven_days_after_start, season_end)

                # Inform the user (translated, no hardcoded text)
                st.info(t("date_range_adjusted_to_season"))
                st.caption(
                    t(
                        "season_date_mismatch_explanation",
                        season=t(selected_season.lower()),
                    )
                )
        else:
            # No data at all for this season; keep season_df empty,
            # downstream empty-state logic will handle this edge case.
            pass
    else:
        season_df = df.copy()

    # 1) Season filter has been applied by choosing season_df above.
    # 2) Apply date range filter *inside* that season (using effective dates).
    season_date_df = filter_by_date_range(
        season_df,
        effective_check_in_ts,
        effective_check_out_ts,
    )

    # 3) Apply city and hotel filters on top of the season+date subset.
    filtered_df = season_date_df.copy()

    # Filter by city (compare with actual "All Cities" string)
    if selected_city != "All Cities":
        filtered_df = filter_by_city(filtered_df, selected_city)

    # Filter by hotel (compare with actual "All Hotels" string)
    if selected_hotel != "All Hotels":
        filtered_df = filter_by_hotel(filtered_df, selected_hotel)

    # For cross-season analytics (e.g., value ranking), we also keep a version
    # that ignores the season filter but still respects date / city / hotel.
    base_cross_season_df = df.copy()
    base_cross_season_df = filter_by_date_range(
        base_cross_season_df,
        effective_check_in_ts,
        effective_check_out_ts,
    )
    if selected_city != "All Cities":
        base_cross_season_df = filter_by_city(base_cross_season_df, selected_city)
    if selected_hotel != "All Hotels":
        base_cross_season_df = filter_by_hotel(base_cross_season_df, selected_hotel)

    # Currency: USD for English, AMD for Armenian
    currency_code = "AMD" if st.session_state.language == "hy" else "USD"
    display_df = apply_currency(filtered_df, currency_code)
    base_display_df = apply_currency(base_cross_season_df, currency_code)

    # Store filtered data (after all filters, including season)
    st.session_state.filtered_df = filtered_df
    
    # Debug info in sidebar
    if not df.empty and 'date' in df.columns:
        st.sidebar.markdown("---")
        st.sidebar.markdown(
            f"**{t('data_loaded')}:** {len(df)} {t('rows')} "
            f"({df['date'].min().date()} → {df['date'].max().date()})"
        )
    
    with st.sidebar.expander(t("debug_info"), expanded=False):
        st.write(f"**{t('total_records')}:** {len(df)}")
        st.write(f"**{t('filtered_records')}:** {len(filtered_df)}")
        st.write(
            f"**{t('selected_range')}:** "
            f"{effective_check_in_ts.date()} to {effective_check_out_ts.date()}"
        )
        if not filtered_df.empty and "date" in filtered_df.columns:
            st.write(f"**{t('filtered_date_min')}:** {filtered_df['date'].min()}")
            st.write(f"**{t('filtered_date_max')}:** {filtered_df['date'].max()}")
    
    # Main content area
    # About Model tab doesn't require filtered data, so allow it to proceed
    if filtered_df.empty and selected_tab != NAV_TAB_ABOUT_MODEL:
        # After applying season → date range (with auto-correction) → city/hotel,
        # there is still no data. For specific seasons this is typically due to
        # city/hotel filters being too narrow, not a season/date mismatch.
        if selected_season != "all":
            season_label = t(selected_season.lower())
            st.warning(t("no_season_data_for_range", season=season_label))
            st.info(t("try_different_season_or_dates"))
        else:
            st.info(t("try_different"))
        st.stop()
    
    # Route to the selected tab content
    if selected_tab == NAV_TAB_ANALYTICS:
        render_analytics_section(
            t,
            display_df,
            base_display_df,
            filtered_df,
            effective_check_in_ts,
            effective_check_out_ts,
            currency_code,
        )
    elif selected_tab == NAV_TAB_ECONOMETRICS:
        render_econometric_section(t, filtered_df)
    elif selected_tab == NAV_TAB_FORECASTS:
        render_forecast_placeholder(t)
    elif selected_tab == NAV_TAB_ABOUT_MODEL:
        render_about_model_section(t, filtered_df)

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #7F8C8D; padding: 1rem;'>"
        f"{t('built_with')}"
        f"</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
