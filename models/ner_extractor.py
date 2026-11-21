import torch

from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
)


class NERExtractor:
    """
    Extracts PER, ORG, LOC and MISC entities from article text.
    """

    def __init__(
        self,
        model_name,
        text_processor,
        max_length=256,
        batch_size=16,
    ):
        self.model_name = model_name
        self.text_processor = text_processor
        self.max_length = max_length
        self.batch_size = batch_size

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            use_fast=True,
        )

        self.model = (
            AutoModelForTokenClassification
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

    @staticmethod
    def normalize_label(label):
        """
        Converts equivalent entity names to a common format.
        """

        label = label.upper()

        if label == "O":
            return "O", "O"

        if "-" in label:
            prefix, entity_type = (
                label.split(
                    "-",
                    1,
                )
            )
        else:
            prefix = "B"
            entity_type = label

        aliases = {
            "PERSON": "PER",
            "ORGANIZATION": "ORG",
            "LOCATION": "LOC",
        }

        entity_type = aliases.get(
            entity_type,
            entity_type,
        )

        return prefix, entity_type

    @staticmethod
    def merge_wordpieces(tokens):
        """
        Reconstructs BERT WordPiece tokens.
        """

        text = ""

        for token in tokens:

            if token.startswith("##"):
                text += token[2:]

            else:

                if text:
                    text += " "

                text += token

        return text.strip()

    @staticmethod
    def unique_entities(values):
        """
        Removes duplicate entity strings while preserving order.
        """

        seen = set()
        result = []

        for value in values:

            key = value.casefold()

            if key not in seen:
                seen.add(key)
                result.append(value)

        return result

    def decode_sequence(
        self,
        input_ids,
        attention_mask,
        prediction_ids,
    ):
        """
        Converts token labels into complete entity strings.
        """

        tokens = (
            self.tokenizer
            .convert_ids_to_tokens(
                input_ids.tolist()
            )
        )

        labels = [
            self.id2label[
                int(label_id)
            ]
            for label_id
            in prediction_ids.tolist()
        ]

        entities = []

        current_type = None
        current_tokens = []

        for token, label, keep in zip(
            tokens,
            labels,
            attention_mask.tolist(),
        ):

            if not keep:
                break

            if token in (
                self.tokenizer
                .all_special_tokens
            ):
                continue

            prefix, entity_type = (
                self.normalize_label(
                    label
                )
            )

            if entity_type == "O":

                if current_type is not None:

                    entity_text = (
                        self.merge_wordpieces(
                            current_tokens
                        )
                    )

                    if entity_text:
                        entities.append(
                            (
                                current_type,
                                entity_text,
                            )
                        )

                current_type = None
                current_tokens = []

                continue

            starts_new = (
                current_type is None
                or prefix == "B"
                or current_type != entity_type
            )

            if starts_new:

                if current_type is not None:

                    entity_text = (
                        self.merge_wordpieces(
                            current_tokens
                        )
                    )

                    if entity_text:
                        entities.append(
                            (
                                current_type,
                                entity_text,
                            )
                        )

                current_type = entity_type
                current_tokens = [token]

            else:

                current_tokens.append(
                    token
                )

        if current_type is not None:

            entity_text = (
                self.merge_wordpieces(
                    current_tokens
                )
            )

            if entity_text:
                entities.append(
                    (
                        current_type,
                        entity_text,
                    )
                )

        return entities

    def predict_sentences(
        self,
        sentences,
    ):
        """
        Runs NER on sentence batches.
        """

        sentence_entities = []

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

                prediction_ids = torch.argmax(
                    outputs.logits,
                    dim=-1,
                ).cpu()

                for row_index in range(
                    len(batch)
                ):

                    entities = (
                        self.decode_sequence(
                            encoded[
                                "input_ids"
                            ][
                                row_index
                            ],
                            encoded[
                                "attention_mask"
                            ][
                                row_index
                            ],
                            prediction_ids[
                                row_index
                            ],
                        )
                    )

                    sentence_entities.append(
                        entities
                    )

        return sentence_entities

    def predict(self, text):
        """
        Extracts unique entities from the complete article.
        """

        sentences = (
            self.text_processor
            .split_sentences(
                text
            )
        )

        if not sentences:

            return {
                "persons": [],
                "organizations": [],
                "locations": [],
                "misc_entities": [],
                "ner_entity_count": 0,
            }

        sentence_entities = (
            self.predict_sentences(
                sentences
            )
        )

        grouped = {
            "PER": [],
            "ORG": [],
            "LOC": [],
            "MISC": [],
        }

        for entities in sentence_entities:

            for (
                entity_type,
                entity_text,
            ) in entities:

                if entity_type in grouped:
                    grouped[
                        entity_type
                    ].append(
                        entity_text
                    )

        for entity_type in grouped:

            grouped[
                entity_type
            ] = self.unique_entities(
                grouped[
                    entity_type
                ]
            )

        total_count = sum(
            len(values)
            for values
            in grouped.values()
        )

        return {
            "persons": grouped["PER"],
            "organizations": grouped["ORG"],
            "locations": grouped["LOC"],
            "misc_entities": grouped["MISC"],
            "ner_entity_count": total_count,
        }
