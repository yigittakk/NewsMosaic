class Config:
    """
    Central configuration for the NewsMosaic application.
    """

    THEME_MODEL = "yigittoud/newsmosaic-theme"
    BIAS_MODEL = "yigittoud/newsmosaic-bias"
    NER_MODEL = "yigittoud/newsmosaic-ner"

    THEME_THRESHOLD = 0.63437831
    BIAS_THRESHOLD = 0.705

    THEME_MAX_LENGTH = 256
    BIAS_MAX_LENGTH = 256
    NER_MAX_LENGTH = 256

    THEME_BATCH_SIZE = 8
    BIAS_BATCH_SIZE = 16
    NER_BATCH_SIZE = 16

    BIAS_POSITIVE_LABEL_ID = 1

    MIN_SENTENCE_CHARS = 10
    MAX_SENTENCES_PER_ARTICLE = 300

    MAX_CORPUS_ARTICLES = 25
