import torch

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


class ThemeClassifier:
    """
    Loads the final theme model and predicts one theme per article.
    """

    def __init__(
        self,
        model_name,
        threshold,
        max_length=256,
    ):
        self.model_name = model_name
        self.threshold = threshold
        self.max_length = max_length

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

        self.id2label = {
            int(key): value
            for key, value
            in self.model.config.id2label.items()
        }

    def predict(self, text):
        """
        Returns the predicted theme, confidence and uncertainty flag.
        """

        encoded = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        with torch.inference_mode():

            outputs = self.model(
                **encoded
            )

            probabilities = torch.softmax(
                outputs.logits.float(),
                dim=-1,
            )[0]

        confidence, label_id = torch.max(
            probabilities,
            dim=-1,
        )

        confidence = float(
            confidence.item()
        )

        label_id = int(
            label_id.item()
        )

        prediction = self.id2label[
            label_id
        ]

        uncertain = (
            confidence
            < self.threshold
        )

        return {
            "theme": prediction,
            "theme_confidence": confidence,
            "theme_uncertain": uncertain,
        }
