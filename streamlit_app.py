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
)


@st.cache_resource
def get_analyzer():
    """
    Creates one lightweight single-article coordinator.
    """

    return NewsAnalyzer()


@st.cache_resource
def get_corpus_analyzer():
    """
    Creates one lightweight corpus coordinator.
    """

    return CorpusAnalyzer()


def show_entity_list(title, entities):
    """
    Displays one named-entity group.
    """

    st.markdown(f"#### {title}")

    if not entities:
        st.caption("No entities detected.")
        return

    for entity in entities:
        st.write(f"• {entity}")


def show_single_article_results(result):
    """
    Displays the output of one article analysis.
    """

    st.divider()
    st.header("Analysis Results")

    st.subheader("1. Theme Classification")

    theme_col1, theme_col2 = st.columns(2)

    with theme_col1:
        st.metric("Predicted Theme", result["theme"])

    with theme_col2:
        st.metric(
            "Confidence",
            f'{result["theme_confidence"]:.1%}',
        )

    if result["theme_uncertain"]:
        st.warning(
            "The theme prediction is below the calibrated "
            f"confidence threshold ({Config.THEME_THRESHOLD:.3f})."
        )
    else:
        st.success(
            "The theme prediction is above the calibrated "
            "confidence threshold."
        )

    st.subheader("2. Linguistic Bias")

    bias_col1, bias_col2, bias_col3 = st.columns(3)

    mean_bias = result["mean_bias_probability"]
    bias_ratio = result["bias_ratio"]

    with bias_col1:
        st.metric(
            "Mean Bias Probability",
            f"{mean_bias:.1%}" if mean_bias is not None else "N/A",
        )

    with bias_col2:
        st.metric(
            "Bias Ratio",
            f"{bias_ratio:.1%}" if bias_ratio is not None else "N/A",
        )

    with bias_col3:
        st.metric(
            "Analyzed Sentences",
            result["bias_sentence_count"],
        )

    st.caption(
        "Bias Ratio = proportion of analyzed sentences whose "
        f"predicted bias probability is at least {Config.BIAS_THRESHOLD}."
    )

    st.subheader("3. Named Entity Recognition")

    st.metric("Unique Entities", result["ner_entity_count"])

    entity_col1, entity_col2 = st.columns(2)

    with entity_col1:
        show_entity_list("Persons", result["persons"])
        show_entity_list("Locations", result["locations"])

    with entity_col2:
        show_entity_list("Organizations", result["organizations"])
        show_entity_list("Miscellaneous", result["misc_entities"])

    st.divider()

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
        label="Download Result as JSON",
        data=json.dumps(
            export_result,
            indent=2,
            ensure_ascii=False,
        ),
        file_name="newsmosaic_analysis.json",
        mime="application/json",
        use_container_width=True,
    )


def get_top_entities(series, limit=10):
    """
    Counts pipe-separated entity strings from corpus results.
    """

    counter = Counter()

    for value in series.dropna():
        for entity in str(value).split(" | "):
            entity = entity.strip()

            if entity:
                counter[entity] += 1

    return counter.most_common(limit)


def show_top_entities(title, values):
    """
    Displays a compact entity frequency table.
    """

    st.markdown(f"#### {title}")

    if not values:
        st.caption("No entities detected.")
        return

    entity_table = pd.DataFrame(
        values,
        columns=["Entity", "Articles"],
    )

    st.dataframe(
        entity_table,
        hide_index=True,
        use_container_width=True,
    )


def show_corpus_dashboard(result):
    """
    Displays simple corpus-level summaries.
    """

    analyzed = result[result["analysis_status"] == "analyzed"].copy()

    if analyzed.empty:
        st.warning("No valid articles were analyzed.")
        return

    theme_counts = analyzed["predicted_theme"].value_counts()
    most_common_theme = theme_counts.index[0]

    mean_bias = pd.to_numeric(
        analyzed["mean_bias_probability"],
        errors="coerce",
    ).mean()

    entity_total = pd.to_numeric(
        analyzed["ner_entity_count"],
        errors="coerce",
    ).sum()

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Analyzed Articles", len(analyzed))

    with metric_col2:
        st.metric("Most Common Theme", most_common_theme)

    with metric_col3:
        st.metric("Average Bias Probability", f"{mean_bias:.1%}")

    with metric_col4:
        st.metric("Extracted Entities", int(entity_total))

    st.subheader("Theme Distribution")

    theme_chart = theme_counts.rename_axis("Theme").to_frame("Articles")
    st.bar_chart(theme_chart)

    entity_col1, entity_col2, entity_col3 = st.columns(3)

    with entity_col1:
        show_top_entities(
            "Top Persons",
            get_top_entities(analyzed["persons"]),
        )

    with entity_col2:
        show_top_entities(
            "Top Organizations",
            get_top_entities(analyzed["organizations"]),
        )

    with entity_col3:
        show_top_entities(
            "Top Locations",
            get_top_entities(analyzed["locations"]),
        )


st.title("📰 NewsMosaic")

st.caption(
    "A research-oriented platform for English news analysis"
)

with st.expander("About the analysis", expanded=False):
    st.write(
        "Theme classification uses a 16-class model. "
        "Low-confidence theme predictions are marked as uncertain."
    )
    st.write(
        "Bias analysis is performed at sentence level and aggregated "
        "to article-level measures."
    )
    st.write(
        "Named Entity Recognition extracts persons, organizations, "
        "locations, and miscellaneous entities."
    )

single_tab, corpus_tab = st.tabs(
    ["Single Article", "Corpus Analysis"]
)


with single_tab:
    st.subheader("Single Article Analysis")

    st.write(
        "Paste one English news article and run the three final NLP models."
    )

    article_text = st.text_area(
        "Article text",
        height=320,
        placeholder="Paste an English news article here...",
        key="single_article_text",
    )

    analyze_button = st.button(
        "Analyze Article",
        type="primary",
        use_container_width=True,
        key="single_analyze_button",
    )

    if analyze_button:
        if not article_text.strip():
            st.warning(
                "Please enter an article before running the analysis."
            )
        else:
            analyzer = get_analyzer()
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_single_progress(value, message):
                progress_bar.progress(value)
                status_text.write(message)

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
        show_single_article_results(
            st.session_state["single_result"]
        )


with corpus_tab:
    st.subheader("Corpus Analysis")

    st.write(
        "Upload a CSV file, select the article-text column, and enrich "
        "the corpus with theme, bias, and named-entity predictions."
    )

    st.info(
        f"Online demo limit: {Config.MAX_CORPUS_ARTICLES} rows per run. "
        "The limit protects the free deployment from excessive memory "
        "and CPU use."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"],
        key="corpus_file",
    )

    if uploaded_file is not None:
        try:
            corpus_df = pd.read_csv(uploaded_file)
        except Exception as error:
            st.error("The CSV file could not be read.")
            st.exception(error)
            corpus_df = None

        if corpus_df is not None:
            row_count = len(corpus_df)
            column_count = len(corpus_df.columns)

            info_col1, info_col2 = st.columns(2)

            with info_col1:
                st.metric("Rows", row_count)

            with info_col2:
                st.metric("Columns", column_count)

            if row_count == 0:
                st.error("The uploaded CSV is empty.")

            elif row_count > Config.MAX_CORPUS_ARTICLES:
                st.error(
                    f"This file has {row_count} rows. The online demo "
                    f"accepts at most {Config.MAX_CORPUS_ARTICLES} rows."
                )

            elif column_count == 0:
                st.error("No columns were found in the uploaded CSV.")

            else:
                default_index = 0

                likely_text_columns = [
                    "text",
                    "plain_text",
                    "article",
                    "article_text",
                    "content",
                ]

                for candidate in likely_text_columns:
                    if candidate in corpus_df.columns:
                        default_index = list(corpus_df.columns).index(candidate)
                        break

                text_column = st.selectbox(
                    "Article text column",
                    options=list(corpus_df.columns),
                    index=default_index,
                )

                empty_text_count = (
                    corpus_df[text_column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                    .eq("")
                    .sum()
                )

                st.write(
                    f"Validation: **{row_count - empty_text_count}** valid "
                    f"article(s), **{empty_text_count}** empty text row(s)."
                )

                with st.expander("Preview uploaded data", expanded=False):
                    st.dataframe(
                        corpus_df.head(10),
                        use_container_width=True,
                    )

                analyze_corpus_button = st.button(
                    "Analyze Corpus",
                    type="primary",
                    use_container_width=True,
                    key="corpus_analyze_button",
                    disabled=(row_count == 0 or empty_text_count == row_count),
                )

                if analyze_corpus_button:
                    corpus_analyzer = get_corpus_analyzer()
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    def update_corpus_progress(value, message):
                        progress_bar.progress(value)
                        status_text.write(message)

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
        st.header("Corpus Results")

        show_corpus_dashboard(corpus_result)

        st.subheader("Enriched Corpus")
        st.dataframe(
            corpus_result,
            use_container_width=True,
        )

        csv_data = corpus_result.to_csv(
            index=False,
        ).encode("utf-8")

        st.download_button(
            label="Download Enriched CSV",
            data=csv_data,
            file_name="newsmosaic_enriched_results.csv",
            mime="text/csv",
            use_container_width=True,
        )


st.divider()

st.caption(
    "NewsMosaic is an academic prototype. Model outputs are predictions "
    "and should not be interpreted as verified factual judgments."
)
