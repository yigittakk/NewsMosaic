import streamlit as st


st.set_page_config(
    page_title="NewsMosaic",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui_components import inject_global_styles, render_top_navigation


home_page = st.Page(
    "app_pages/home.py",
    title="Home",
    icon=":material/home:",
    default=True,
)
single_article_page = st.Page(
    "app_pages/single_article.py",
    title="Single Article",
    icon=":material/article:",
)
corpus_page = st.Page(
    "app_pages/corpus_analysis.py",
    title="Corpus Analysis",
    icon=":material/upload_file:",
)
dashboard_page = st.Page(
    "app_pages/dashboard.py",
    title="Dashboard",
    icon=":material/analytics:",
)
methodology_page = st.Page(
    "app_pages/methodology.py",
    title="Methodology",
    icon=":material/science:",
)
about_page = st.Page(
    "app_pages/about.py",
    title="About",
    icon=":material/info:",
)

pages = [
    home_page,
    single_article_page,
    corpus_page,
    dashboard_page,
    methodology_page,
    about_page,
]

inject_global_styles()

# Keep Streamlit's router for URLs and session-safe page switching,
# but hide its built-in navigation. NewsMosaic renders its own persistent
# product navigation bar at the top of every page.
page = st.navigation(pages, position="hidden")
render_top_navigation(
    [
        (home_page, "Home", ":material/home:"),
        (single_article_page, "Single Article", ":material/article:"),
        (corpus_page, "Corpus Analysis", ":material/upload_file:"),
        (dashboard_page, "Dashboard", ":material/analytics:"),
        (methodology_page, "Methodology", ":material/science:"),
        (about_page, "About", ":material/info:"),
    ]
)

page.run()
