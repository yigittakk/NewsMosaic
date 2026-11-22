import pandas as pd
import streamlit as st

from ui_components import (
    apply_dashboard_filters,
    entity_bar_figure,
    plotly_config,
    prepare_dashboard_frame,
    render_footer,
    render_page_header,
    show_article_explorer,
    show_bias_view,
    show_overview,
    show_theme_view,
    show_trend_view,
)


render_page_header(
    "Corpus exploration",
    "Dashboard",
    "Explore the latest analysed corpus without rerunning the NLP models. Filters update the current view only.",
    ["Overview", "Themes", "Bias", "Entities", "Trends", "Articles"],
)

if "corpus_result" not in st.session_state:
    st.info("No corpus result is available in this session yet. Run Corpus Analysis first.")
    if st.button("Go to Corpus Analysis", type="primary"):
        st.switch_page("app_pages/corpus_analysis.py")
    render_footer()
    st.stop()

source_result = st.session_state["corpus_result"]
analyzed = prepare_dashboard_frame(source_result)
if analyzed.empty:
    st.warning("The current corpus does not contain analyzed rows.")
    render_footer()
    st.stop()

filtered = apply_dashboard_filters(analyzed)
if filtered.empty:
    st.warning("No articles match the current filters.")
    render_footer()
    st.stop()

view = st.radio(
    "Dashboard view",
    ["Overview", "Themes", "Bias", "Entities", "Trends", "Articles"],
    horizontal=True,
    label_visibility="collapsed",
)

if view == "Overview":
    show_overview(filtered, source_result)
elif view == "Themes":
    show_theme_view(filtered)
elif view == "Bias":
    show_bias_view(filtered)
elif view == "Entities":
    entity_type = st.selectbox("Entity type", ["Persons", "Organizations", "Locations"], label_visibility="collapsed")
    mapping = {
        "Persons": ("persons", "Most frequent persons", "#7180f5"),
        "Organizations": ("organizations", "Most frequent organizations", "#9a7bd8"),
        "Locations": ("locations", "Most frequent locations", "#55b7c7"),
    }
    column, title, color = mapping[entity_type]
    fig = entity_bar_figure(filtered, column, title, color)
    if fig is None:
        st.info("No entities detected in the current selection.")
    else:
        st.plotly_chart(fig, use_container_width=True, config=plotly_config())
        st.caption("Counts refer to articles in which the deduplicated entity appears.")
elif view == "Trends":
    show_trend_view(filtered)
else:
    show_article_explorer(filtered)

st.markdown('<div class="nm-section">Export</div>', unsafe_allow_html=True)
st.download_button(
    "Download enriched CSV",
    data=source_result.to_csv(index=False).encode("utf-8"),
    file_name="newsmosaic_enriched_results.csv",
    mime="text/csv",
    use_container_width=True,
)

render_footer()
