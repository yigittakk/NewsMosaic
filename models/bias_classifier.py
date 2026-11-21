import numpy as np
import torch

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


class BiasClassifier:
    """
    Runs sentence-level bias classification and aggregates
    sentence probabilities to article-level measures.
    """

    def __init__(
        self,
        model_name,
        text_processor,
        threshold,
        positive_label_id=1,
        max_length=256,
        batch_size=16,
    ):
        self.model_name = model_name
        self.text_processor = text_processor
        self.threshold = threshold
        self.positive_label_id = positive_label_id
        self.max_length = max_length
        self.batch_size = batch_size

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True,
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                self.model_name
            )
        )

        self.model.eval()

        if self.model.config.num_labels != 2:
            raise ValueError(
                "The bias model must be a binary classifier."
            )

    def predict_sentences(
        self,
        sentences,
    ):
        """
        Returns one bias probability for each sentence.
        """

        results = []

        with torch.inference_mode():

            for start in range(
                0,
                len(sentences),
                self.batch_size,
            ):

                batch = sentences[
                    start:
                    start + self.batch_size
                ]

                encoded = self.tokenizer(
                    batch,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                )

                outputs = self.model(
                    **encoded
                )

                probabilities = torch.softmax(
                    outputs.logits.float(),
                    dim=-1,
                )

                bias_probabilities = probabilities[
                    :,
                    self.positive_label_id,
                ]

                results.extend(
                    bias_probabilities
                    .cpu()
                    .tolist()
                )

        return results

    def predict(self, text):
        """
        Returns article-level bias measures.
        """

        sentences = (
            self.text_processor
            .split_sentences(
                text
            )
        )

        if not sentences:

            return {
                "mean_bias_probability": None,
                "bias_ratio": None,
                "bias_sentence_count": 0,
            }

        probabilities = (
            self.predict_sentences(
                sentences
            )
        )

        values = np.asarray(
            probabilities,
            dtype=np.float32,
        )

        mean_probability = float(
            values.mean()
        )

        bias_ratio = float(
            (
                values
                >= self.threshold
            ).mean()
        )

        return {
            "mean_bias_probability": mean_probability,
            "bias_ratio": bias_ratio,
            "bias_sentence_count": len(
                sentences
            ),
        }
