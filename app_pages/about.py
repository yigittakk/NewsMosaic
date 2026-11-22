import streamlit as st

from ui_components import render_footer, render_page_header


render_page_header(
    "Project context",
    "About NewsMosaic",
    "An academic software and machine-learning project for structured exploration of English news corpora.",
    ["University of Bologna", "Machine Learning for Humanities", "2026"],
)

left, right = st.columns([0.72, 1.28], gap="large")
with left:
    st.image("https://github.com/yigittakk.png?size=320", width=180)
    st.markdown("### Yiğit Ak")
    st.write("Developer · University of Bologna")
    st.link_button("GitHub profile", "https://github.com/yigittakk", use_container_width=True)
    st.link_button("NewsMosaic repository", "https://github.com/yigittakk/NewsMosaic", use_container_width=True)

with right:
    st.markdown("## Academic context")
    st.write(
        "NewsMosaic was developed by **Yiğit Ak** at the **University of Bologna** within the "
        "**Machine Learning for Humanities** course. It combines supervised NLP model development "
        "with a research-oriented web application for article-level and corpus-level news analysis."
    )
    st.markdown("## Scope")
    st.write(
        "The application supports structured corpus upload and validation, theme classification, "
        "linguistic bias detection, named entity recognition, uncertainty and data-quality warnings, "
        "interactive exploration, article inspection, and enriched export."
    )
    st.markdown("## Current prototype boundary")
    st.write(
        "The public Streamlit deployment is intentionally lightweight and inference-only. "
        "Automatic news collection, real-time monitoring, fact-checking, misinformation detection, "
        "in-app model training, and unrestricted multilingual analysis remain outside the current scope."
    )

st.markdown(
    '<div class="nm-callout"><b>Research use.</b> The public interface is designed for demonstration and small interactive corpora. Large-scale experimental processing belongs to the offline batch pipeline.</div>',
    unsafe_allow_html=True,
)

render_footer()
