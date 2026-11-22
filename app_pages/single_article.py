import streamlit as st

from config import Config
from ui_components import get_analyzer, render_footer, render_page_header, show_single_article_results


render_page_header(
    "Article analysis",
    "Single Article",
    "Paste an English news article and run the complete NewsMosaic inference pipeline without uploading a corpus.",
    ["Theme", "Bias", "NER"],
)

article_text = st.text_area(
    "Article text",
    height=330,
    placeholder="Paste an English news article here...",
    key="single_article_text",
)
char_count = len(article_text.strip())
st.caption(f"{char_count:,} / {Config.MAX_ARTICLE_CHARS:,} characters")

too_long = char_count > Config.MAX_ARTICLE_CHARS
if too_long:
    st.error(f"This article exceeds the online demo limit of {Config.MAX_ARTICLE_CHARS:,} characters.")

if st.button("Analyze article", type="primary", use_container_width=True, disabled=too_long):
    if not article_text.strip():
        st.warning("Please enter an article before running the analysis.")
    else:
        analyzer = get_analyzer()
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(value, message):
            progress_bar.progress(value)
            status_text.caption(message)

        try:
            st.session_state["single_result"] = analyzer.analyze(
                article_text,
                progress_callback=update_progress,
            )
        except Exception as error:
            st.error("The analysis could not be completed.")
            st.exception(error)
        finally:
            progress_bar.empty()
            status_text.empty()

if "single_result" in st.session_state:
    show_single_article_results(st.session_state["single_result"])

render_footer()
