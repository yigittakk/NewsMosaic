# NewsMosaic

**NewsMosaic** is a research-oriented multipage web application for analysing English news at article and corpus level. It combines three supervised NLP tasks in one workflow: **theme classification**, **linguistic bias detection**, and **Named Entity Recognition (NER)**.

Developed by **Yiğit Ak** at the **University of Bologna** for the **Machine Learning for Humanities** course.

> Functional academic MVP · inference-only deployment · English news corpora

## Application pages

- **Home** — project landing page, workflow, model suite, and academic context.
- **Single Article** — paste one article and run Theme + Bias + NER.
- **Corpus Analysis** — upload, validate, analyse, and export a CSV corpus.
- **Dashboard** — explore the latest analysed corpus without rerunning the models.
- **Methodology** — processing pipeline, dataset/training strategy, model cards, interpretation guidance, and system design.
- **About** — developer information, academic context, project scope, and repository links.

## Core workflow

**Upload → Validate → Analyse → Aggregate → Explore → Export**

For corpus analysis, the three transformer models are loaded **sequentially**. One model processes all valid articles, is released from memory, and then the next model is loaded. This design reduces memory pressure on the public Streamlit deployment.

## Final NLP models

| Task | Final model | Main evaluation result | Deployed behaviour |
|---|---|---:|---|
| Theme classification | RoBERTa | Macro-F1 **0.8354** | 16 classes; confidence below **0.6344** is flagged as uncertain |
| Linguistic bias detection | ModernBERT | Macro-F1 **0.8288** | sentence probabilities aggregated to article mean + ratio above **0.705** |
| Named Entity Recognition | `bert-base-cased` | Entity-level F1 **0.8893** | PER / ORG / LOC / MISC extraction |

Model repositories:

- Theme: <https://huggingface.co/yigittoud/newsmosaic-theme>
- Bias: <https://huggingface.co/yigittoud/newsmosaic-bias>
- NER: <https://huggingface.co/yigittoud/newsmosaic-ner>

## Training and dataset strategy

The deployed models were trained and evaluated on labeled external datasets, while **CCNews 2020–2024** is primarily the target corpus for research analysis. Dataset roles were kept separate to avoid treating model-generated CCNews labels as supervised ground truth.

**CCNews collection vs. analysis:** the raw collection sampled **100,000 English-language news records per year** for 2020–2024 (**500,000 raw records before cleaning and selection**). The final offline research analysis used **125,000 articles** (**25,000 per year**), **not all 500,000 raw records**. A separate non-holdout CCNews pool supplied metadata-derived weak labels for theme adaptation.

| Task | Dataset | Role | Treatment |
|---|---|---|---|
| Theme | HuffPost, IAB, AG News, NewsCatcher, and MN-DS | Supervised training / validation / test | Source labels were harmonized into the 16-class NewsMosaic taxonomy and the combined external corpus was deduplicated and split. |
| Theme | Separate CCNews weak-label pool | Target-domain adaptation | Conservative labels were generated from metadata such as categories and tags. The fixed final inference corpus was excluded by exact-content hash. |
| Bias | BABE | Fine-tuning / primary evaluation | ModernBERT was fine-tuned on sentence-level annotations; the decision threshold was calibrated on validation data only. |
| Bias | MBIC | External robustness evaluation | Used to test out-of-dataset generalization; not used to fit the final model. |
| NER | CoNLL-2003 | Fine-tuning / evaluation | `bert-base-cased` was fine-tuned for PER / ORG / LOC / MISC token classification. |
| All tasks | Fixed CCNews reference corpus | Final target inference | 125,000 articles, balanced at 25,000 per year from 2020–2024, were analysed only after model selection. |

For Theme classification, the final prepared external dataset contained **316,697** examples (253,357 train / 31,670 validation / 31,670 test). A separate weakly labeled CCNews pool produced **112,610** clean examples, from which a balanced subset of **53,551** was selected. The original joint-training script then made a **stratified 90% weak-training / 10% weak-validation split**: only the weak-training portion was combined with external supervised training data; the weak-validation portion was kept separate for evaluation. A sequential adaptation experiment was rejected because it degraded external performance; the deployed model instead uses joint training with external supervised data and this weak CCNews training portion.

The final CCNews outputs are therefore **model estimates**, not human gold labels. Thresholds control decision/uncertainty behaviour and do not guarantee a fixed accuracy on CCNews.

## Dashboard design

The dashboard is deliberately focused rather than chart-heavy. A single view selector switches between:

- **Overview** — leading theme, coverage, bias signal, most visible entity, quality status, and corpus snapshot.
- **Themes** — ranked horizontal theme distribution and supporting confidence/uncertainty table.
- **Bias** — article-level bias probability distribution with mean/median summaries.
- **Entities** — top persons, organizations, or locations, one entity type at a time.
- **Trends** — time-based summaries when year/date metadata is available.
- **Articles** — searchable article-level drill-down with metadata, predictions, entities, and original text.

Filters change the dashboard view without rerunning model inference.

## Interpretation

All outputs are **model estimates**.

- Theme predictions are not human gold labels. Low-confidence predictions are explicitly marked as uncertain.
- Bias is a **lexical/linguistic signal** learned from supervised data. It is not a fact-check, truth score, or political verdict.
- NER outputs depend on the entity taxonomy and conventions learned during fine-tuning.

## Input format

### Single article

Paste one English news article into the **Single Article** page.

### Corpus

Upload a CSV and select the article-text column. Common names include:

```text
text
plain_text
article
article_text
content
```

Optional metadata such as `id`, `title`, `date`, `year`, `source`, `publisher`, and categories are preserved and can support dashboard exploration.

## Public demo safeguards

The Streamlit Community Cloud version intentionally limits online workloads to:

- **25 articles per corpus**
- **5 MB maximum CSV size**
- **20,000 characters per article**
- English-language news

These are deployment safeguards, not limits of the research pipeline. Larger corpora should be processed through the offline batch workflow.

Rows with empty or over-length text are preserved in the enriched export and marked with an `analysis_status` rather than being silently removed.

## Enriched output

NewsMosaic preserves original columns and can add:

```text
analysis_status
predicted_theme
theme_confidence
theme_uncertain
mean_bias_probability
bias_ratio_0705
bias_sentence_count
persons
organizations
locations
misc_entities
ner_entity_count
```

## System architecture

```text
Browser
  ↓
Streamlit multipage interface
  ├── Home
  ├── Single Article
  ├── Corpus Analysis
  ├── Dashboard
  ├── Methodology
  └── About
        ↓
NewsAnalyzer / CorpusAnalyzer
        ↓
ThemeClassifier → BiasClassifier → NERExtractor
        ↓
Public Hugging Face model repositories
        ↓
Interactive exploration + enriched export
```

## Repository structure

```text
NewsMosaic/
├── streamlit_app.py            # Multipage router
├── ui_components.py            # Shared styles, dashboard, and UI helpers
├── corpus_analyzer.py          # Corpus-level orchestration
├── news_analyzer.py            # Single-article orchestration
├── config.py                   # Model IDs, thresholds, and demo limits
├── requirements.txt
├── README.md
├── app_pages/
│   ├── home.py
│   ├── single_article.py
│   ├── corpus_analysis.py
│   ├── dashboard.py
│   ├── methodology.py
│   └── about.py
├── .streamlit/
│   └── config.toml
├── models/
│   ├── theme_classifier.py
│   ├── bias_classifier.py
│   └── ner_extractor.py
└── utils/
    └── text_processing.py
```

## Local setup

Python 3.11 is recommended.

```bash
conda create -n newsmosaic python=3.11 -y
conda activate newsmosaic
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

## Streamlit deployment

For Streamlit Community Cloud:

1. connect the GitHub repository;
2. use the `main` branch;
3. set `streamlit_app.py` as the entry point;
4. select Python 3.11;
5. deploy.

The app downloads its public final models from Hugging Face and performs inference only. No model-training credentials are required.

## Project scope

The current application includes structured corpus upload and validation, Theme/Bias/NER analysis, uncertainty and data-quality warnings, corpus-level exploration, article inspection, and enriched export.

Outside the current scope:

- automatic news collection;
- real-time monitoring;
- fact-checking;
- misinformation detection;
- training custom models inside the application;
- unrestricted multilingual analysis.

## Scaling beyond the public demo

A production-oriented version for larger or concurrent workloads would separate the UI from inference and add background jobs, persistent storage, dedicated model-serving workers/endpoints, job status, authentication, monitoring, and larger-corpus queue management.

## Author

**Yiğit Ak**  
University of Bologna  
Machine Learning for Humanities · 2026

GitHub: <https://github.com/yigittakk>  
Repository: <https://github.com/yigittakk/NewsMosaic>


## Navigation

NewsMosaic uses Streamlit's multipage router with its built-in navigation hidden (`st.navigation(..., position="hidden")`). A custom horizontal menu created with `st.page_link` provides Home, Single Article, Corpus Analysis, Dashboard, Methodology, and About directly at the top of every page. The sidebar is optional and contains developer and online-demo information only.

