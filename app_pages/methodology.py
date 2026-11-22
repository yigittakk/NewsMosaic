import streamlit as st

from ui_components import (
    methodology_interpretation,
    methodology_models,
    methodology_pipeline,
    methodology_system,
    render_footer,
    render_page_header,
)


render_page_header(
    "Methods & model cards",
    "Methodology",
    "A product-facing explanation of how NewsMosaic processes data, how the deployed models were evaluated, and how outputs should be interpreted.",
    ["Pipeline", "Model cards", "Interpretation", "System design"],
)

st.markdown("## 1. Processing pipeline")
methodology_pipeline()
st.divider()

st.markdown("## 2. Deployed model cards")
methodology_models()
st.divider()

st.markdown("## 3. Interpretation guidance")
methodology_interpretation()
st.divider()

st.markdown("## 4. System design")
methodology_system()

render_footer()
