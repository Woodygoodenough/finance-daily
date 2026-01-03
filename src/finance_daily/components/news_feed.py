from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

import pandas as pd
import streamlit as st
from streamlit_elements import elements, mui

from finance_daily.constants import NewsFields


@dataclass(frozen=True)
class NewsItem:
    title: str
    url: str
    time_published: str | None = None
    summary: str | None = None
    icon_url: str | None = None
    sentiment_score: float | None = None
    sentiment_label: str | None = None


@dataclass(frozen=True)
class NewsFeedSpec:
    max_items: int = 5
    show_summaries: bool = True
    summary_char_limit: int = 220


CARD_SX = {"borderRadius": 3, "backgroundColor": "rgba(255,255,255,0.02)"}
CONTENT_SX = {"padding": "12px !important"}
TITLE_SX = {
    "fontWeight": 650,
    "fontSize": "0.98rem",
    "lineHeight": 1.25,
    "display": "inline-block",
}
META_ROW_SX = {
    "display": "flex",
    "justifyContent": "space-between",
    "gap": 1.5,
    "alignItems": "flex-start",
    "marginTop": 0.75,
}
CHIPS_ROW_SX = {
    "display": "flex",
    "gap": 1,
    "flexWrap": "wrap",
    "alignItems": "center",
    "marginBottom": 0.5,
}
THUMB_SX = {
    "width": 56,
    "height": 44,
    "borderRadius": 2,
    "overflow": "hidden",
    "border": "1px solid rgba(255,255,255,0.12)",
    "backgroundColor": "rgba(255,255,255,0.04)",
    "flex": "0 0 auto",
}
THUMB_IMG_SX = {
    "width": "100%",
    "height": "100%",
    "objectFit": "cover",
    "display": "block",
}


def _parse_dt(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        # Example: "2026-01-03 13:08:33+00:00"
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _clean_str(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    s = str(value).strip()
    if not s or s.upper() == "NULL" or s.lower() == "nan":
        return None
    return s


def _clean_float(value) -> float | None:
    if value is None:
        return None
    try:
        if isinstance(value, float) and pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None


def _truncate(text: str | None, *, limit: int) -> str | None:
    if not text:
        return None
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "…"


def _sentiment_chip_color(label: str | None) -> str:
    """Map sentiment label to a MUI Chip color."""
    if not label:
        return "default"

    return {
        "bullish": "success",
        "somewhat-bullish": "success",
        "neutral": "info",
        "somewhat-bearish": "warning",
        "bearish": "error",
    }.get(label.strip().lower(), "default")


def _news_chips(it: NewsItem) -> list:
    chips: list = []
    if it.sentiment_label:
        chips.append(
            mui.Chip(
                label=it.sentiment_label,
                color=_sentiment_chip_color(it.sentiment_label),
                size="small",
                variant="outlined",
                sx={"fontWeight": 700},
            )
        )
    if it.sentiment_score is not None:
        chips.append(
            mui.Chip(
                label=f"Sentiment Score {it.sentiment_score:+.3f}",
                color="default",
                size="small",
                variant="outlined",
            )
        )
    return chips


def _news_card(it: NewsItem, *, spec: NewsFeedSpec, key: str) -> object:
    summary = (
        _truncate(it.summary, limit=spec.summary_char_limit)
        if spec.show_summaries
        else None
    )
    return mui.Card(
        key=key,
        variant="outlined",
        sx=CARD_SX,
        children=mui.CardContent(
            sx=CONTENT_SX,
            children=[
                mui.Link(
                    it.title,
                    href=it.url,
                    target="_blank",
                    underline="hover",
                    color="inherit",
                    sx=TITLE_SX,
                ),
                mui.Box(
                    sx=META_ROW_SX,
                    children=[
                        mui.Box(
                            sx={"flex": "1 1 auto", "minWidth": 0},
                            children=[
                                mui.Box(sx=CHIPS_ROW_SX, children=_news_chips(it)),
                                *(
                                    [
                                        mui.Typography(
                                            it.time_published,
                                            variant="caption",
                                            sx={"opacity": 0.75},
                                        )
                                    ]
                                    if it.time_published
                                    else []
                                ),
                            ],
                        ),
                        mui.Box(
                            sx=THUMB_SX,
                            children=(
                                mui.Box(
                                    component="img",
                                    src=it.icon_url,
                                    alt="icon",
                                    sx=THUMB_IMG_SX,
                                )
                                if it.icon_url
                                else None
                            ),
                        ),
                    ],
                ),
                *(
                    [
                        mui.Typography(
                            summary,
                            variant="body2",
                            sx={"opacity": 0.9, "marginTop": 0.75},
                        )
                    ]
                    if summary
                    else []
                ),
            ],
        ),
    )


def df_to_news_items(
    df: pd.DataFrame,
) -> list[NewsItem]:
    """Convert the raw news dataset into render-ready NewsItem objects.

    Returns all items (sorted by most recent if `time_published` exists). Use
    `NewsFeedSpec.max_items` in the renderer to control how many to show.
    """
    if df is None or df.empty:
        return []

    cols = set(df.columns)

    def col(name: str) -> str:
        return name if name in cols else ""

    title_col = col(NewsFields.TITLE.value)
    url_col = col(NewsFields.URL.value)
    time_col = col(NewsFields.TIME_PUBLISHED.value)
    summary_col = col(NewsFields.SUMMARY.value)

    # Optional icon fields: prefer explicit icon, fall back to banner_image.
    icon_col = col(NewsFields.ICON.value)
    banner_col = col(NewsFields.BANNER_IMAGE.value)
    sent_score_col = col(NewsFields.OVERALL_SENTIMENT_SCORE.value)
    sent_label_col = col(NewsFields.OVERALL_SENTIMENT_LABEL.value)

    if not title_col or not url_col:
        return []

    df_view = df.copy()
    if time_col:
        df_view["_time_dt"] = df_view[time_col].map(_parse_dt)
        df_view = df_view.sort_values("_time_dt", ascending=False, na_position="last")

    items: list[NewsItem] = []
    for _, row in df_view.iterrows():
        title = _clean_str(row.get(title_col))
        url = _clean_str(row.get(url_col))
        if not title or not url:
            continue

        time_published = _clean_str(row.get(time_col)) if time_col else None
        summary = _clean_str(row.get(summary_col)) if summary_col else None

        icon_url = None
        if icon_col:
            icon_url = _clean_str(row.get(icon_col))
        if not icon_url and banner_col:
            icon_url = _clean_str(row.get(banner_col))

        sentiment_score = (
            _clean_float(row.get(sent_score_col)) if sent_score_col else None
        )
        sentiment_label = (
            _clean_str(row.get(sent_label_col)) if sent_label_col else None
        )

        items.append(
            NewsItem(
                title=title,
                url=url,
                time_published=time_published,
                summary=summary,
                icon_url=icon_url,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
            )
        )

    return items


def render_news_feed(
    items: Iterable[NewsItem],
    *,
    spec: NewsFeedSpec = NewsFeedSpec(),
    key: str = "news_feed",
    columns: int = 1,
) -> None:
    """Render a clean, scalable news feed UI (no dataframes)."""
    items = list(items)
    if not items:
        st.info("No news items available yet.")
        return

    with elements(key):
        feed_children = [
            _news_card(it, spec=spec, key=f"{key}_card_{i}")
            for i, it in enumerate(items[: spec.max_items])
        ]

        if columns <= 1:
            mui.Stack(spacing=1.25, children=feed_children)
        else:
            mui.Grid(
                container=True,
                spacing=1.5,
                children=[
                    mui.Grid(
                        key=f"{key}_item_{i}",
                        item=True,
                        xs=12,
                        md=6,
                        children=card,
                    )
                    for i, card in enumerate(feed_children)
                ],
            )
