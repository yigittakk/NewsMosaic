import streamlit as st


st.set_page_config(
    page_title="NewsMosaic",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui_components import inject_global_styles, render_sidebar_footer

pages = {
    "NewsMosaic": [
        st.Page("app_pages/home.py", title="Home", icon=":material/home:", default=True),
        st.Page("app_pages/single_article.py", title="Single Article", icon=":material/article:"),
        st.Page("app_pages/corpus_analysis.py", title="Corpus Analysis", icon=":material/upload_file:"),
        st.Page("app_pages/dashboard.py", title="Dashboard", icon=":material/analytics:"),
    ],
    "Project": [
        st.Page("app_pages/methodology.py", title="Methodology", icon=":material/science:"),
        st.Page("app_pages/about.py", title="About", icon=":material/info:"),
    ],
}

inject_global_styles()
page = st.navigation(pages)
render_sidebar_footer()
page.run()
