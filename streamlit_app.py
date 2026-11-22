import json
from collections import Counter

import pandas as pd
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
    .block-container {
        max-width: 1240px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.18);
    }

    .nm-hero {
        padding: 1.5rem 1.6rem;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 18px;
        margin-bottom: 1.1rem;
        background: linear-gradient(135deg, rgba(81, 99, 255, 0.10), rgba(0, 180, 170, 0.06));
    }

    .nm-kicker {
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-weight: 700;
        opacity: 0.72;
        margin-bottom: 0.35rem;
    }

    .nm-hero h1 {
        margin: 0;
        padding: 0;
        font-size: 2.35rem;
        line-height: 1.05;
    }

    .nm-hero p {
        margin: 0.7rem 0 0 0;
        max-width: 800px;
        opacity: 0.82;
        font-size: 1.02rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 14px;
        padding: 0.8rem 0.9rem;
        background: rgba(128, 128, 128, 0.035);
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 12px;
        overflow: hidden;
    }

    .nm-section {
        margin-top: 1.4rem;
        margin-bottom: 0.45rem;
        font-size: 1.1rem;
        font-weight: 700;
    }

    .nm-muted {
        opacity: 0.72;
        font-size: 0.9rem;
    }

    .nm-pill {
        display: inline-block;
        padding: 0.22rem 0.55rem;
        border-radius: 999px;
        border: 1px solid rgba(128, 128, 128, 0.22);
        margin: 0.1rem 0.2rem 0.1rem 0;
        font-size: 0.86rem;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 10px;
        min-height: 2.8rem;
        font-weight: 650;
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
    if value is None:
        return "N/A"
    return str(value).replace("_", " ").title()


def show_entity_chips(title, entities):
    st.markdown(f"**{title}**")

    if not entities:
        st.caption("No entities detected.")
        return

    chips = "".join(
        f'<span class="nm-pill">{entity}</span>'
        for entity in entities
    )
    st.markdown(chips, unsafe_allow_html=True)


def show_single_article_results(result):
    st.markdown('<div class="nm-section">Analysis summary</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Theme", pretty_label(result["theme"]))
    with col2:
        st.metric("Theme confidence", f'{result["theme_confidence"]:.1%}')
    with col3:
        bias_value = result["mean_bias_probability"]
        st.metric("Mean bias probability", f"{bias_value:.1%}" if bias_value is not None else "N/A")
    with col4:
        st.metric("Unique entities", result["ner_entity_count"])

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
        with b1:
            bias_ratio = result["bias_ratio"]
            st.metric("Bias ratio", f"{bias_ratio:.1%}" if bias_ratio is not None else "N/A")
        with b2:
            st.metric("Analyzed sentences", result["bias_sentence_count"])
        st.caption(
            "Bias Ratio is the share of analyzed sentences with predicted bias "
            f"probability ≥ {Config.BIAS_THRESHOLD}."
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


def get_top_entities(series, limit=10):
    counter = Counter()

    for value in series.dropna():
        for entity in str(value).split(" | "):
            entity = entity.strip()
            if entity:
                counter[entity] += 1

    return counter.most_common(limit)


def show_top_entities(title, values):
    st.markdown(f"**{title}**")

    if not values:
        st.caption("No entities detected.")
        return

    entity_table = pd.DataFrame(values, columns=["Entity", "Articles"])
    st.dataframe(entity_table, hide_index=True, use_container_width=True)


def find_date_column(dataframe):
    likely_columns = [
        "date",
        "published_date",
        "publication_date",
        "published",
        "datetime",
        "timestamp",
    ]

    lower_map = {str(column).lower(): column for column in dataframe.columns}

    for candidate in likely_columns:
        if candidate in lower_map:
            return lower_map[candidate]

    return None


def show_time_trends(analyzed):
    date_column = find_date_column(analyzed)

    if date_column is None:
        return

    dates = pd.to_datetime(analyzed[date_column], errors="coerce")
    valid_dates = dates.notna()

    if valid_dates.sum() < 2:
        return

    trend_data = analyzed.loc[valid_dates].copy()
    trend_data["_year"] = dates.loc[valid_dates].dt.year.values

    if trend_data["_year"].nunique() < 2:
        return

    st.markdown('<div class="nm-section">Time trends</div>', unsafe_allow_html=True)
    st.caption(f"Detected date column: {date_column}")

    trend_col1, trend_col2 = st.columns(2)

    with trend_col1:
        yearly_articles = trend_data.groupby("_year").size().rename("Articles")
        st.markdown("**Articles by year**")
        st.bar_chart(yearly_articles)

    with trend_col2:
        trend_data["mean_bias_probability"] = pd.to_numeric(
            trend_data["mean_bias_probability"], errors="coerce"
        )
        yearly_bias = trend_data.groupby("_year")["mean_bias_probability"].mean().dropna()
        st.markdown("**Average bias probability by year**")
        if yearly_bias.empty:
            st.caption("No valid bias values available for the detected dates.")
        else:
            st.line_chart(yearly_bias)


def show_corpus_dashboard(result):
    analyzed = result[result["analysis_status"] == "analyzed"].copy()

    if analyzed.empty:
        st.warning("No valid articles were analyzed.")
        return

    theme_counts = analyzed["predicted_theme"].value_counts()
    most_common_theme = pretty_label(theme_counts.index[0])

    confidence = pd.to_numeric(analyzed["theme_confidence"], errors="coerce")
    mean_confidence = confidence.mean()

    uncertainty = analyzed["theme_uncertain"].fillna(False).astype(bool)
    coverage = 1 - uncertainty.mean()

    mean_bias = pd.to_numeric(
        analyzed["mean_bias_probability"], errors="coerce"
    ).mean()

    entity_total = pd.to_numeric(
        analyzed["ner_entity_count"], errors="coerce"
    ).sum()

    st.markdown('<div class="nm-section">Corpus overview</div>', unsafe_allow_html=True)

    row1 = st.columns(4)
    row1[0].metric("Analyzed articles", len(analyzed))
    row1[1].metric("Most common theme", most_common_theme)
    row1[2].metric("Theme coverage", f"{coverage:.1%}")
    row1[3].metric("Mean theme confidence", f"{mean_confidence:.1%}")

    row2 = st.columns(4)
    row2[0].metric("Average bias probability", f"{mean_bias:.1%}")
    row2[1].metric("Uncertain themes", int(uncertainty.sum()))
    row2[2].metric("Extracted entities", int(entity_total))
    row2[3].metric("Avg. entities/article", f"{entity_total / len(analyzed):.1f}")

    chart_col1, chart_col2 = st.columns([1.35, 1])

    with chart_col1:
        st.markdown('<div class="nm-section">Theme distribution</div>', unsafe_allow_html=True)
        theme_chart = theme_counts.rename_axis("Theme").to_frame("Articles")
        theme_chart.index = [pretty_label(value) for value in theme_chart.index]
        st.bar_chart(theme_chart)

    with chart_col2:
        st.markdown('<div class="nm-section">Theme quality</div>', unsafe_allow_html=True)
        quality_table = pd.DataFrame(
            {
                "Measure": [
                    "Above confidence threshold",
                    "Below confidence threshold",
                    "Mean confidence",
                ],
                "Value": [
                    f"{coverage:.1%}",
                    f"{uncertainty.mean():.1%}",
                    f"{mean_confidence:.1%}",
                ],
            }
        )
        st.dataframe(quality_table, hide_index=True, use_container_width=True)
        st.caption(
            "Coverage refers to model predictions above the calibrated theme "
            "confidence threshold; it is not an accuracy estimate."
        )

    st.markdown('<div class="nm-section">Entity prominence</div>', unsafe_allow_html=True)
    entity_col1, entity_col2, entity_col3 = st.columns(3)

    with entity_col1:
        show_top_entities("Top persons", get_top_entities(analyzed["persons"]))
    with entity_col2:
        show_top_entities("Top organizations", get_top_entities(analyzed["organizations"]))
    with entity_col3:
        show_top_entities("Top locations", get_top_entities(analyzed["locations"]))

    show_time_trends(analyzed)


with st.sidebar:
    st.markdown("## NewsMosaic")
    st.caption("Research-oriented news corpus analysis")
    st.divider()
    st.markdown("**Models**")
    st.write("Theme · RoBERTa")
    st.write("Bias · ModernBERT")
    st.write("NER · BERT")
    st.divider()
    st.markdown("**Online demo safeguards**")
    st.write(f"Up to {Config.MAX_CORPUS_ARTICLES} articles")
    st.write(f"Up to {Config.MAX_UPLOAD_MB} MB per CSV")
    st.write(f"Up to {Config.MAX_ARTICLE_CHARS:,} characters/article")
    st.divider()
    st.caption(
        "Larger corpora should be processed with the offline pipeline."
    )


st.markdown(
    """
    <div class="nm-hero">
        <div class="nm-kicker">One corpus · Three NLP tasks · One workflow</div>
        <h1>NewsMosaic</h1>
        <p>
            Analyze English news with theme classification, linguistic bias detection,
            and named entity recognition. Inspect individual articles or enrich a small
            research corpus directly in the browser.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

single_tab, corpus_tab, methodology_tab = st.tabs(
    ["Single Article", "Corpus Analysis", "Methodology"]
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
            f"This article exceeds the online demo limit of "
            f"{Config.MAX_ARTICLE_CHARS:,} characters."
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
    st.subheader("Corpus Analysis")
    st.caption(
        "Upload a CSV, choose the article-text column, validate the file, "
        "and export an enriched corpus."
    )

    st.info(
        f"Online demo: up to {Config.MAX_CORPUS_ARTICLES} rows, "
        f"{Config.MAX_UPLOAD_MB} MB per CSV, and "
        f"{Config.MAX_ARTICLE_CHARS:,} characters per article."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="corpus_file",
    )

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        file_too_large = file_size_mb > Config.MAX_UPLOAD_MB

        if file_too_large:
            st.error(
                f"This file is {file_size_mb:.2f} MB. The online demo limit is "
                f"{Config.MAX_UPLOAD_MB} MB."
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
            file_cols[3].metric("Row limit", Config.MAX_CORPUS_ARTICLES)

            if row_count == 0:
                st.error("The uploaded CSV is empty.")
            elif row_count > Config.MAX_CORPUS_ARTICLES:
                st.error(
                    f"This file has {row_count} rows. The online demo accepts "
                    f"at most {Config.MAX_CORPUS_ARTICLES} rows."
                )
            elif column_count == 0:
                st.error("No columns were found in the uploaded CSV.")
            else:
                likely_text_columns = [
                    "text",
                    "plain_text",
                    "article",
                    "article_text",
                    "content",
                ]
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
                validation_cols[0].metric("Ready for analysis", valid_count)
                validation_cols[1].metric("Empty text", int(empty_text_count))
                validation_cols[2].metric("Too long", int(too_long_count))

                if empty_text_count or too_long_count:
                    st.warning(
                        "Invalid rows are preserved in the exported corpus but are not "
                        "sent to the NLP models. Their analysis_status explains why."
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
        st.subheader("Corpus Results")
        show_corpus_dashboard(corpus_result)

        st.markdown('<div class="nm-section">Article explorer</div>', unsafe_allow_html=True)
        st.dataframe(corpus_result, use_container_width=True)

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
        "NewsMosaic combines three supervised NLP tasks. Model outputs are "
        "predictions designed for research exploration, not verified factual judgments."
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("**Theme classification**")
        st.write("16-class RoBERTa classifier.")
        st.write(f"Confidence threshold: {Config.THEME_THRESHOLD:.3f}")
        st.caption("Predictions below the threshold are marked uncertain.")
    with m2:
        st.markdown("**Linguistic bias**")
        st.write("Sentence-level ModernBERT classifier.")
        st.write(f"Sentence threshold: {Config.BIAS_THRESHOLD}")
        st.caption("Article scores aggregate sentence-level model probabilities.")
    with m3:
        st.markdown("**Named entities**")
        st.write("BERT token-classification model.")
        st.write("PER · ORG · LOC · MISC")
        st.caption("Entities are deduplicated within each article.")

    st.divider()
    st.markdown("**Important interpretation note**")
    st.write(
        "Theme coverage is the share of predictions above the calibrated confidence "
        "threshold. It should not be interpreted as model accuracy. Bias outputs are "
        "model-estimated linguistic bias probabilities, not claims that an article or "
        "publisher is objectively biased."
    )


st.divider()
st.caption(
    "NewsMosaic · Academic prototype · English-language news analysis"
)
