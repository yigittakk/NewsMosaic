import re


class TextProcessor:
    """
    Provides lightweight text cleaning and sentence splitting.
    """

    def __init__(
        self,
        min_sentence_chars=10,
        max_sentences_per_article=300,
    ):
        self.min_sentence_chars = min_sentence_chars
        self.max_sentences_per_article = max_sentences_per_article

    @staticmethod
    def clean_text(text):
        """
        Removes repeated whitespace and converts the input to a string.
        """

        if text is None:
            return ""

        return re.sub(
            r"\s+",
            " ",
            str(text),
        ).strip()

    def split_sentences(self, text):
        """
        Splits English article text into sentences.

        A simple regular expression is used to avoid an additional
        NLP dependency in the deployed application.
        """

        text = self.clean_text(text)

        if not text:
            return []

        sentences = re.split(
            r'(?<=[.!?])\s+(?=[A-Z0-9"\'])',
            text,
        )

        sentences = [
            self.clean_text(sentence)
            for sentence in sentences
            if len(self.clean_text(sentence))
            >= self.min_sentence_chars
        ]

        if not sentences:
            sentences = [text]

        return sentences[
            :self.max_sentences_per_article
        ]
