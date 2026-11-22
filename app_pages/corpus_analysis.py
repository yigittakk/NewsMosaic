import pandas as pd
import streamlit as st

from config import Config
from ui_components import get_corpus_analyzer, render_footer, render_page_header


render_page_header(
    "Corpus workflow",
    "Corpus Analysis",
    "Upload and validate a structured CSV, run the three NLP tasks, then continue to the dedicated dashboard page for exploration.",
    ["Upload", "Validate", "Analyse", "Export"],
)

st.markdown(
    f'<div class="nm-note"><b>Online demo capacity.</b> Up to {Config.MAX_CORPUS_ARTICLES} articles, {Config.MAX_UPLOAD_MB} MB per CSV, and {Config.MAX_ARTICLE_CHARS:,} characters per article. Invalid rows remain in the export but are not sent to the models.</div>',
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader("Upload CSV", type=["csv"], key="corpus_file")

if uploaded_file is not None:
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > Config.MAX_UPLOAD_MB:
        st.error(f"This file is {file_size_mb:.2f} MB. The online demo limit is {Config.MAX_UPLOAD_MB} MB.")
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
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Rows", row_count)
        m2.metric("Columns", column_count)
        m3.metric("File size", f"{file_size_mb:.2f} MB")
        m4.metric("Demo limit", Config.MAX_CORPUS_ARTICLES)

        if row_count == 0:
            st.error("The uploaded CSV is empty.")
        elif row_count > Config.MAX_CORPUS_ARTICLES:
            st.error(f"This file has {row_count} rows. The online demo accepts at most {Config.MAX_CORPUS_ARTICLES} rows.")
        elif column_count == 0:
            st.error("No columns were found in the uploaded CSV.")
        else:
            likely_text_columns = ["text", "plain_text", "article", "article_text", "content"]
            default_index = next(
                (list(corpus_df.columns).index(candidate) for candidate in likely_text_columns if candidate in corpus_df.columns),
                0,
            )
            text_column = st.selectbox("Article text column", list(corpus_df.columns), index=default_index)

            text_series = corpus_df[text_column].fillna("").astype(str).str.strip()
            empty_text_count = int(text_series.eq("").sum())
            too_long_count = int(text_series.str.len().gt(Config.MAX_ARTICLE_CHARS).sum())
            valid_count = row_count - empty_text_count - too_long_count

            v1, v2, v3 = st.columns(3)
            v1.metric("Ready", valid_count)
            v2.metric("Empty text", empty_text_count)
            v3.metric("Too long", too_long_count)

            if valid_count == row_count:
                st.success("Validation passed. All rows are ready for analysis.")
            else:
                st.warning("Rows with empty or over-length text are preserved but skipped during model inference.")

            with st.expander("Preview uploaded data", expanded=False):
                st.dataframe(corpus_df.head(10), use_container_width=True)

            if st.button("Analyze corpus", type="primary", use_container_width=True, disabled=(valid_count == 0)):
                corpus_analyzer = get_corpus_analyzer()
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(value, message):
                    progress_bar.progress(value)
                    status_text.caption(message)

                try:
                    st.session_state["corpus_result"] = corpus_analyzer.analyze(
                        dataframe=corpus_df,
                        text_column=text_column,
                        progress_callback=update_progress,
                    )
                    st.session_state["corpus_source_name"] = uploaded_file.name
                    st.session_state["corpus_text_column"] = text_column
                    st.success("Corpus analysis complete. Open the dashboard to explore the results.")
                except Exception as error:
                    st.error("The corpus analysis could not be completed.")
                    st.exception(error)
                finally:
                    progress_bar.empty()
                    status_text.empty()

if "corpus_result" in st.session_state:
    result = st.session_state["corpus_result"]
    analyzed_count = int((result["analysis_status"] == "analyzed").sum())
    st.markdown('<div class="nm-section">Current analysis</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    c1.metric("Analyzed", analyzed_count)
    c2.metric("Rows retained", len(result))
    c3.metric("Source", st.session_state.get("corpus_source_name", "Uploaded CSV"))

    b1, b2 = st.columns(2)
    if b1.button("Open Dashboard", type="primary", use_container_width=True):
        st.switch_page("app_pages/dashboard.py")
    csv_data = result.to_csv(index=False).encode("utf-8")
    b2.download_button(
        "Download enriched CSV",
        data=csv_data,
        file_name="newsmosaic_enriched_results.csv",
        mime="text/csv",
        use_container_width=True,
    )

render_footer()
