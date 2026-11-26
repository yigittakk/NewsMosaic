import html
import json
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import Config
from corpus_analyzer import CorpusAnalyzer
from news_analyzer import NewsAnalyzer


CUSTOM_CSS = """
<style>
    :root {
        --nm-ink: #17213a;
        --nm-muted: #667085;
        --nm-border: #e6eaf2;
        --nm-card: #ffffff;
        --nm-bg: #f7f9fd;
        --nm-blue: #5b6cff;
        --nm-cyan: #37b6c9;
        --nm-violet: #8a67d5;
        --nm-peach: #f4a261;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 0%, rgba(91,108,255,.08), transparent 24rem),
            radial-gradient(circle at 95% 12%, rgba(55,182,201,.07), transparent 24rem),
            var(--nm-bg);
        color: var(--nm-ink);
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.35rem;
        padding-bottom: 4rem;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--nm-border);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.25rem;
    }

    .nm-brand {
        display: flex;
        gap: .7rem;
        align-items: center;
        margin-bottom: .2rem;
    }

    .nm-logo {
        width: 38px;
        height: 38px;
        border-radius: 12px;
        background: linear-gradient(135deg, #5b6cff, #37b6c9);
        box-shadow: 0 8px 22px rgba(91,108,255,.22);
    }

    .nm-brand-name {
        font-weight: 800;
        font-size: 1.16rem;
        letter-spacing: -.02em;
        color: var(--nm-ink);
    }

    .nm-hero {
        position: relative;
        overflow: hidden;
        padding: 2.05rem 2.15rem;
        border: 1px solid #e8ebf4;
        border-radius: 24px;
        margin-bottom: 1.2rem;
        background: linear-gradient(115deg, #ffffff 0%, #f4f6ff 62%, #eefafc 100%);
        box-shadow: 0 18px 55px rgba(31, 42, 68, .07);
    }

    .nm-hero::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -85px;
        top: -100px;
        border-radius: 50%;
        background: linear-gradient(145deg, rgba(91,108,255,.17), rgba(55,182,201,.05));
    }

    .nm-kicker {
        color: #5b6cff;
        font-size: .76rem;
        letter-spacing: .15em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: .45rem;
    }

    .nm-hero h1 {
        color: var(--nm-ink);
        margin: 0;
        padding: 0;
        font-size: clamp(2.25rem, 5vw, 3.45rem);
        line-height: .98;
        letter-spacing: -.055em;
    }

    .nm-hero p {
        color: #5f6b82;
        margin: .9rem 0 0 0;
        max-width: 790px;
        font-size: 1.02rem;
        line-height: 1.65;
    }

    .nm-badges {
        display: flex;
        flex-wrap: wrap;
        gap: .45rem;
        margin-top: 1.05rem;
    }

    .nm-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: .32rem .68rem;
        background: rgba(255,255,255,.82);
        border: 1px solid #e2e6f2;
        color: #46516b;
        font-size: .78rem;
        font-weight: 650;
    }

    .nm-side-intro {
        color: #667085;
        font-size: .82rem;
        line-height: 1.55;
        margin: .35rem 0 .8rem 0;
    }

    .nm-side-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8faff 100%);
        border: 1px solid #e5e9f3;
        border-radius: 14px;
        padding: .8rem .85rem;
        margin: .55rem 0;
        box-shadow: 0 6px 18px rgba(31,42,68,.035);
    }

    .nm-side-card-title {
        color: #27314b;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .48rem;
    }

    .nm-side-flow {
        display: flex;
        flex-wrap: wrap;
        gap: .3rem;
    }

    .nm-side-step {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        background: #eef1ff;
        border: 1px solid #dde2ff;
        color: #4653c7;
        padding: .22rem .46rem;
        font-size: .69rem;
        font-weight: 700;
    }

    .nm-side-row {
        display: flex;
        justify-content: space-between;
        gap: .75rem;
        padding: .26rem 0;
        border-bottom: 1px solid #edf0f6;
        font-size: .77rem;
        line-height: 1.35;
    }

    .nm-side-row:last-child {
        border-bottom: 0;
    }

    .nm-side-label {
        color: #7a8498;
    }

    .nm-side-value {
        color: #2d3750;
        font-weight: 750;
        text-align: right;
    }

    .nm-side-note {
        color: #6d778c;
        font-size: .74rem;
        line-height: 1.5;
    }

    .nm-author-card {
        display: flex;
        align-items: center;
        gap: .72rem;
        background: linear-gradient(145deg, #f4f7ff 0%, #ffffff 100%);
        border: 1px solid #dfe6f7;
        border-radius: 16px;
        padding: .8rem;
        margin: .65rem 0 .55rem 0;
        box-shadow: 0 8px 22px rgba(54,67,130,.055);
    }

    .nm-author-avatar {
        width: 54px;
        height: 54px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 12px rgba(31,42,68,.12);
        flex: 0 0 auto;
    }

    .nm-author-name {
        color: #202a44;
        font-size: .88rem;
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: .12rem;
    }

    .nm-author-meta {
        color: #6f7890;
        font-size: .72rem;
        line-height: 1.35;
    }

    .nm-author-course {
        margin-top: .5rem;
        padding-top: .52rem;
        border-top: 1px solid #e8ecf5;
        color: #5f6980;
        font-size: .72rem;
        line-height: 1.45;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: .35rem;
        background: rgba(255,255,255,.82);
        border: 1px solid var(--nm-border);
        border-radius: 14px;
        padding: .28rem;
        width: fit-content;
        box-shadow: 0 7px 24px rgba(31,42,68,.04);
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 10px;
        padding-left: 1rem;
        padding-right: 1rem;
        color: #697386;
        font-weight: 650;
    }

    [data-testid="stTabs"] [aria-selected="true"] {
        background: #eef1ff;
        color: #4454e8;
    }

    div[data-testid="stMetric"] {
        background: var(--nm-card);
        border: 1px solid var(--nm-border);
        border-radius: 16px;
        padding: 1rem 1rem .9rem 1rem;
        box-shadow: 0 8px 25px rgba(31,42,68,.045);
        min-height: 116px;
    }

    div[data-testid="stMetric"] label {
        color: #768197 !important;
        font-size: .78rem !important;
        font-weight: 700 !important;
        letter-spacing: .02em;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--nm-ink);
        font-weight: 790;
        letter-spacing: -.035em;
    }

    div[data-testid="stDataFrame"] {
        background: #fff;
        border: 1px solid var(--nm-border);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(31,42,68,.035);
    }

    .nm-section {
        margin-top: 1.75rem;
        margin-bottom: .55rem;
        color: var(--nm-ink);
        font-size: 1.1rem;
        font-weight: 800;
        letter-spacing: -.015em;
    }

    .nm-eyebrow {
        color: #6f7b91;
        font-size: .76rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin-bottom: .25rem;
    }

    .nm-panel {
        background: #ffffff;
        border: 1px solid var(--nm-border);
        border-radius: 18px;
        padding: 1.05rem 1.15rem;
        box-shadow: 0 8px 25px rgba(31,42,68,.035);
    }

    .nm-note {
        padding: .9rem 1rem;
        border-radius: 14px;
        background: #f0f5ff;
        border: 1px solid #dfe7ff;
        color: #4b5874;
        font-size: .9rem;
        line-height: 1.55;
    }

    .nm-pill {
        display: inline-block;
        padding: .27rem .62rem;
        border-radius: 999px;
        background: #f3f5fb;
        border: 1px solid #e4e8f2;
        color: #45516a;
        margin: .12rem .24rem .12rem 0;
        font-size: .84rem;
        font-weight: 620;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 720;
        border: 1px solid #dfe3ee;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(100deg, #5b6cff, #6676ff);
        border: none;
        box-shadow: 0 9px 20px rgba(91,108,255,.21);
    }

    [data-testid="stFileUploaderDropzone"] {
        background: #ffffff;
        border: 1.5px dashed #cad2e5;
        border-radius: 16px;
    }

    [data-testid="stExpander"] {
        background: #ffffff;
        border: 1px solid var(--nm-border);
        border-radius: 14px;
    }

    hr {
        border-color: #e8ebf2 !important;
    }
</style>
"""

PRODUCT_CSS = """
<style>
    .nm-product-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: .75rem;
        margin: .8rem 0 1.1rem 0;
    }
    .nm-insight-card, .nm-method-card, .nm-flow-card {
        background: rgba(255,255,255,.94);
        border: 1px solid #e4e8f2;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(31,42,68,.04);
    }
    .nm-insight-card {
        padding: 1rem 1.05rem;
        min-height: 108px;
    }
    .nm-insight-label {
        color: #7a8498;
        font-size: .72rem;
        font-weight: 800;
        letter-spacing: .07em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }
    .nm-insight-value {
        color: #17213a;
        font-size: 1.22rem;
        font-weight: 820;
        line-height: 1.15;
        letter-spacing: -.025em;
    }
    .nm-insight-copy {
        color: #697386;
        font-size: .8rem;
        line-height: 1.45;
        margin-top: .35rem;
    }
    .nm-flow-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: .65rem;
        margin: .85rem 0 1rem 0;
    }
    .nm-flow-card {
        padding: .95rem;
        min-height: 142px;
    }
    .nm-flow-number {
        width: 30px;
        height: 30px;
        border-radius: 9px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #eef1ff;
        color: #4e5ee8;
        font-weight: 850;
        font-size: .78rem;
        margin-bottom: .7rem;
    }
    .nm-flow-title {
        color: #26314c;
        font-size: .9rem;
        font-weight: 800;
        margin-bottom: .32rem;
    }
    .nm-flow-copy {
        color: #707a8f;
        font-size: .78rem;
        line-height: 1.48;
    }
    .nm-method-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: .8rem;
        margin: .75rem 0 1rem 0;
    }
    .nm-method-card {
        padding: 1.1rem;
    }
    .nm-method-tag {
        display: inline-block;
        border-radius: 999px;
        padding: .25rem .55rem;
        background: #f1f4ff;
        color: #5362d9;
        font-size: .69rem;
        font-weight: 800;
        margin-bottom: .65rem;
    }
    .nm-method-title {
        color: #17213a;
        font-weight: 840;
        font-size: 1rem;
        margin-bottom: .18rem;
    }
    .nm-method-sub {
        color: #788297;
        font-size: .78rem;
        margin-bottom: .8rem;
    }
    .nm-stat-row {
        display: flex;
        justify-content: space-between;
        gap: .75rem;
        padding: .38rem 0;
        border-top: 1px solid #edf0f6;
        font-size: .78rem;
    }
    .nm-stat-row span:first-child { color: #7a8498; }
    .nm-stat-row span:last-child { color: #28334c; font-weight: 780; text-align:right; }
    .nm-callout {
        background: linear-gradient(120deg, #f7f8ff, #f3fbfc);
        border: 1px solid #e2e7f2;
        border-radius: 16px;
        padding: 1rem 1.1rem;
        color: #566178;
        line-height: 1.58;
        font-size: .88rem;
        margin: .65rem 0;
    }
    .nm-divider-title {
        font-size: .78rem;
        color: #6f7a91;
        font-weight: 820;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin: 1.1rem 0 .55rem 0;
    }
    @media (max-width: 950px) {
        .nm-product-grid, .nm-method-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
        .nm-flow-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 640px) {
        .nm-product-grid, .nm-method-grid, .nm-flow-grid { grid-template-columns: 1fr; }
    }


    .nm-top-brand {
        display: flex;
        align-items: center;
        gap: .55rem;
        min-height: 2.55rem;
        font-weight: 850;
        letter-spacing: -.025em;
        color: var(--nm-ink);
        font-size: 1.02rem;
        white-space: nowrap;
    }

    .nm-top-brand-mark {
        width: 28px;
        height: 28px;
        border-radius: 9px;
        background: linear-gradient(135deg, #5b6cff, #37b6c9);
        box-shadow: 0 7px 18px rgba(91,108,255,.2);
        flex: 0 0 auto;
    }

    div[data-testid="stPageLink"] a {
        justify-content: center;
        min-height: 2.55rem;
        border: 1px solid #e2e7f0;
        border-radius: 999px;
        background: rgba(255,255,255,.92);
        color: #33405c;
        font-weight: 720;
        text-decoration: none;
        transition: all .15s ease;
    }

    div[data-testid="stPageLink"] a:hover {
        border-color: #bfc8ff;
        background: #f3f5ff;
        color: #4453d8;
        transform: translateY(-1px);
    }

</style>
"""


def inject_global_styles():
    """Emit application CSS on every Streamlit rerun/page navigation."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(PRODUCT_CSS, unsafe_allow_html=True)


@st.cache_resource
def get_analyzer():
    return NewsAnalyzer()


@st.cache_resource
def get_corpus_analyzer():
    return CorpusAnalyzer()


def pretty_label(value):
    if value is None or pd.isna(value):
        return "N/A"
    return str(value).replace("_", " ").title()


def show_entity_chips(title, entities):
    st.markdown(f"**{title}**")
    if not entities:
        st.caption("No entities detected.")
        return
    chips = "".join(
        f'<span class="nm-pill">{html.escape(str(entity))}</span>' for entity in entities
    )
    st.markdown(chips, unsafe_allow_html=True)


def parse_entities(value):
    if pd.isna(value) or not str(value).strip():
        return []
    return [item.strip() for item in str(value).split(" | ") if item.strip()]


def get_top_entities(series, limit=10):
    counter = Counter()
    for value in series.dropna():
        counter.update(parse_entities(value))
    return counter.most_common(limit)


def find_column(dataframe, candidates):
    lower_map = {str(column).lower(): column for column in dataframe.columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def derive_year(dataframe):
    year_column = find_column(dataframe, ["year", "analysis_year"])
    if year_column is not None:
        year = pd.to_numeric(dataframe[year_column], errors="coerce")
        return year.where(year.between(1900, 2100))

    date_column = find_column(
        dataframe,
        ["date", "published_date", "publication_date", "published", "datetime", "timestamp"],
    )
    if date_column is None:
        return pd.Series(pd.NA, index=dataframe.index, dtype="Float64")

    dates = pd.to_datetime(dataframe[date_column], errors="coerce")
    return dates.dt.year


def plotly_config():
    return {
        "displaylogo": False,
        "displayModeBar": False,
        "responsive": True,
        "scrollZoom": False,
    }


def polish_figure(fig, height=390, legend=False):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=18, r=18, t=54, b=22),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#536078", size=12),
        title=dict(font=dict(color="#17213a", size=16), x=0.01, xanchor="left"),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        showlegend=legend,
    )
    if legend:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                title=None,
            )
        )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#e8ebf2")
    fig.update_yaxes(showgrid=True, gridcolor="#eef1f6", zeroline=False)
    return fig


def show_single_article_results(result):
    st.markdown('<div class="nm-section">Analysis summary</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Theme", pretty_label(result["theme"]))
    col2.metric("Theme confidence", f'{result["theme_confidence"]:.1%}')
    bias_value = result["mean_bias_probability"]
    col3.metric("Mean bias probability", f"{bias_value:.1%}" if bias_value is not None else "N/A")
    col4.metric("Entities", result["ner_entity_count"])

    if result["theme_uncertain"]:
        st.warning(
            "Theme prediction is below the calibrated confidence threshold "
            f"({Config.THEME_THRESHOLD:.3f}) and is marked as uncertain."
        )
    else:
        st.success("Theme prediction is above the calibrated confidence threshold.")

    bias_col, entity_col = st.columns([.9, 1.1])
    with bias_col:
        st.markdown('<div class="nm-section">Bias signal</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        bias_ratio = result["bias_ratio"]
        b1.metric("Sentence bias ratio", f"{bias_ratio:.1%}" if bias_ratio is not None else "N/A")
        b2.metric("Sentences", result["bias_sentence_count"])
        st.markdown(
            f'<div class="nm-note">Mean bias probability averages sentence-level predictions. '
            f'The ratio reports the share of sentences at or above {Config.BIAS_THRESHOLD}. '
            f'These are linguistic model signals, not fact-checking or political judgments.</div>',
            unsafe_allow_html=True,
        )

    with entity_col:
        st.markdown('<div class="nm-section">Named entities</div>', unsafe_allow_html=True)
        show_entity_chips("Persons", result["persons"])
        show_entity_chips("Organizations", result["organizations"])
        show_entity_chips("Locations", result["locations"])
        show_entity_chips("Miscellaneous", result["misc_entities"])

    export_result = {
        "theme": result["theme"],
        "theme_confidence": result["theme_confidence"],
        "theme_uncertain": result["theme_uncertain"],
        "mean_bias_probability": result["mean_bias_probability"],
        "bias_ratio": result["bias_ratio"],
        "bias_sentence_count": result["bias_sentence_count"],
        "persons": result["persons"],
        "organizations": result["organizations"],
        "locations": result["locations"],
        "misc_entities": result["misc_entities"],
        "ner_entity_count": result["ner_entity_count"],
    }
    st.download_button(
        "Download JSON result",
        data=json.dumps(export_result, indent=2, ensure_ascii=False),
        file_name="newsmosaic_analysis.json",
        mime="application/json",
        use_container_width=True,
    )


def prepare_dashboard_frame(result):
    analyzed = result[result["analysis_status"] == "analyzed"].copy()
    if analyzed.empty:
        return analyzed

    analyzed["_theme"] = analyzed["predicted_theme"].map(pretty_label)
    analyzed["_confidence"] = pd.to_numeric(analyzed["theme_confidence"], errors="coerce")
    analyzed["_bias"] = pd.to_numeric(analyzed["mean_bias_probability"], errors="coerce")
    analyzed["_bias_ratio"] = pd.to_numeric(analyzed["bias_ratio_0705"], errors="coerce")
    analyzed["_entity_count"] = pd.to_numeric(analyzed["ner_entity_count"], errors="coerce").fillna(0)
    analyzed["_uncertain"] = analyzed["theme_uncertain"].fillna(False).astype(bool)
    analyzed["_year"] = derive_year(analyzed)

    source_column = find_column(analyzed, ["source", "publisher", "sitename", "news_source"])
    analyzed["_source"] = (
        analyzed[source_column].fillna("Unknown").astype(str)
        if source_column is not None
        else "Unknown"
    )

    title_column = find_column(analyzed, ["title", "headline", "article_title"])
    if title_column is not None:
        analyzed["_title"] = analyzed[title_column].fillna("Untitled").astype(str)
    else:
        analyzed["_title"] = [f"Article {i + 1}" for i in range(len(analyzed))]

    return analyzed


def apply_dashboard_filters(analyzed):
    with st.expander("Filter this analysis", expanded=False):
        f1, f2, f3 = st.columns(3)
        themes = sorted(analyzed["_theme"].dropna().unique().tolist())
        selected_themes = f1.multiselect("Theme", themes, placeholder="All themes")

        years = sorted(int(year) for year in analyzed["_year"].dropna().unique())
        selected_years = f2.multiselect("Year", years, placeholder="All years") if years else []

        sources = sorted(analyzed["_source"].dropna().unique().tolist())
        selected_sources = f3.multiselect("Source", sources, placeholder="All sources")

        f4, f5, f6 = st.columns(3)
        confidence_range = f4.slider(
            "Theme confidence", 0.0, 1.0, (0.0, 1.0), 0.05
        )
        bias_range = f5.slider(
            "Mean bias probability", 0.0, 1.0, (0.0, 1.0), 0.05
        )
        certainty = f6.selectbox("Theme certainty", ["All", "Certain only", "Uncertain only"])

    filtered = analyzed.copy()
    if selected_themes:
        filtered = filtered[filtered["_theme"].isin(selected_themes)]
    if selected_years:
        filtered = filtered[filtered["_year"].isin(selected_years)]
    if selected_sources:
        filtered = filtered[filtered["_source"].isin(selected_sources)]

    filtered = filtered[
        filtered["_confidence"].between(*confidence_range, inclusive="both")
        & filtered["_bias"].between(*bias_range, inclusive="both")
    ]
    if certainty == "Certain only":
        filtered = filtered[~filtered["_uncertain"]]
    elif certainty == "Uncertain only":
        filtered = filtered[filtered["_uncertain"]]

    st.caption(f"Current view: {len(filtered)} of {len(analyzed)} analyzed articles.")
    return filtered


def show_overview(filtered, source_result):
    theme_counts = filtered["_theme"].value_counts()
    lead_theme = theme_counts.index[0]
    lead_share = theme_counts.iloc[0] / len(filtered)
    coverage = (~filtered["_uncertain"]).mean()
    mean_bias = filtered["_bias"].mean()
    entity_mentions = int(filtered["_entity_count"].sum())

    top_entity_counter = Counter()
    for column in ["persons", "organizations", "locations"]:
        for value in filtered[column].dropna():
            top_entity_counter.update(parse_entities(value))
    top_entity = top_entity_counter.most_common(1)[0][0] if top_entity_counter else "None detected"

    st.markdown(
        f"""
        <div class="nm-product-grid">
            <div class="nm-insight-card">
                <div class="nm-insight-label">Leading theme</div>
                <div class="nm-insight-value">{html.escape(lead_theme)}</div>
                <div class="nm-insight-copy">{lead_share:.0%} of articles in the current view.</div>
            </div>
            <div class="nm-insight-card">
                <div class="nm-insight-label">Theme coverage</div>
                <div class="nm-insight-value">{coverage:.0%}</div>
                <div class="nm-insight-copy">Predictions above the calibrated confidence threshold.</div>
            </div>
            <div class="nm-insight-card">
                <div class="nm-insight-label">Mean bias probability</div>
                <div class="nm-insight-value">{mean_bias:.1%}</div>
                <div class="nm-insight-copy">Average article-level linguistic bias probability.</div>
            </div>
            <div class="nm-insight-card">
                <div class="nm-insight-label">Most visible entity</div>
                <div class="nm-insight-value">{html.escape(str(top_entity))}</div>
                <div class="nm-insight-copy">Top person, organization, or location in the current view.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Analyzed articles", len(filtered))
    k2.metric("Mean theme confidence", f'{filtered["_confidence"].mean():.1%}')
    k3.metric("Uncertain themes", int(filtered["_uncertain"].sum()))
    k4.metric("Entity mentions", entity_mentions)

    invalid = source_result[source_result["analysis_status"] != "analyzed"]
    if not invalid.empty:
        counts = invalid["analysis_status"].value_counts().to_dict()
        parts = [f"{count} {status.replace('_', ' ')}" for status, count in counts.items()]
        st.info("Rows retained but not analyzed: " + ", ".join(parts) + ".")

    preview_cols = ["_title", "_theme", "_confidence", "_bias", "_source"]
    preview = filtered[preview_cols].copy().head(8)
    preview.columns = ["Article", "Theme", "Confidence", "Bias", "Source"]
    preview["Confidence"] = preview["Confidence"].map(lambda x: f"{x:.1%}")
    preview["Bias"] = preview["Bias"].map(lambda x: f"{x:.1%}")
    st.markdown('<div class="nm-divider-title">Corpus snapshot</div>', unsafe_allow_html=True)
    st.dataframe(preview, use_container_width=True, hide_index=True)


def theme_distribution_figure(filtered):
    stats = (
        filtered.groupby("_theme", as_index=False)
        .agg(Articles=("_theme", "size"), MeanConfidence=("_confidence", "mean"))
        .sort_values("Articles", ascending=True)
    )
    fig = go.Figure(
        go.Bar(
            x=stats["Articles"],
            y=stats["_theme"],
            orientation="h",
            marker=dict(color="#7180f5"),
            customdata=stats[["MeanConfidence"]],
            hovertemplate="<b>%{y}</b><br>Articles: %{x}<br>Mean confidence: %{customdata[0]:.1%}<extra></extra>",
        )
    )
    fig.update_layout(title="Theme distribution")
    fig.update_xaxes(title="Articles", dtick=1 if stats["Articles"].max() <= 12 else None)
    fig.update_yaxes(title=None, showgrid=False)
    return polish_figure(fig, height=max(390, 31 * len(stats) + 140))


def show_theme_view(filtered):
    coverage = (~filtered["_uncertain"]).mean()
    c1, c2, c3 = st.columns(3)
    c1.metric("Theme coverage", f"{coverage:.1%}")
    c2.metric("Mean confidence", f'{filtered["_confidence"].mean():.1%}')
    c3.metric("Uncertain articles", int(filtered["_uncertain"].sum()))

    st.plotly_chart(theme_distribution_figure(filtered), use_container_width=True, config=plotly_config())

    stats = (
        filtered.groupby("_theme", as_index=False)
        .agg(Articles=("_theme", "size"), MeanConfidence=("_confidence", "mean"), Uncertain=("_uncertain", "sum"))
        .sort_values("Articles", ascending=False)
    )
    stats["Share"] = stats["Articles"] / len(filtered)
    table = stats.rename(columns={"_theme": "Theme"})[["Theme", "Articles", "Share", "MeanConfidence", "Uncertain"]]
    table["Share"] = table["Share"].map(lambda x: f"{x:.1%}")
    table["MeanConfidence"] = table["MeanConfidence"].map(lambda x: f"{x:.1%}")
    st.caption("Confidence is shown as context; theme coverage is not an accuracy estimate.")
    st.dataframe(table, use_container_width=True, hide_index=True)


def show_bias_view(filtered):
    mean_bias = filtered["_bias"].mean()
    median_bias = filtered["_bias"].median()
    sentence_ratio = filtered["_bias_ratio"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("Mean Bias Probability", f"{mean_bias:.1%}")
    c2.metric("Median Bias Probability", f"{median_bias:.1%}")
    c3.metric("Mean sentence bias ratio", f"{sentence_ratio:.1%}")

    bins = max(5, min(12, len(filtered)))
    fig = px.histogram(
        filtered,
        x="_bias",
        nbins=bins,
        color_discrete_sequence=["#55b7c7"],
        labels={"_bias": "Mean bias probability"},
        title="Distribution of article-level bias signals",
    )
    fig.add_vline(
        x=mean_bias,
        line_dash="dash",
        line_color="#5969e8",
        annotation_text=f"Mean {mean_bias:.1%}",
        annotation_position="top right",
    )
    fig.update_xaxes(tickformat=".0%", range=[0, 1], title="Mean bias probability")
    fig.update_yaxes(title="Articles", dtick=1 if len(filtered) <= 25 else None)
    polish_figure(fig, height=430)
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())
    st.markdown(
        f'<div class="nm-note">Article mean bias probability is the average sentence-level model score (not the share of biased articles). '
        f'The sentence bias ratio separately reports the share of sentences scoring at or above {Config.BIAS_THRESHOLD}. '
        f'Neither measure evaluates factual accuracy or political truthfulness.</div>',
        unsafe_allow_html=True,
    )


def entity_bar_figure(filtered, column, title, color):
    values = get_top_entities(filtered[column], limit=10)
    if not values:
        return None
    frame = pd.DataFrame(values, columns=["Entity", "Articles"]).sort_values("Articles")
    fig = go.Figure(
        go.Bar(
            x=frame["Articles"],
            y=frame["Entity"],
            orientation="h",
            marker=dict(color=color),
            hovertemplate="<b>%{y}</b><br>Articles: %{x}<extra></extra>",
        )
    )
    fig.update_layout(title=title)
    fig.update_xaxes(title="Articles", dtick=1 if frame["Articles"].max() <= 12 else None)
    fig.update_yaxes(title=None, showgrid=False)
    return polish_figure(fig, height=max(380, 32 * len(frame) + 130))




def show_trend_view(filtered):
    trend = filtered.dropna(subset=["_year"]).copy()
    if trend.empty or trend["_year"].nunique() < 2:
        st.info("Add a year/date column with at least two years to unlock temporal analysis.")
        return

    trend["_year"] = trend["_year"].astype(int)

    st.markdown("#### Bias signal over time")
    yearly = (
        trend.groupby("_year", as_index=False)
        .agg(
            MeanBias=("_bias", "mean"),
            Articles=("_year", "size"),
            Coverage=("_uncertain", lambda s: 1 - s.mean()),
        )
        .sort_values("_year")
    )
    fig = go.Figure(
        go.Scatter(
            x=yearly["_year"],
            y=yearly["MeanBias"],
            mode="lines+markers",
            line=dict(color="#55b7c7", width=3),
            marker=dict(size=9, color="#55b7c7"),
            customdata=yearly[["Articles"]],
            hovertemplate="<b>%{x}</b><br>Mean bias: %{y:.1%}<br>Articles: %{customdata[0]}<extra></extra>",
        )
    )
    fig.update_layout(title="Mean bias probability by year")
    fig.update_xaxes(title="Year", dtick=1)
    fig.update_yaxes(title="Mean bias probability", tickformat=".0%", rangemode="tozero")
    polish_figure(fig, height=410)
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())

    summary = yearly.rename(columns={"_year": "Year"})
    summary["MeanBias"] = summary["MeanBias"].map(lambda x: f"{x:.1%}")
    summary["Coverage"] = summary["Coverage"].map(lambda x: f"{x:.1%}")
    summary.columns = ["Year", "Mean bias", "Articles", "Theme coverage"]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("#### Theme composition over time")
    counts = trend.groupby(["_year", "_theme"]).size().rename("Articles").reset_index()
    top_themes = trend["_theme"].value_counts().head(6).index.tolist()
    counts = counts[counts["_theme"].isin(top_themes)].copy()
    totals = trend.groupby("_year").size().rename("Total").reset_index()
    counts = counts.merge(totals, on="_year", how="left")
    counts["Share"] = counts["Articles"] / counts["Total"]
    years = sorted(trend["_year"].unique())
    matrix = (
        counts.pivot(index="_theme", columns="_year", values="Share")
        .reindex(index=top_themes, columns=years)
        .fillna(0)
    )
    text_matrix = matrix.map(lambda x: f"{x:.0%}")
    fig = go.Figure(
        data=go.Heatmap(
            z=matrix.values,
            x=[str(year) for year in matrix.columns],
            y=matrix.index.tolist(),
            text=text_matrix.values,
            texttemplate="%{text}",
            colorscale=[[0, "#f8f9ff"], [.45, "#dce3ff"], [1, "#6878ef"]],
            colorbar=dict(title="Share", tickformat=".0%", thickness=12),
            hovertemplate="<b>%{y}</b><br>Year: %{x}<br>Share: %{z:.1%}<extra></extra>",
        )
    )
    fig.update_layout(title="Top theme shares by year")
    fig.update_xaxes(title="Year", side="bottom")
    fig.update_yaxes(title=None, autorange="reversed", showgrid=False)
    polish_figure(fig, height=max(390, 48 * len(matrix.index) + 150))
    st.plotly_chart(fig, use_container_width=True, config=plotly_config())
    st.caption("The heatmap shows the six most frequent themes in the current selection to keep the view readable.")

def show_article_explorer(filtered):
    search = st.text_input("Search article titles", placeholder="Type part of a headline...")
    explorer = filtered.copy()
    if search.strip():
        explorer = explorer[explorer["_title"].str.contains(search.strip(), case=False, na=False)]
    if explorer.empty:
        st.info("No article matches this search.")
        return

    explorer["_article_label"] = [
        f"{idx + 1:02d} · {title[:100]}" for idx, title in enumerate(explorer["_title"].tolist())
    ]
    selected_label = st.selectbox("Open article", explorer["_article_label"].tolist())
    row = explorer.loc[explorer["_article_label"] == selected_label].iloc[0]

    a, b, c, d = st.columns(4)
    a.metric("Theme", row["_theme"])
    b.metric("Confidence", f'{row["_confidence"]:.1%}')
    c.metric("Bias", f'{row["_bias"]:.1%}')
    d.metric("Entities", int(row["_entity_count"]))

    meta_bits = []
    if pd.notna(row["_year"]):
        meta_bits.append(str(int(row["_year"])))
    if row["_source"] != "Unknown":
        meta_bits.append(row["_source"])
    if meta_bits:
        st.caption(" · ".join(meta_bits))

    l, r = st.columns(2)
    with l:
        show_entity_chips("Persons", parse_entities(row.get("persons")))
        show_entity_chips("Organizations", parse_entities(row.get("organizations")))
    with r:
        show_entity_chips("Locations", parse_entities(row.get("locations")))
        show_entity_chips("Miscellaneous", parse_entities(row.get("misc_entities")))

    text_column = find_column(filtered, ["text", "plain_text", "article", "article_text", "content"])
    if text_column is not None:
        with st.expander("Read article text", expanded=True):
            st.write(str(row[text_column]))




def methodology_pipeline():
    st.markdown(
        """
        <div class="nm-callout"><b>One workflow, three supervised NLP tasks.</b> NewsMosaic validates structured English news, runs the selected final models, aggregates article-level outputs, and exposes the results for exploration and export.</div>
        <div class="nm-flow-grid">
            <div class="nm-flow-card"><div class="nm-flow-number">01</div><div class="nm-flow-title">Validate</div><div class="nm-flow-copy">Check the CSV structure, selected text field, missing text, article length, and online demo limits.</div></div>
            <div class="nm-flow-card"><div class="nm-flow-number">02</div><div class="nm-flow-title">Classify theme</div><div class="nm-flow-copy">Assign one of 16 news themes and retain the model confidence. Low-confidence outputs are flagged.</div></div>
            <div class="nm-flow-card"><div class="nm-flow-number">03</div><div class="nm-flow-title">Score language</div><div class="nm-flow-copy">Split the article into sentences, estimate lexical/linguistic bias per sentence, then aggregate to article level.</div></div>
            <div class="nm-flow-card"><div class="nm-flow-number">04</div><div class="nm-flow-title">Extract entities</div><div class="nm-flow-copy">Detect persons, organizations, locations, and miscellaneous named entities and deduplicate them per article.</div></div>
            <div class="nm-flow-card"><div class="nm-flow-number">05</div><div class="nm-flow-title">Explore & export</div><div class="nm-flow-copy">Aggregate the enriched corpus into focused views, inspect individual articles, and download the full results.</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )



def methodology_data_strategy():
    st.markdown(
        """
        <div class="nm-callout"><b>Dataset roles were kept separate.</b> Labeled external datasets were used to train and evaluate the supervised models, while CCNews was treated as the target news corpus. For theme adaptation, only a separate weakly labeled CCNews pool was used; the fixed final inference sample was excluded from that training pool.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Corpus collection and analysis scope")
    st.write(
        "The raw CCNews collection sampled 100,000 English-language records per year from "
        "2020 to 2024 (500,000 raw records in total, before cleaning and selection). "
        "The final offline research analysis used 125,000 articles (25,000 per year); "
        "the full raw collection was not analysed with the three final models. "
        "A separate non-holdout CCNews pool was used for metadata-derived theme weak supervision."
    )

    st.markdown("#### Dataset roles")
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Task": "Theme classification",
                    "Dataset": "HuffPost, IAB, AG News, NewsCatcher, MN-DS",
                    "Role": "Gold supervised training / validation / test",
                    "What we did": "Harmonized labels from five external supervised sources into the final 16-class taxonomy, removed unusable or duplicate rows, and created train/validation/test splits. The external test split was reserved for evaluation.",
                },
                {
                    "Task": "Theme classification",
                    "Dataset": "CCNews 2020–2024 weak-label pool",
                    "Role": "Target-domain adaptation",
                    "What we did": "Generated conservative weak theme labels from metadata such as categories and tags, removed ambiguous rows, balanced the weak set, and combined it with external gold training data for the final joint RoBERTa model.",
                },
                {
                    "Task": "Linguistic bias",
                    "Dataset": "BABE",
                    "Role": "Supervised fine-tuning / primary evaluation",
                    "What we did": "Fine-tuned ModernBERT on annotated sentence-level bias labels, evaluated on held-out BABE data, and calibrated the sentence decision threshold on validation data only.",
                },
                {
                    "Task": "Linguistic bias",
                    "Dataset": "MBIC",
                    "Role": "External robustness check",
                    "What we did": "Used as an additional out-of-dataset evaluation set to check whether the bias model generalized beyond BABE. It was not used to fit the final model.",
                },
                {
                    "Task": "Named entity recognition",
                    "Dataset": "CoNLL-2003",
                    "Role": "Supervised fine-tuning / evaluation",
                    "What we did": "Fine-tuned bert-base-cased for token classification and evaluated entity extraction for PER, ORG, LOC, and MISC labels on held-out CoNLL data.",
                },
                {
                    "Task": "All three tasks",
                    "Dataset": "Fixed CCNews reference corpus",
                    "Role": "Target inference / research analysis",
                    "What we did": "Applied the already selected models to a fixed 125,000-article sample (25,000 per year, 2020–2024). These outputs are model estimates, not ground-truth labels.",
                },
            ]
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Theme data preparation")
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            **External supervised theme dataset**

            - Sources: **HuffPost, IAB, AG News, NewsCatcher, MN-DS**
            - Final prepared dataset: **316,697 articles**
            - Train: **253,357**
            - Validation: **31,670**
            - Test: **31,670**
            - Content leakage check: **PASS**
            - External test data remained untouched during training and threshold calibration.
            """
        )
    with right:
        st.markdown(
            """
            **Target-domain weak supervision**

            - CCNews metadata was used only for conservative weak labeling.
            - The fixed final 125k inference corpus was excluded by exact-content hash.
            - Clean weak-label pool: **112,610 articles**
            - Balanced weak-label subset: **53,551 articles**
            - This subset was split **90% weak train / 10% weak validation** (stratified).
            - Only the **weak-training portion** was combined with external supervised training data for the final joint model.
            """
        )

    st.markdown(
        """
        <div class="nm-note"><b>Why this matters.</b> CCNews is the domain being studied, not a fully labeled benchmark. Keeping the final 125k reference corpus outside the adaptation set prevents the application from reporting training-set predictions as if they were independent research results.</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Final model-selection logic")
    st.markdown(
        """
        1. **Train on labeled data.** Each task began with an external supervised dataset appropriate to the task.
        2. **Evaluate on held-out data.** Model selection used validation/test metrics rather than CCNews output distributions.
        3. **Adapt theme classification cautiously.** A sequential weak-adaptation experiment improved target behavior but degraded external performance, so it was rejected.
        4. **Use the joint theme model.** The selected RoBERTa model combined external gold data with weak CCNews data and preserved external performance much better.
        5. **Freeze models before corpus analysis.** The final Theme, Bias, and NER models were then applied to the fixed CCNews sample without further training.
        """
    )

    st.caption(
        "Thresholds are calibrated decision rules, not guarantees of accuracy on CCNews. The theme confidence threshold was calibrated on external validation data; the bias threshold was calibrated on BABE validation data."
    )

def methodology_models():
    st.markdown(
        f"""
        <div class="nm-method-grid">
            <div class="nm-method-card">
                <div class="nm-method-tag">THEME CLASSIFICATION</div>
                <div class="nm-method-title">Joint RoBERTa</div>
                <div class="nm-method-sub">16-class supervised news theme classifier</div>
                <div class="nm-stat-row"><span>External test Macro-F1</span><span>0.835</span></div>
                <div class="nm-stat-row"><span>External test accuracy</span><span>0.857</span></div>
                <div class="nm-stat-row"><span>Confidence threshold</span><span>{Config.THEME_THRESHOLD:.3f}</span></div>
                <div class="nm-stat-row"><span>Output</span><span>Theme + confidence</span></div>
            </div>
            <div class="nm-method-card">
                <div class="nm-method-tag">LINGUISTIC BIAS</div>
                <div class="nm-method-title">ModernBERT</div>
                <div class="nm-method-sub">Sentence-level binary classifier with article aggregation</div>
                <div class="nm-stat-row"><span>BABE test Macro-F1</span><span>0.829</span></div>
                <div class="nm-stat-row"><span>BABE test accuracy</span><span>0.830</span></div>
                <div class="nm-stat-row"><span>Sentence threshold</span><span>{Config.BIAS_THRESHOLD:.3f}</span></div>
                <div class="nm-stat-row"><span>Output</span><span>Mean + sentence ratio</span></div>
            </div>
            <div class="nm-method-card">
                <div class="nm-method-tag">NAMED ENTITY RECOGNITION</div>
                <div class="nm-method-title">BERT base cased</div>
                <div class="nm-method-sub">CoNLL-2003 token classification</div>
                <div class="nm-stat-row"><span>Entity-level F1</span><span>0.889</span></div>
                <div class="nm-stat-row"><span>Token accuracy</span><span>0.970</span></div>
                <div class="nm-stat-row"><span>Entity types</span><span>PER · ORG · LOC · MISC</span></div>
                <div class="nm-stat-row"><span>Output</span><span>Deduplicated entities</span></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Reported evaluation metrics refer to held-out labeled evaluation data; corpus-level NewsMosaic outputs remain model estimates on the uploaded news data.")


def methodology_interpretation():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Theme outputs")
        st.write(
            "The classifier assigns a news theme and confidence score. Predictions below the calibrated threshold are marked uncertain. Theme coverage is the share above that threshold; it is not an estimate of corpus accuracy."
        )
        st.markdown("#### Bias outputs")
        st.write(
            "Bias is deliberately narrow: it represents lexical/linguistic signals learned from annotated sentences. The article mean averages sentence probabilities, while the sentence ratio measures the proportion of sentences above the decision threshold. These are model scores, not shares of objectively biased articles."
        )
    with col2:
        st.markdown("#### NER outputs")
        st.write(
            "Named entities support actor prominence analysis. NewsMosaic reports persons, organizations, locations, and miscellaneous entities, deduplicated within each article before aggregation."
        )
        st.markdown("#### What the app does not claim")
        st.write(
            "The system does not perform fact-checking, misinformation detection, political truth assessment, causal inference, or unrestricted multilingual analysis. Outputs should be interpreted as supervised model estimates."
        )

    st.markdown(
        '<div class="nm-note"><b>Research interpretation.</b> The dashboard is designed to surface patterns worth inspecting, not to replace reading the underlying articles or validating substantive claims with domain evidence.</div>',
        unsafe_allow_html=True,
    )


def methodology_system():
    st.markdown("#### Application architecture")
    st.code(
        "Browser\n  ↓\nStreamlit interface\n  ↓\nNewsAnalyzer / CorpusAnalyzer\n  ↓\nThemeClassifier → BiasClassifier → NERExtractor\n  ↓\nHugging Face model repositories\n  ↓\nDashboard + enriched CSV",
        language="text",
    )
    left, right = st.columns(2)
    with left:
        st.markdown("#### Deployment design")
        st.write(
            "The public prototype runs on Streamlit Community Cloud. Models are downloaded from public Hugging Face repositories and loaded sequentially so that only one transformer model is resident for a task stage at a time."
        )
        st.write(
            f"Online safeguards: {Config.MAX_CORPUS_ARTICLES} articles, {Config.MAX_UPLOAD_MB} MB per CSV, and {Config.MAX_ARTICLE_CHARS:,} characters per article."
        )
    with right:
        st.markdown("#### Scale boundary")
        st.write(
            "The deployed interface is an academic interactive prototype. Large research corpora should use the offline batch pipeline, where the same task logic can run without Community Cloud resource constraints."
        )
        st.write("The web application performs inference only; it does not train or fine-tune models inside the user interface.")





def render_top_navigation(items):
    """Render a persistent horizontal product navigation bar."""
    with st.container(border=True):
        brand, *nav_cols = st.columns(
            [1.25, 0.85, 1.15, 1.25, 0.95, 1.05, 0.75],
            gap="small",
            vertical_alignment="center",
        )

        with brand:
            st.markdown(
                """
                <div class="nm-top-brand">
                    <span class="nm-top-brand-mark"></span>
                    <span>NewsMosaic</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        for column, (page, label, icon) in zip(nav_cols, items):
            with column:
                st.page_link(
                    page,
                    label=label,
                    icon=icon,
                    use_container_width=True,
                )


def render_sidebar_footer():
    """Render the persistent product/developer information below navigation."""
    with st.sidebar:
        st.markdown(
            """
            <div class="nm-author-card">
                <img class="nm-author-avatar" src="https://github.com/yigittakk.png?size=160" alt="Yiğit Ak">
                <div>
                    <div class="nm-author-name">Yiğit Ak</div>
                    <div class="nm-author-meta">Developer · University of Bologna</div>
                    <div class="nm-author-course">Machine Learning for Humanities · 2026</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="nm-side-card">
                <div class="nm-side-card-title">Online demo</div>
                <div class="nm-side-row"><span class="nm-side-label">Corpus</span><span class="nm-side-value">≤ {Config.MAX_CORPUS_ARTICLES} articles</span></div>
                <div class="nm-side-row"><span class="nm-side-label">CSV</span><span class="nm-side-value">≤ {Config.MAX_UPLOAD_MB} MB</span></div>
                <div class="nm-side-row"><span class="nm-side-label">Article</span><span class="nm-side-value">≤ {Config.MAX_ARTICLE_CHARS:,} chars</span></div>
                <div class="nm-side-row"><span class="nm-side-label">Language</span><span class="nm-side-value">English</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.link_button("GitHub · @yigittakk", "https://github.com/yigittakk", use_container_width=True)
        st.link_button("NewsMosaic repository", "https://github.com/yigittakk/NewsMosaic", use_container_width=True)


def render_page_header(kicker, title, copy, badges=None):
    badge_html = ""
    if badges:
        badge_html = '<div class="nm-badges">' + "".join(
            f'<span class="nm-badge">{html.escape(str(badge))}</span>' for badge in badges
        ) + "</div>"
    st.markdown(
        f"""
        <div class="nm-hero">
            <div class="nm-kicker">{html.escape(str(kicker))}</div>
            <h1>{html.escape(str(title))}</h1>
            <p>{html.escape(str(copy))}</p>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.divider()
    st.caption("NewsMosaic · Yiğit Ak · University of Bologna · Machine Learning for Humanities · 2026")
