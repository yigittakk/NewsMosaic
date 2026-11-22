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
st.markdown(
    """
    <div class="nm-method-grid">
        <div class="nm-method-card">
            <div class="nm-method-tag">THEME</div>
            <div class="nm-method-title">RoBERTa classifier</div>
            <div class="nm-method-sub">16 news themes</div>
            <div class="nm-stat-row"><span>Test Macro-F1</span><span>0.8354</span></div>
            <div class="nm-stat-row"><span>Confidence threshold</span><span>0.6344</span></div>
            <div class="nm-stat-row"><span>Low confidence</span><span>Flagged uncertain</span></div>
        </div>
        <div class="nm-method-card">
            <div class="nm-method-tag">BIAS</div>
            <div class="nm-method-title">ModernBERT classifier</div>
            <div class="nm-method-sub">Sentence-level linguistic signal</div>
            <div class="nm-stat-row"><span>Test Macro-F1</span><span>0.8288</span></div>
            <div class="nm-stat-row"><span>Sentence threshold</span><span>0.705</span></div>
            <div class="nm-stat-row"><span>Article output</span><span>Mean + ratio</span></div>
        </div>
        <div class="nm-method-card">
            <div class="nm-method-tag">NER</div>
            <div class="nm-method-title">BERT token classifier</div>
            <div class="nm-method-sub">PER · ORG · LOC · MISC</div>
            <div class="nm-stat-row"><span>Entity-level F1</span><span>0.8893</span></div>
            <div class="nm-stat-row"><span>Output</span><span>Deduplicated entities</span></div>
            <div class="nm-stat-row"><span>Use</span><span>Actor prominence</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

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
