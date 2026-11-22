# NewsMosaic

**NewsMosaic** is a research-oriented web application for analysing English news at both article and corpus level. It combines three supervised NLP tasks in one workflow: **theme classification**, **linguistic bias detection**, and **Named Entity Recognition (NER)**.

The application is designed as an academic functional prototype: users can upload a structured news corpus, validate it, run the final NLP models, inspect individual articles, explore corpus-level patterns through an interactive dashboard, and export an enriched version of the original data.

> **Status:** functional MVP · inference-only deployment · English news corpora

## What NewsMosaic does

The core workflow is:

**Upload → Validate → Analyse → Aggregate → Explore → Export**

NewsMosaic supports:

- single-article analysis;
- structured CSV corpus upload and validation;
- theme classification across 16 news categories;
- sentence-level linguistic bias scoring aggregated to article level;
- extraction of persons, organizations, locations, and miscellaneous entities;
- explicit uncertainty flags for low-confidence theme predictions;
- interactive filtering by theme, year, source, confidence, bias score, and certainty;
- corpus-level theme, bias, entity, and time-trend visualizations;
- article-level drill-down inside the dashboard;
- export of an enriched CSV while preserving the original input columns.

## Final NLP models

The deployed application uses previously trained and validated models hosted on Hugging Face. The web app performs **inference only**; it does not train or fine-tune models at runtime.

| Task | Final model | Main evaluation result | Inference behaviour |
|---|---|---:|---|
| Theme classification | RoBERTa | Macro-F1 **0.8354** | 16 classes; predictions below **0.6344** confidence are flagged as uncertain |
| Linguistic bias detection | ModernBERT | Macro-F1 **0.8288** | sentence-level bias probability; article mean plus ratio above **0.705** |
| Named Entity Recognition | `bert-base-cased` | Entity-level F1 **0.8893** | PER / ORG / LOC / MISC extraction |

Hugging Face model repositories:

- Theme: <https://huggingface.co/yigittoud/newsmosaic-theme>
- Bias: <https://huggingface.co/yigittoud/newsmosaic-bias>
- NER: <https://huggingface.co/yigittoud/newsmosaic-ner>

### Important interpretation note

All outputs are **model estimates**. Theme labels should not be treated as human gold labels. The bias component measures lexical/linguistic signals learned from supervised data; it does **not** determine whether an article is factually correct, politically fair, or intentionally misleading. NER results depend on the entity types and conventions learned during fine-tuning.

## Focused corpus dashboard

The dashboard is intentionally divided into focused views instead of showing every chart at once. Filters update the views without rerunning the NLP models.

- **Overview** — leading theme, theme coverage, mean bias signal, most visible entity, quality status, and a compact article snapshot.
- **Themes** — ranked horizontal theme distribution plus a supporting table with share, mean confidence, and uncertainty counts.
- **Bias** — article-level bias probability distribution with mean/median summaries and the mean sentence bias ratio.
- **Entities** — separate top-N views for persons, organizations, and locations.
- **Trends** — yearly bias line chart and a compact heatmap of the most frequent theme shares when year/date metadata is available.
- **Articles** — searchable article drill-down with metadata, model outputs, named entities, and original text.

The visual design prioritizes comparison and interpretation over chart quantity: categorical rankings use horizontal bars, distributions use histograms, ordered temporal signals use lines, and cross-year theme composition uses a heatmap rather than a crowded stacked chart.


## In-app methodology

The **Methods & model cards** area is organized as a product-facing explanation rather than a long technical appendix:

1. **Pipeline** explains the five-stage workflow from validation to enriched export.
2. **Model cards** summarize each deployed model, its task, evaluation metric, threshold, and output.
3. **Interpretation** states what theme confidence, linguistic bias, and NER outputs do and do not mean.
4. **System design** documents the inference architecture, sequential model loading, deployment limits, and the boundary between the public demo and the offline large-corpus pipeline.

## Input format

### Single article

Paste one English news article into the **Single Article** tab.

### Corpus

Upload a CSV file. A text column is required and can be selected in the interface. Common accepted names include:

- `text`
- `plain_text`
- `article`
- `article_text`
- `content`

Optional metadata such as `id`, `title`, `date`, `year`, `source`, `publisher`, or categories can be retained and used by the dashboard when available.

### Public demo safeguards

The Streamlit Community Cloud deployment intentionally limits the online demo to:

- **25 articles per corpus**;
- **5 MB maximum CSV size**;
- **20,000 characters per article**;
- English-language news.

These are deployment safeguards for a free public demo, not limits of the research pipeline itself. Large corpora should be processed through the offline batch workflow.

Invalid or unsupported rows are preserved in the exported data and can be marked with statuses such as `empty_text` or `too_long` rather than being silently discarded.

## Enriched output

Depending on the analysis, NewsMosaic adds fields such as:

```text
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
analysis_status
```

The original corpus columns are preserved.

## System architecture

```text
User browser
    |
    v
Streamlit interface
    |
    +--> Single Article Analysis
    |
    +--> Corpus Upload + Validation
             |
             v
        Corpus Analyzer
             |
             +--> ThemeClassifier  --> Hugging Face model
             +--> BiasClassifier   --> Hugging Face model
             +--> NERExtractor     --> Hugging Face model
             |
             v
        Aggregation + Dashboard
             |
             v
        Enriched CSV Export
```

To keep memory usage manageable on the public deployment, the three transformer models are loaded **sequentially** for corpus processing rather than being kept in memory simultaneously.

## Repository structure

```text
NewsMosaic/
├── streamlit_app.py          # Streamlit interface and dashboard
├── corpus_analyzer.py        # Corpus-level orchestration
├── news_analyzer.py          # Single-article orchestration
├── config.py                 # Model IDs, thresholds, and demo limits
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml           # Light theme and Streamlit configuration
├── models/
│   ├── theme_classifier.py
│   ├── bias_classifier.py
│   └── ner_extractor.py
└── utils/
    └── text_processing.py
```

## Local setup

A clean Python 3.11 environment is recommended.

### Conda

```bash
conda create -n newsmosaic python=3.11 -y
conda activate newsmosaic
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

### Standard Python environment

```bash
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

The application will normally be available at `http://localhost:8501`.

## Deployment

The public app is designed for **Streamlit Community Cloud**:

1. connect the GitHub repository;
2. use the `main` branch;
3. set `streamlit_app.py` as the entry point;
4. use Python 3.11;
5. deploy the public app.

The final models are downloaded from their public Hugging Face repositories. No model-training credentials or API keys are required by the current inference-only application.

## Research context

NewsMosaic was designed around comparative supervised analysis of English news corpora, with CCNews used as the target news corpus. The system supports article-level analysis and corpus-level aggregation across time and available metadata.

The application scope includes structured corpus upload, validation, Theme/Bias/NER analysis, interactive exploration, uncertainty/data-quality warnings, and enriched export.

The following remain outside the current project scope:

- automatic news collection;
- real-time monitoring;
- fact-checking;
- misinformation detection;
- training custom models inside the web application;
- unrestricted multilingual analysis.

## Scaling beyond the public demo

The current Streamlit deployment is intentionally small and synchronous. A production-oriented version for larger or concurrent workloads would separate the UI from inference and add infrastructure such as:

- background job processing;
- persistent object/file storage;
- model-serving workers or dedicated inference endpoints;
- job status and resumable processing;
- authentication and per-user workspaces;
- larger-corpus batching and queue management;
- monitoring and deployment observability.

The research pipeline can therefore remain reproducible while the public demo stays lightweight and safe.

## Author & academic context

<table>
<tr>
<td width="150" valign="top">
<a href="https://github.com/yigittakk">
<img src="https://github.com/yigittakk.png?size=160" width="120" alt="Yiğit Ak">
</a>
</td>
<td valign="top">

### Yiğit Ak

Developer of **NewsMosaic**  
University of Bologna  
**Machine Learning for Humanities** · 2026

NewsMosaic was developed as an academic machine-learning project for the University of Bologna's *Machine Learning for Humanities* course. The project combines supervised NLP model development with a deployable research-oriented application for English news corpus analysis.

- GitHub: [@yigittakk](https://github.com/yigittakk)
- Source repository: [yigittakk/NewsMosaic](https://github.com/yigittakk/NewsMosaic)

</td>
</tr>
</table>

## Project

**NewsMosaic – A Research-Oriented Platform for News Corpus Analysis**  
Developed by **Yiğit Ak**  
University of Bologna · Machine Learning for Humanities · 2026
