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


st.set_page_config(
    page_title="NewsMosaic",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)


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

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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


def get_top_entities(series, limit=12):
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
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "responsive": True,
    }


def polish_figure(fig, height=380, legend=True):
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=16, r=16, t=42, b=18),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#45516a", size=12),
        title_font=dict(color="#17213a", size=15),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            title=None,
        ),
        showlegend=legend,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf0f6", zeroline=False)
    fig.update_yaxes(showgrid=False, zeroline=False)
    return fig


def show_single_article_results(result):
    st.markdown('<div class="nm-section">Analysis summary</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Theme", pretty_label(result["theme"]))
    col2.metric("Theme confidence", f'{result["theme_confidence"]:.1%}')
    bias_value = result["mean_bias_probability"]
    col3.metric("Mean bias probability", f"{bias_value:.1%}" if bias_value is not None else "N/A")
    col4.metric("Unique entities", result["ner_entity_count"])

    if result["theme_uncertain"]:
        st.warning(
            "Theme prediction is below the calibrated confidence threshold "
            f"({Config.THEME_THRESHOLD:.3f}) and is marked as uncertain."
        )
    else:
        st.success("Theme prediction is above the calibrated confidence threshold.")

    left, right = st.columns([1, 1])
    with left:
        st.markdown('<div class="nm-section">Linguistic bias</div>', unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        bias_ratio = result["bias_ratio"]
        b1.metric("Bias ratio", f"{bias_ratio:.1%}" if bias_ratio is not None else "N/A")
        b2.metric("Analyzed sentences", result["bias_sentence_count"])
        st.markdown(
            f'<div class="nm-note">Bias Ratio is the share of analyzed sentences with predicted '
            f'bias probability ≥ {Config.BIAS_THRESHOLD}. It is a model-estimated linguistic signal, '
            f'not a factual judgment about the publisher.</div>',
            unsafe_allow_html=True,
        )

    with right:
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
        label="Download JSON result",
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
    st.markdown('<div class="nm-section">Explore the corpus</div>', unsafe_allow_html=True)
    with st.expander("Dashboard filters", expanded=True):
        f1, f2, f3 = st.columns(3)

        themes = sorted(analyzed["_theme"].dropna().unique().tolist())
        selected_themes = f1.multiselect(
            "Theme",
            themes,
            placeholder="All themes",
        )

        years = sorted(int(year) for year in analyzed["_year"].dropna().unique())
        selected_years = f2.multiselect(
            "Year",
            years,
            placeholder="All years",
        ) if years else []

        sources = sorted(analyzed["_source"].dropna().unique().tolist())
        selected_sources = f3.multiselect(
            "Source",
            sources,
            placeholder="All sources",
        )

        f4, f5, f6 = st.columns(3)
        confidence_range = f4.slider(
            "Theme confidence",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
        )
        bias_range = f5.slider(
            "Mean bias probability",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.05,
        )
        certainty = f6.selectbox(
            "Theme certainty",
            ["All", "Certain only", "Uncertain only"],
        )

    filtered = analyzed.copy()
    if selected_themes:
        filtered = filtered[filtered["_theme"].isin(selected_themes)]
    if selected_years:
        filtered = filtered[filtered["_year"].isin(selected_years)]
    if selected_sources:
        filtered = filtered[filtered["_source"].isin(selected_sources)]

    filtered = filtered[
        filtered["_confidence"].between(confidence_range[0], confidence_range[1], inclusive="both")
        & filtered["_bias"].between(bias_range[0], bias_range[1], inclusive="both")
    ]

    if certainty == "Certain only":
        filtered = filtered[~filtered["_uncertain"]]
    elif certainty == "Uncertain only":
        filtered = filtered[filtered["_uncertain"]]

    st.caption(f"Showing {len(filtered)} of {len(analyzed)} analyzed articles.")
    return filtered


def show_kpis(filtered):
    if filtered.empty:
        return

    theme_counts = filtered["_theme"].value_counts()
    most_common_theme = theme_counts.index[0]
    coverage = 1 - filtered["_uncertain"].mean()
    mean_confidence = filtered["_confidence"].mean()
    mean_bias = filtered["_bias"].mean()
    entity_total = filtered["_entity_count"].sum()

    row1 = st.columns(4)
    row1[0].metric("Articles", len(filtered))
    row1[1].metric("Leading theme", most_common_theme)
    row1[2].metric("Theme coverage", f"{coverage:.1%}")
    row1[3].metric("Mean confidence", f"{mean_confidence:.1%}")

    row2 = st.columns(4)
    row2[0].metric("Average bias", f"{mean_bias:.1%}")
    row2[1].metric("Uncertain themes", int(filtered["_uncertain"].sum()))
    row2[2].metric("Unique entity mentions", int(entity_total))
    row2[3].metric("Entities / article", f"{entity_total / len(filtered):.1f}")


def show_theme_visuals(filtered):
    left, right = st.columns([1.55, 1])

    with left:
        theme_stats = (
            filtered.groupby("_theme", as_index=False)
            .agg(Articles=("_theme", "size"), MeanConfidence=("_confidence", "mean"))
            .sort_values("Articles", ascending=True)
        )
        fig = px.bar(
            theme_stats,
            x="Articles",
            y="_theme",
            orientation="h",
            color="_theme",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            custom_data=["MeanConfidence"],
            labels={"_theme": "Theme"},
            title="Theme distribution",
        )
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>Articles: %{x}<br>Mean confidence: %{customdata[0]:.1%}<extra></extra>"
        )
        fig.update_layout(yaxis_title=None, xaxis_title="Articles")
        polish_figure(fig, height=max(360, 34 * len(theme_stats) + 120), legend=False)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())

    with right:
        certain_count = int((~filtered["_uncertain"]).sum())
        uncertain_count = int(filtered["_uncertain"].sum())
        certainty_frame = pd.DataFrame(
            {"Status": ["Above threshold", "Below threshold"], "Articles": [certain_count, uncertain_count]}
        )
        fig = px.pie(
            certainty_frame,
            names="Status",
            values="Articles",
            hole=.68,
            color="Status",
            color_discrete_map={"Above threshold": "#5b6cff", "Below threshold": "#f4a261"},
            title="Theme confidence coverage",
        )
        fig.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>%{value} articles<extra></extra>")
        fig.add_annotation(
            text=f"<b>{certain_count / len(filtered):.0%}</b><br><span style='font-size:11px'>coverage</span>",
            x=.5,
            y=.5,
            showarrow=False,
            font=dict(color="#17213a", size=20),
        )
        polish_figure(fig, height=390, legend=True)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def show_bias_visuals(filtered):
    left, right = st.columns([1.2, 1])

    with left:
        fig = px.histogram(
            filtered,
            x="_bias",
            nbins=12,
            color_discrete_sequence=["#37b6c9"],
            labels={"_bias": "Mean bias probability"},
            title="Bias score distribution",
        )
        mean_bias = filtered["_bias"].mean()
        fig.add_vline(
            x=mean_bias,
            line_dash="dash",
            line_color="#5b6cff",
            annotation_text=f"Mean {mean_bias:.1%}",
            annotation_position="top right",
        )
        fig.update_xaxes(tickformat=".0%", range=[0, 1])
        fig.update_layout(yaxis_title="Articles")
        polish_figure(fig, height=360, legend=False)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())

    with right:
        theme_bias = (
            filtered.groupby("_theme", as_index=False)
            .agg(MeanBias=("_bias", "mean"), Articles=("_theme", "size"))
            .sort_values("MeanBias", ascending=False)
        )
        fig = px.bar(
            theme_bias,
            x="_theme",
            y="MeanBias",
            color="_theme",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            custom_data=["Articles"],
            labels={"_theme": "Theme", "MeanBias": "Mean bias probability"},
            title="Average bias by theme",
        )
        fig.update_traces(hovertemplate="<b>%{x}</b><br>Mean bias: %{y:.1%}<br>Articles: %{customdata[0]}<extra></extra>")
        fig.update_yaxes(tickformat=".0%", range=[0, max(.25, min(1.0, theme_bias["MeanBias"].max() * 1.25))])
        fig.update_xaxes(tickangle=-35)
        polish_figure(fig, height=360, legend=False)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def show_time_visuals(filtered):
    trend = filtered.dropna(subset=["_year"]).copy()
    if trend.empty or trend["_year"].nunique() < 2:
        return

    trend["_year"] = trend["_year"].astype(int)
    st.markdown('<div class="nm-section">Time trends</div>', unsafe_allow_html=True)

    left, right = st.columns([1.45, 1])
    with left:
        theme_year = (
            trend.groupby(["_year", "_theme"]).size().rename("Articles").reset_index()
        )
        theme_year["Share"] = theme_year.groupby("_year")["Articles"].transform(lambda s: s / s.sum())
        fig = px.bar(
            theme_year,
            x="_year",
            y="Share",
            color="_theme",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={"_year": "Year", "_theme": "Theme"},
            title="Theme mix by year",
            custom_data=["Articles"],
        )
        fig.update_traces(hovertemplate="%{fullData.name}<br>Share: %{y:.1%}<br>Articles: %{customdata[0]}<extra></extra>")
        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        polish_figure(fig, height=420, legend=True)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())

    with right:
        yearly = (
            trend.groupby("_year", as_index=False)
            .agg(MeanBias=("_bias", "mean"), MeanConfidence=("_confidence", "mean"), Articles=("_year", "size"))
        )
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=yearly["_year"],
                y=yearly["MeanBias"],
                mode="lines+markers",
                name="Bias",
                line=dict(color="#37b6c9", width=3),
                marker=dict(size=8),
                customdata=yearly[["Articles"]],
                hovertemplate="Year %{x}<br>Bias: %{y:.1%}<br>Articles: %{customdata[0]}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=yearly["_year"],
                y=yearly["MeanConfidence"],
                mode="lines+markers",
                name="Theme confidence",
                line=dict(color="#5b6cff", width=3),
                marker=dict(size=8),
                hovertemplate="Year %{x}<br>Confidence: %{y:.1%}<extra></extra>",
            )
        )
        fig.update_yaxes(tickformat=".0%", range=[0, 1])
        fig.update_layout(title="Model signals by year")
        polish_figure(fig, height=420, legend=True)
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def show_entity_visuals(filtered):
    st.markdown('<div class="nm-section">Entity prominence</div>', unsafe_allow_html=True)
    person_tab, org_tab, loc_tab = st.tabs(["Persons", "Organizations", "Locations"])

    for tab, column, title, color in [
        (person_tab, "persons", "Top persons", "#5b6cff"),
        (org_tab, "organizations", "Top organizations", "#8a67d5"),
        (loc_tab, "locations", "Top locations", "#37b6c9"),
    ]:
        with tab:
            values = get_top_entities(filtered[column], limit=15)
            if not values:
                st.caption("No entities detected in the current filter selection.")
                continue
            frame = pd.DataFrame(values, columns=["Entity", "Articles"]).sort_values("Articles")
            fig = px.bar(
                frame,
                x="Articles",
                y="Entity",
                orientation="h",
                color_discrete_sequence=[color],
                title=title,
            )
            fig.update_traces(hovertemplate="<b>%{y}</b><br>Articles: %{x}<extra></extra>")
            polish_figure(fig, height=max(340, 29 * len(frame) + 100), legend=False)
            st.plotly_chart(fig, use_container_width=True, config=plotly_config())


def show_article_explorer(filtered):
    st.markdown('<div class="nm-section">Article explorer</div>', unsafe_allow_html=True)
    if filtered.empty:
        return

    explorer = filtered.copy()
    explorer["_article_label"] = [
        f"{idx + 1:02d} · {title[:95]}" for idx, title in enumerate(explorer["_title"].tolist())
    ]
    selected_label = st.selectbox("Open an article", explorer["_article_label"].tolist())
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

    l, r = st.columns([1.05, 1])
    with l:
        show_entity_chips("Persons", parse_entities(row.get("persons")))
        show_entity_chips("Organizations", parse_entities(row.get("organizations")))
    with r:
        show_entity_chips("Locations", parse_entities(row.get("locations")))
        show_entity_chips("Miscellaneous", parse_entities(row.get("misc_entities")))

    text_column = find_column(
        filtered,
        ["text", "plain_text", "article", "article_text", "content"],
    )
    if text_column is not None:
        with st.expander("Read article text", expanded=False):
            st.write(str(row[text_column]))


def show_corpus_dashboard(result):
    analyzed = prepare_dashboard_frame(result)
    if analyzed.empty:
        st.warning("No valid articles were analyzed.")
        return

    filtered = apply_dashboard_filters(analyzed)
    if filtered.empty:
        st.warning("No articles match the current filters.")
        return

    show_kpis(filtered)

    st.markdown('<div class="nm-section">Theme landscape</div>', unsafe_allow_html=True)
    show_theme_visuals(filtered)

    st.markdown('<div class="nm-section">Bias landscape</div>', unsafe_allow_html=True)
    show_bias_visuals(filtered)

    show_time_visuals(filtered)
    show_entity_visuals(filtered)
    show_article_explorer(filtered)


with st.sidebar:
    st.markdown(
        """
        <div class="nm-brand">
            <div class="nm-logo"></div>
            <div><div class="nm-brand-name">NewsMosaic</div><div style="font-size:.76rem;color:#7b8497">Research dashboard</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Analysis stack**")
    st.caption("THEME")
    st.write("RoBERTa · 16 classes")
    st.caption("BIAS")
    st.write("ModernBERT · sentence-level")
    st.caption("NER")
    st.write("BERT · PER / ORG / LOC / MISC")
    st.divider()
    st.markdown("**Online demo limits**")
    st.write(f"{Config.MAX_CORPUS_ARTICLES} articles / run")
    st.write(f"{Config.MAX_UPLOAD_MB} MB CSV")
    st.write(f"{Config.MAX_ARTICLE_CHARS:,} chars / article")
    st.caption("Large research corpora should use the offline batch pipeline.")


st.markdown(
    f"""
    <div class="nm-hero">
        <div class="nm-kicker">Research-oriented news intelligence</div>
        <h1>NewsMosaic</h1>
        <p>
            Turn English news into an explorable research view. Classify themes, estimate
            linguistic bias signals, extract named entities, compare years, filter sources,
            inspect individual articles, and export the enriched corpus.
        </p>
        <div class="nm-badges">
            <span class="nm-badge">Theme classification</span>
            <span class="nm-badge">Bias analysis</span>
            <span class="nm-badge">Named entities</span>
            <span class="nm-badge">Interactive corpus dashboard</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

single_tab, corpus_tab, methodology_tab = st.tabs(
    ["Single Article", "Corpus Dashboard", "Methodology"]
)


with single_tab:
    st.subheader("Single Article Analysis")
    st.caption("Paste one English news article and run all three final NLP models.")

    article_text = st.text_area(
        "Article text",
        height=300,
        placeholder="Paste an English news article here...",
        key="single_article_text",
    )

    char_count = len(article_text.strip())
    st.caption(f"{char_count:,} / {Config.MAX_ARTICLE_CHARS:,} characters")

    single_too_long = char_count > Config.MAX_ARTICLE_CHARS
    if single_too_long:
        st.error(
            f"This article exceeds the online demo limit of {Config.MAX_ARTICLE_CHARS:,} characters."
        )

    analyze_button = st.button(
        "Analyze article",
        type="primary",
        use_container_width=True,
        key="single_analyze_button",
        disabled=single_too_long,
    )

    if analyze_button:
        if not article_text.strip():
            st.warning("Please enter an article before running the analysis.")
        else:
            analyzer = get_analyzer()
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_single_progress(value, message):
                progress_bar.progress(value)
                status_text.caption(message)

            try:
                single_result = analyzer.analyze(
                    article_text,
                    progress_callback=update_single_progress,
                )
                st.session_state["single_result"] = single_result
            except Exception as error:
                st.error("The analysis could not be completed.")
                st.exception(error)
            finally:
                progress_bar.empty()
                status_text.empty()

    if "single_result" in st.session_state:
        show_single_article_results(st.session_state["single_result"])


with corpus_tab:
    st.subheader("Corpus Dashboard")
    st.caption(
        "Upload a CSV, validate it, run the three NLP tasks, then explore the results with interactive filters and charts."
    )

    st.markdown(
        f'<div class="nm-note">Online demo capacity: up to <b>{Config.MAX_CORPUS_ARTICLES} articles</b>, '
        f'<b>{Config.MAX_UPLOAD_MB} MB</b> per CSV, and <b>{Config.MAX_ARTICLE_CHARS:,} characters</b> per article. '
        f'Invalid rows stay in the export but are not sent to the models.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="corpus_file")

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        file_too_large = file_size_mb > Config.MAX_UPLOAD_MB

        if file_too_large:
            st.error(
                f"This file is {file_size_mb:.2f} MB. The online demo limit is {Config.MAX_UPLOAD_MB} MB."
            )
            corpus_df = None
        else:
            try:
                corpus_df = pd.read_csv(uploaded_file)
            except Exception as error:
                st.error("The CSV file could not be read.")
                st.exception(error)
                corpus_df = None

        if corpus_df is not None:
            row_count = len(corpus_df)
            column_count = len(corpus_df.columns)

            file_cols = st.columns(4)
            file_cols[0].metric("Rows", row_count)
            file_cols[1].metric("Columns", column_count)
            file_cols[2].metric("File size", f"{file_size_mb:.2f} MB")
            file_cols[3].metric("Demo limit", Config.MAX_CORPUS_ARTICLES)

            if row_count == 0:
                st.error("The uploaded CSV is empty.")
            elif row_count > Config.MAX_CORPUS_ARTICLES:
                st.error(
                    f"This file has {row_count} rows. The online demo accepts at most {Config.MAX_CORPUS_ARTICLES} rows."
                )
            elif column_count == 0:
                st.error("No columns were found in the uploaded CSV.")
            else:
                likely_text_columns = ["text", "plain_text", "article", "article_text", "content"]
                default_index = 0
                for candidate in likely_text_columns:
                    if candidate in corpus_df.columns:
                        default_index = list(corpus_df.columns).index(candidate)
                        break

                text_column = st.selectbox(
                    "Article text column",
                    options=list(corpus_df.columns),
                    index=default_index,
                )

                text_series = corpus_df[text_column].fillna("").astype(str).str.strip()
                empty_text_count = text_series.eq("").sum()
                too_long_count = text_series.str.len().gt(Config.MAX_ARTICLE_CHARS).sum()
                valid_count = row_count - empty_text_count - too_long_count

                validation_cols = st.columns(3)
                validation_cols[0].metric("Ready", valid_count)
                validation_cols[1].metric("Empty text", int(empty_text_count))
                validation_cols[2].metric("Too long", int(too_long_count))

                if empty_text_count or too_long_count:
                    st.warning(
                        "Invalid rows are preserved in the exported corpus but are not sent to the NLP models."
                    )
                else:
                    st.success("Validation passed. All rows are ready for analysis.")

                with st.expander("Preview uploaded data", expanded=False):
                    st.dataframe(corpus_df.head(10), use_container_width=True)

                analyze_corpus_button = st.button(
                    "Analyze corpus",
                    type="primary",
                    use_container_width=True,
                    key="corpus_analyze_button",
                    disabled=(valid_count == 0),
                )

                if analyze_corpus_button:
                    corpus_analyzer = get_corpus_analyzer()
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def update_corpus_progress(value, message):
                        progress_bar.progress(value)
                        status_text.caption(message)

                    try:
                        corpus_result = corpus_analyzer.analyze(
                            dataframe=corpus_df,
                            text_column=text_column,
                            progress_callback=update_corpus_progress,
                        )
                        st.session_state["corpus_result"] = corpus_result
                        st.session_state["corpus_source_name"] = uploaded_file.name
                    except Exception as error:
                        st.error("The corpus analysis could not be completed.")
                        st.exception(error)
                    finally:
                        progress_bar.empty()
                        status_text.empty()

    if "corpus_result" in st.session_state:
        corpus_result = st.session_state["corpus_result"]

        st.divider()
        st.subheader("Interactive Results")
        show_corpus_dashboard(corpus_result)

        st.markdown('<div class="nm-section">Enriched dataset</div>', unsafe_allow_html=True)
        st.dataframe(corpus_result, use_container_width=True, hide_index=True)

        csv_data = corpus_result.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download enriched CSV",
            data=csv_data,
            file_name="newsmosaic_enriched_results.csv",
            mime="text/csv",
            use_container_width=True,
        )


with methodology_tab:
    st.subheader("Methodology & interpretation")
    st.write(
        "NewsMosaic combines three supervised NLP tasks. Model outputs are predictions designed for research exploration, not verified factual judgments."
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("**Theme classification**")
        st.write("16-class RoBERTa classifier")
        st.write(f"Confidence threshold: {Config.THEME_THRESHOLD:.3f}")
        st.caption("Predictions below the threshold are marked uncertain.")
    with m2:
        st.markdown("**Linguistic bias**")
        st.write("Sentence-level ModernBERT classifier")
        st.write(f"Sentence threshold: {Config.BIAS_THRESHOLD}")
        st.caption("Article scores aggregate sentence-level model probabilities.")
    with m3:
        st.markdown("**Named entities**")
        st.write("BERT token-classification model")
        st.write("PER · ORG · LOC · MISC")
        st.caption("Entities are deduplicated within each article.")

    st.markdown('<div class="nm-section">Interpretation guardrails</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="nm-note"><b>Theme coverage</b> is the share of predictions above the calibrated confidence threshold; '
        'it is not an accuracy estimate. <b>Bias outputs</b> are model-estimated linguistic bias probabilities; they are not '
        'claims that an article or publisher is objectively biased.</div>',
        unsafe_allow_html=True,
    )


st.divider()
st.caption("NewsMosaic · Academic prototype · English-language news analysis")
