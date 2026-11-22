import gc

import pandas as pd

from config import Config
from models.bias_classifier import BiasClassifier
from models.ner_extractor import NERExtractor
from models.theme_classifier import ThemeClassifier
from utils.text_processing import TextProcessor


class CorpusAnalyzer:
    """
    Runs the three final NewsMosaic models over a small uploaded corpus.

    Each model is loaded once, used for all valid articles, and then
    released before the next model is loaded. This keeps memory use lower
    on Streamlit Community Cloud.
    """

    def __init__(self):
        self.text_processor = TextProcessor(
            min_sentence_chars=Config.MIN_SENTENCE_CHARS,
            max_sentences_per_article=Config.MAX_SENTENCES_PER_ARTICLE,
        )

    @staticmethod
    def clear_memory():
        gc.collect()

    def analyze(self, dataframe, text_column, progress_callback=None):
        """
        Returns a copy of the input dataframe enriched with NLP outputs.
        Empty and over-length articles are preserved but not analyzed.
        """

        if text_column not in dataframe.columns:
            raise ValueError("The selected text column does not exist.")

        if len(dataframe) == 0:
            raise ValueError("The uploaded corpus is empty.")

        if len(dataframe) > Config.MAX_CORPUS_ARTICLES:
            raise ValueError(
                f"The online demo supports at most "
                f"{Config.MAX_CORPUS_ARTICLES} articles per run."
            )

        result = dataframe.copy()

        cleaned_texts = []
        valid_positions = []
        row_statuses = []

        for position, value in enumerate(result[text_column].tolist()):
            text = "" if pd.isna(value) else str(value)
            text = self.text_processor.clean_text(text)
            cleaned_texts.append(text)

            if not text:
                row_statuses.append("empty_text")
            elif len(text) > Config.MAX_ARTICLE_CHARS:
                row_statuses.append("too_long")
            else:
                row_statuses.append("ready")
                valid_positions.append(position)

        if not valid_positions:
            raise ValueError(
                "No article passed validation. Check empty text and article length limits."
            )

        result["analysis_status"] = row_statuses
        result["predicted_theme"] = None
        result["theme_confidence"] = None
        result["theme_uncertain"] = None
        result["mean_bias_probability"] = None
        result["bias_ratio_0705"] = None
        result["bias_sentence_count"] = None
        result["persons"] = None
        result["organizations"] = None
        result["locations"] = None
        result["misc_entities"] = None
        result["ner_entity_count"] = None

        total_steps = len(valid_positions) * 3
        completed_steps = 0

        def report(message):
            if progress_callback:
                progress_callback(
                    int((completed_steps / total_steps) * 100),
                    message,
                )

        report("Loading theme model...")

        theme_classifier = ThemeClassifier(
            model_name=Config.THEME_MODEL,
            threshold=Config.THEME_THRESHOLD,
            max_length=Config.THEME_MAX_LENGTH,
        )

        for article_number, position in enumerate(valid_positions, start=1):
            prediction = theme_classifier.predict(cleaned_texts[position])

            result.iat[position, result.columns.get_loc("predicted_theme")] = prediction["theme"]
            result.iat[position, result.columns.get_loc("theme_confidence")] = prediction["theme_confidence"]
            result.iat[position, result.columns.get_loc("theme_uncertain")] = prediction["theme_uncertain"]

            completed_steps += 1
            report(
                f"Theme classification: article "
                f"{article_number}/{len(valid_positions)}"
            )

        del theme_classifier
        self.clear_memory()

        report("Loading bias model...")

        bias_classifier = BiasClassifier(
            model_name=Config.BIAS_MODEL,
            text_processor=self.text_processor,
            threshold=Config.BIAS_THRESHOLD,
            positive_label_id=Config.BIAS_POSITIVE_LABEL_ID,
            max_length=Config.BIAS_MAX_LENGTH,
            batch_size=Config.BIAS_BATCH_SIZE,
        )

        for article_number, position in enumerate(valid_positions, start=1):
            prediction = bias_classifier.predict(cleaned_texts[position])

            result.iat[position, result.columns.get_loc("mean_bias_probability")] = prediction["mean_bias_probability"]
            result.iat[position, result.columns.get_loc("bias_ratio_0705")] = prediction["bias_ratio"]
            result.iat[position, result.columns.get_loc("bias_sentence_count")] = prediction["bias_sentence_count"]

            completed_steps += 1
            report(
                f"Bias analysis: article "
                f"{article_number}/{len(valid_positions)}"
            )

        del bias_classifier
        self.clear_memory()

        report("Loading NER model...")

        ner_extractor = NERExtractor(
            model_name=Config.NER_MODEL,
            text_processor=self.text_processor,
            max_length=Config.NER_MAX_LENGTH,
            batch_size=Config.NER_BATCH_SIZE,
        )

        for article_number, position in enumerate(valid_positions, start=1):
            prediction = ner_extractor.predict(cleaned_texts[position])

            result.iat[position, result.columns.get_loc("persons")] = " | ".join(prediction["persons"])
            result.iat[position, result.columns.get_loc("organizations")] = " | ".join(prediction["organizations"])
            result.iat[position, result.columns.get_loc("locations")] = " | ".join(prediction["locations"])
            result.iat[position, result.columns.get_loc("misc_entities")] = " | ".join(prediction["misc_entities"])
            result.iat[position, result.columns.get_loc("ner_entity_count")] = prediction["ner_entity_count"]
            result.iat[position, result.columns.get_loc("analysis_status")] = "analyzed"

            completed_steps += 1
            report(
                f"NER: article "
                f"{article_number}/{len(valid_positions)}"
            )

        del ner_extractor
        self.clear_memory()

        if progress_callback:
            progress_callback(100, "Corpus analysis complete.")

        return result
