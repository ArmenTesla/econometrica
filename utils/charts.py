"""
Chart generation utilities using Plotly.

This module is intentionally focused on visualization concerns only.
Business logic and translations are handled by callers; any user-facing
labels can be injected via the optional ``labels`` dictionaries so charts
remain presentation-only and fully testable.
"""

from typing import Dict, Optional

import pandas as pd
import plotly.graph_objects as go


def create_price_trend_chart(
    df: pd.DataFrame,
    title: str = "Price Trend Over Time",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive line chart showing price trends over time.
    
    Args:
        df: DataFrame with 'date' and 'average_price' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Average Price",
        "x_axis_title": "Date",
        "y_axis_title": f"Price per Night ({currency_label})",
        "hover_x_label": "Date",
        "hover_y_label": "Price",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "date" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["average_price"],
        mode="lines+markers",
        name=default_labels["series_name"],
        line=dict(
            color="#4A90E2",
            width=3,
            shape="spline",
            smoothing=1.3,
        ),
        marker=dict(
            size=6,
            color="#4A90E2",
            line=dict(width=1, color="white"),
        ),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x|%Y-%m-%d}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<br>"
            "<extra></extra>"
        ),
        fill="tonexty" if len(df) > 1 else None,
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial",
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
    )
    
    return fig


def create_hotel_comparison_chart(
    df: pd.DataFrame,
    title: str = "Price Comparison by Hotel",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive bar chart comparing prices across hotels.
    
    Args:
        df: DataFrame with 'hotel_name' and 'average_price' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Average Price",
        "x_axis_title": "Hotel",
        "y_axis_title": f"Average Price per Night ({currency_label})",
        "hover_x_label": "Hotel",
        "hover_y_label": "Price",
        "colorbar_title": f"Price ({currency_label})",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "hotel_name" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["hotel_name"],
        y=df["average_price"],
        name=default_labels["series_name"],
        marker=dict(
            color=df["average_price"],
            colorscale="Blues",
            showscale=True,
            colorbar=dict(title=default_labels["colorbar_title"]),
        ),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
    )
    
    if len(df) > 5:
        fig.update_xaxes(tickangle=-45)
    
    return fig


def create_city_comparison_chart(
    df: pd.DataFrame,
    title: str = "Price Comparison by City",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive bar chart comparing prices across cities.
    
    Args:
        df: DataFrame with 'city' and 'average_price' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Average Price",
        "x_axis_title": "City",
        "y_axis_title": f"Average Price per Night ({currency_label})",
        "hover_x_label": "City",
        "hover_y_label": "Price",
        "colorbar_title": f"Price ({currency_label})",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "city" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["city"],
        y=df["average_price"],
        name=default_labels["series_name"],
        marker=dict(
            color=df["average_price"],
            colorscale="Greens",
            showscale=True,
            colorbar=dict(title=default_labels["colorbar_title"]),
        ),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
    )
    
    return fig


def create_price_distribution_chart(
    df: pd.DataFrame,
    title: str = "Price Distribution",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive histogram showing price distribution.
    
    Args:
        df: DataFrame with 'price_per_night' column
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Price Distribution",
        "x_axis_title": f"Price per Night ({currency_label})",
        "y_axis_title": "Frequency",
        "hover_x_label": "Price Range",
        "hover_y_label": "Count",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "price_per_night" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    prices = df["price_per_night"].dropna()

    if len(prices) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=prices,
        nbinsx=20,
        name=default_labels["series_name"],
        marker=dict(
            color="#9B59B6",
            line=dict(color="#7D3C98", width=1),
        ),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            f"%{{x:.2f}} {currency_label}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            "%{y}<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
        showlegend=False,
    )
    
    return fig


def create_seasonal_comparison_chart(
    df: pd.DataFrame,
    title: str = "Seasonal Price Comparison",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive bar chart comparing prices across seasons.
    
    Args:
        df: DataFrame with 'season' and 'average_price' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Average Price",
        "x_axis_title": "Season",
        "y_axis_title": f"Average Price per Night ({currency_label})",
        "hover_x_label": "Season",
        "hover_y_label": "Price",
        "colorbar_title": f"Price ({currency_label})",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "season" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["season"],
        y=df["average_price"],
        name=default_labels["series_name"],
        marker=dict(
            color=df["average_price"],
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title=default_labels["colorbar_title"]),
        ),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
    )
    
    return fig


def create_weekend_comparison_chart(
    df: pd.DataFrame,
    title: str = "Weekend vs Weekday Prices",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive bar chart comparing weekend vs weekday prices.
    
    Args:
        df: DataFrame with 'is_weekend' and 'average_price' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "series_name": "Average Price",
        "x_axis_title": "Day Type",
        "y_axis_title": f"Average Price per Night ({currency_label})",
        "hover_x_label": "Day Type",
        "hover_y_label": "Price",
        "difference_label": "Difference",
        "weekend_label": "Weekend",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "is_weekend" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    colors = [
        "#E74C3C" if day_type == default_labels["weekend_label"] else "#2ECC71"
        for day_type in df["is_weekend"]
    ]
    
    fig.add_trace(go.Bar(
        x=df["is_weekend"],
        y=df["average_price"],
        name=default_labels["series_name"],
        marker=dict(color=colors),
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x}<br>"
            f"<b>{default_labels['hover_y_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<extra></extra>"
        ),
    ))
    
    if "difference_percent" in df.columns and len(df) >= 1:
        diff_values = df["difference_percent"].dropna()
        if len(diff_values) > 0:
            diff = float(diff_values.iloc[0])
            if diff != 0:
                fig.add_annotation(
                    text=f"{default_labels['difference_label']}: {diff:+.1f}%",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.95,
                    showarrow=False,
                    font=dict(size=12, color="#2C3E50"),
                )
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
        showlegend=False,
    )
    
    return fig


def create_yoy_chart(
    df: pd.DataFrame,
    title: str = "Year-over-Year Price Change",
    currency_label: str = "USD",
    labels: Optional[Dict[str, str]] = None,
) -> go.Figure:
    """
    Create an interactive line chart showing year-over-year price changes.
    
    Args:
        df: DataFrame with 'year', 'average_price', and 'yoy_change' columns
        title: Chart title
        
    Returns:
        Plotly figure object
    """
    default_labels = {
        "no_data": "No data available",
        "price_series_name": "Average Price",
        "change_series_name": "YoY Change %",
        "x_axis_title": "Year",
        "y_axis_title": f"Average Price ({currency_label})",
        "y2_axis_title": "YoY Change (%)",
        "hover_x_label": "Year",
        "hover_y_price_label": "Price",
        "hover_y_change_label": "YoY Change",
    }
    if labels:
        default_labels.update(labels)

    if df.empty or "year" not in df.columns or "average_price" not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text=default_labels["no_data"],
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
        )
        return fig

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["year"],
        y=df["average_price"],
        mode="lines+markers",
        name=default_labels["price_series_name"],
        line=dict(color="#4A90E2", width=3),
        marker=dict(size=8, color="#4A90E2"),
        yaxis="y",
        hovertemplate=(
            f"<b>{default_labels['hover_x_label']}:</b> "
            "%{x}<br>"
            f"<b>{default_labels['hover_y_price_label']}:</b> "
            f"%{{y:.2f}} {currency_label}<extra></extra>"
        ),
    ))
    
    if "yoy_change" in df.columns:
        fig.add_trace(go.Bar(
            x=df["year"],
            y=df["yoy_change"],
            name=default_labels["change_series_name"],
            marker=dict(
                color=[
                    "#E74C3C" if value < 0 else "#2ECC71"
                    for value in df["yoy_change"]
                ],
                opacity=0.6,
            ),
            yaxis="y2",
            hovertemplate=(
                f"<b>{default_labels['hover_x_label']}:</b> "
                "%{x}<br>"
                f"<b>{default_labels['hover_y_change_label']}:</b> "
                "%{y:.2f}%<extra></extra>"
            ),
        ))
    
    fig.update_layout(
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#2C3E50"},
        },
        xaxis_title=default_labels["x_axis_title"],
        yaxis_title=default_labels["y_axis_title"],
        yaxis2=dict(
            title=default_labels["y2_axis_title"],
            overlaying="y",
            side="right",
        ),
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#2C3E50"),
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            showgrid=True,
        ),
        height=400,
    )
    
    return fig

