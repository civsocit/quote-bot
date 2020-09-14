import re
from abc import ABC, abstractmethod

import pymorphy2


class TextFilter(ABC):
    @classmethod
    @abstractmethod
    def process(cls, text_in: str) -> str:
        """
        Prepare some text
        :param text_in: input test
        :output: processed text
        """
        raise NotImplemented()


class FilterDuplicatedSpaces(TextFilter):
    @classmethod
    def process(cls, text_in: str) -> str:
        """
        Remove duplicated spaces
        Example: 'foo     bar' -> 'foo bar'
        """
        return re.sub(r"\s{2,}", " ", text_in)


class FilterBadHyphen(TextFilter):
    @classmethod
    def process(cls, text_in: str) -> str:
        """
        Replace bad hyphens
        Example: "A - is B" -> "A — is B"
        """
        return text_in.replace(" - ", " — ")


class FilterHangingPreposition(TextFilter):
    analyzer = pymorphy2.MorphAnalyzer()

    @classmethod
    def process(cls, text_in: str) -> str:
        """
        Place non-breaking spaces after prepositions, conjunctions
        Example: 'привет и пока' -> 'привет и\xa0пока'
        Example: 'из-за двери перекати-поле' -> 'из\u2011за двери перекати-поле'
        """
        text = text_in
        words = text.split()
        for word in words:
            if cls.analyzer.parse(word)[0].tag.POS in ("PREP", "CONJ") and len(word) < 6:
                text = text.replace(" " + word + " ", " " + word + "\u00a0")  # non-breaking space
                if "-" in word:
                    text = text.replace(word, word.replace("-", "\u2011"))  # non-breaking hyphen
        return text


def process(text_in: str) -> str:
    text = text_in
    for kls in TextFilter.__subclasses__():
        text = kls.process(text)

    return text
