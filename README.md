# NewsMosaic

NewsMosaic is an academic prototype for English news analysis.

The application uses three previously trained transformer models:

- Theme classification
- Linguistic bias detection
- Named Entity Recognition

## Models

- Theme: `yigittoud/newsmosaic-theme`
- Bias: `yigittoud/newsmosaic-bias`
- NER: `yigittoud/newsmosaic-ner`

## Local installation

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deployment

The repository is designed to be deployed on Streamlit Community Cloud.

Use `streamlit_app.py` as the application entry point.

## Important

The deployed application performs inference only.
It does not train or fine-tune any model.
