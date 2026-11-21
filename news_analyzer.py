import gc

from config import Config
from models.bias_classifier import BiasClassifier
from models.ner_extractor import NERExtractor
from models.theme_classifier import ThemeClassifier
from utils.text_processing import TextProcessor


class NewsAnalyzer:
    """
    Coordinates the three final NewsMosaic models.

    Models are loaded one at a time to reduce memory use
    on Streamlit Community Cloud.
    """

    def __init__(self):
        self.text_processor = TextProcessor(
            min_sentence_chars=(
                Config.MIN_SENTENCE_CHARS
            ),
            max_sentences_per_article=(
                Config.MAX_SENTENCES_PER_ARTICLE
            ),
        )

    @staticmethod
    def clear_memory():
        """
        Requests Python garbage collection after a model is released.
        """

        gc.collect()

    def analyze_theme(self, text):
        """
        Loads the theme model, predicts, then releases the model.
        """

        classifier = ThemeClassifier(
            model_name=(
                Config.THEME_MODEL
            ),
            threshold=(
                Config.THEME_THRESHOLD
            ),
            max_length=(
                Config.THEME_MAX_LENGTH
            ),
        )

        result = classifier.predict(
            text
        )

        del classifier

        self.clear_memory()

        return result

    def analyze_bias(self, text):
        """
        Loads the bias model, predicts, then releases the model.
        """

        classifier = BiasClassifier(
            model_name=(
                Config.BIAS_MODEL
            ),
            text_processor=(
                self.text_processor
            ),
            threshold=(
                Config.BIAS_THRESHOLD
            ),
            positive_label_id=(
                Config
                .BIAS_POSITIVE_LABEL_ID
            ),
            max_length=(
                Config.BIAS_MAX_LENGTH
            ),
            batch_size=(
                Config.BIAS_BATCH_SIZE
            ),
        )

        result = classifier.predict(
            text
        )

        del classifier

        self.clear_memory()

        return result

    def analyze_ner(self, text):
        """
        Loads the NER model, predicts, then releases the model.
        """

        extractor = NERExtractor(
            model_name=(
                Config.NER_MODEL
            ),
            text_processor=(
                self.text_processor
            ),
            max_length=(
                Config.NER_MAX_LENGTH
            ),
            batch_size=(
                Config.NER_BATCH_SIZE
            ),
        )

        result = extractor.predict(
            text
        )

        del extractor

        self.clear_memory()

        return result

    def analyze(self, text, progress_callback=None):
        """
        Runs Theme, Bias and NER sequentially.
        """

        text = (
            self.text_processor
            .clean_text(
                text
            )
        )

        if not text:
            raise ValueError(
                "Article text cannot be empty."
            )

        result = {}

        if progress_callback:
            progress_callback(
                10,
                "Running theme classification..."
            )

        result.update(
            self.analyze_theme(
                text
            )
        )

        if progress_callback:
            progress_callback(
                40,
                "Running linguistic bias analysis..."
            )

        result.update(
            self.analyze_bias(
                text
            )
        )

        if progress_callback:
            progress_callback(
                70,
                "Running named entity recognition..."
            )

        result.update(
            self.analyze_ner(
                text
            )
        )

        if progress_callback:
            progress_callback(
                100,
                "Analysis complete."
            )

        return result
