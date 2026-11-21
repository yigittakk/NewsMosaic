import json

import streamlit as st

from config import Config
from news_analyzer import NewsAnalyzer


st.set_page_config(
    page_title="NewsMosaic",
    page_icon="📰",
    layout="wide",
)


@st.cache_resource
def get_analyzer():
    """
    Creates one lightweight coordinator object.

    The transformer models themselves are loaded one at a time
    during analysis to reduce memory usage.
    """

    return NewsAnalyzer()


def show_entity_list(
    title,
    entities,
):
    """
    Displays one named-entity group.
    """

    st.markdown(
        f"#### {title}"
    )

    if not entities:

        st.caption(
            "No entities detected."
        )

        return

    for entity in entities:

        st.write(
            f"• {entity}"
        )


st.title(
    "📰 NewsMosaic"
)

st.caption(
    "A research-oriented platform for English news analysis"
)

st.markdown(
    """
    Paste an English news article below. NewsMosaic applies
    three previously trained NLP models for **theme classification**,
    **linguistic bias detection**, and **named entity recognition**.
    """
)

with st.expander(
    "About the analysis",
    expanded=False,
):

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


article_text = st.text_area(
    "Article text",
    height=320,
    placeholder=(
        "Paste an English news article here..."
    ),
)


analyze_button = st.button(
    "Analyze Article",
    type="primary",
    use_container_width=True,
)


if analyze_button:

    if not article_text.strip():

        st.warning(
            "Please enter an article before running the analysis."
        )

        st.stop()

    analyzer = get_analyzer()

    progress_bar = st.progress(
        0
    )

    status_text = st.empty()

    def update_progress(
        value,
        message,
    ):
        progress_bar.progress(
            value
        )

        status_text.write(
            message
        )

    try:

        result = analyzer.analyze(
            article_text,
            progress_callback=(
                update_progress
            ),
        )

    except Exception as error:

        progress_bar.empty()
        status_text.empty()

        st.error(
            "The analysis could not be completed."
        )

        st.exception(
            error
        )

        st.stop()

    progress_bar.empty()
    status_text.empty()

    st.divider()

    st.header(
        "Analysis Results"
    )

    # ------------------------------------------------------
    # Theme
    # ------------------------------------------------------

    st.subheader(
        "1. Theme Classification"
    )

    theme_col1, theme_col2 = st.columns(
        2
    )

    with theme_col1:

        st.metric(
            "Predicted Theme",
            result[
                "theme"
            ],
        )

    with theme_col2:

        st.metric(
            "Confidence",
            (
                f'{result["theme_confidence"]:.1%}'
            ),
        )

    if result[
        "theme_uncertain"
    ]:

        st.warning(
            "The theme prediction is below the calibrated "
            f"confidence threshold ({Config.THEME_THRESHOLD:.3f})."
        )

    else:

        st.success(
            "The theme prediction is above the calibrated "
            "confidence threshold."
        )

    # ------------------------------------------------------
    # Bias
    # ------------------------------------------------------

    st.subheader(
        "2. Linguistic Bias"
    )

    bias_col1, bias_col2, bias_col3 = (
        st.columns(
            3
        )
    )

    mean_bias = result[
        "mean_bias_probability"
    ]

    bias_ratio = result[
        "bias_ratio"
    ]

    with bias_col1:

        st.metric(
            "Mean Bias Probability",
            (
                f"{mean_bias:.1%}"
                if mean_bias is not None
                else "N/A"
            ),
        )

    with bias_col2:

        st.metric(
            "Bias Ratio",
            (
                f"{bias_ratio:.1%}"
                if bias_ratio is not None
                else "N/A"
            ),
        )

    with bias_col3:

        st.metric(
            "Analyzed Sentences",
            result[
                "bias_sentence_count"
            ],
        )

    st.caption(
        "Bias Ratio = proportion of analyzed sentences whose "
        f"predicted bias probability is at least {Config.BIAS_THRESHOLD}."
    )

    # ------------------------------------------------------
    # NER
    # ------------------------------------------------------

    st.subheader(
        "3. Named Entity Recognition"
    )

    st.metric(
        "Unique Entities",
        result[
            "ner_entity_count"
        ],
    )

    entity_col1, entity_col2 = (
        st.columns(
            2
        )
    )

    with entity_col1:

        show_entity_list(
            "Persons",
            result[
                "persons"
            ],
        )

        show_entity_list(
            "Locations",
            result[
                "locations"
            ],
        )

    with entity_col2:

        show_entity_list(
            "Organizations",
            result[
                "organizations"
            ],
        )

        show_entity_list(
            "Miscellaneous",
            result[
                "misc_entities"
            ],
        )

    # ------------------------------------------------------
    # Export
    # ------------------------------------------------------

    st.divider()

    export_result = {
        "theme": result[
            "theme"
        ],
        "theme_confidence": result[
            "theme_confidence"
        ],
        "theme_uncertain": result[
            "theme_uncertain"
        ],
        "mean_bias_probability": result[
            "mean_bias_probability"
        ],
        "bias_ratio": result[
            "bias_ratio"
        ],
        "bias_sentence_count": result[
            "bias_sentence_count"
        ],
        "persons": result[
            "persons"
        ],
        "organizations": result[
            "organizations"
        ],
        "locations": result[
            "locations"
        ],
        "misc_entities": result[
            "misc_entities"
        ],
        "ner_entity_count": result[
            "ner_entity_count"
        ],
    }

    st.download_button(
        label="Download Result as JSON",
        data=json.dumps(
            export_result,
            indent=2,
            ensure_ascii=False,
        ),
        file_name=(
            "newsmosaic_analysis.json"
        ),
        mime="application/json",
        use_container_width=True,
    )


st.divider()

st.caption(
    "NewsMosaic is an academic prototype. Model outputs are "
    "predictions and should not be interpreted as verified factual judgments."
)
