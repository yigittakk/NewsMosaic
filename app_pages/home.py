import streamlit as st

from ui_components import render_footer, render_page_header


render_page_header(
    "Research-oriented news intelligence",
    "NewsMosaic",
    "A single workflow for analysing English news with theme classification, linguistic bias detection, named entity recognition, corpus exploration, and enriched export.",
    ["Theme classification", "Linguistic bias", "Named entities", "Corpus exploration"],
)

left, right = st.columns([1.25, 0.75], gap="large")
with left:
    st.markdown("## From raw news to interpretable signals")
    st.write(
        "NewsMosaic connects three supervised NLP tasks in one research workflow. "
        "Use it for a single article or upload a structured CSV corpus, validate the input, "
        "run the deployed models, inspect uncertain outputs, explore patterns, and export enriched data."
    )
    c1, c2 = st.columns(2)
    if c1.button("Analyse one article", type="primary", use_container_width=True):
        st.switch_page("app_pages/single_article.py")
    if c2.button("Analyse a corpus", use_container_width=True):
        st.switch_page("app_pages/corpus_analysis.py")

with right:
    st.markdown(
        """
        <div class="nm-panel">
            <div class="nm-eyebrow">Academic context</div>
            <h3 style="margin:.15rem 0 .55rem 0;">University of Bologna</h3>
            <div style="color:#667085;line-height:1.6;">
                Developed by <b>Yiğit Ak</b> for the <b>Machine Learning for Humanities</b> course.
                The public application is an inference-only academic prototype.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="nm-section">Three coordinated models</div>', unsafe_allow_html=True)

model_theme, model_bias, model_ner = st.columns(3, gap="medium")

with model_theme:
    with st.container(border=True):
        st.caption("THEME CLASSIFICATION")
        st.markdown("### RoBERTa")
        st.caption("16-class supervised news theme classifier")
        a, b = st.columns(2)
        a.metric("Test Macro-F1", "0.835")
        b.metric("Threshold", "0.634")
        st.markdown("**Output**  \nTheme label + confidence")
        st.caption("Predictions below the calibrated confidence threshold are flagged as uncertain.")

with model_bias:
    with st.container(border=True):
        st.caption("LINGUISTIC BIAS")
        st.markdown("### ModernBERT")
        st.caption("Sentence-level linguistic signal with article aggregation")
        a, b = st.columns(2)
        a.metric("Test Macro-F1", "0.829")
        b.metric("Threshold", "0.705")
        st.markdown("**Output**  \nMean probability + sentence ratio")
        st.caption("The score reflects model-estimated lexical/linguistic bias, not a factual or political verdict.")

with model_ner:
    with st.container(border=True):
        st.caption("NAMED ENTITY RECOGNITION")
        st.markdown("### BERT base cased")
        st.caption("CoNLL-2003 token classification")
        a, b = st.columns(2)
        a.metric("Entity F1", "0.889")
        b.metric("Token accuracy", "0.970")
        st.markdown("**Entities**  \nPER · ORG · LOC · MISC")
        st.caption("Article-level entities are deduplicated for prominence analysis.")

st.markdown('<div class="nm-section">Workflow</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="nm-flow-grid">
        <div class="nm-flow-card"><div class="nm-flow-number">01</div><div class="nm-flow-title">Upload</div><div class="nm-flow-copy">Paste one article or provide a structured CSV corpus.</div></div>
        <div class="nm-flow-card"><div class="nm-flow-number">02</div><div class="nm-flow-title">Validate</div><div class="nm-flow-copy">Check file size, row count, text availability, and article length.</div></div>
        <div class="nm-flow-card"><div class="nm-flow-number">03</div><div class="nm-flow-title">Analyse</div><div class="nm-flow-copy">Run Theme, Bias, and NER sequentially with the deployed final models.</div></div>
        <div class="nm-flow-card"><div class="nm-flow-number">04</div><div class="nm-flow-title">Explore</div><div class="nm-flow-copy">Inspect corpus patterns, uncertainty, entities, and individual articles.</div></div>
        <div class="nm-flow-card"><div class="nm-flow-number">05</div><div class="nm-flow-title">Export</div><div class="nm-flow-copy">Download the original corpus enriched with model-generated fields.</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="nm-callout"><b>Interpretation matters.</b> NewsMosaic outputs are model estimates. Theme labels are not human gold labels, bias is a lexical/linguistic signal rather than a fact-check or political verdict, and NER reflects the entity types learned during fine-tuning.</div>',
    unsafe_allow_html=True,
)

render_footer()
