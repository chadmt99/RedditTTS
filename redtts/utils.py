from typing import List
import os
import re


def get_asset_filepath():
    """Gets the absolute location of asset directory."""
    return os.path.join(os.path.dirname(__file__), 'assets')


def tokenize(text: str) -> List[str]:
    """Tokenize paragraph into sentences.

    Create a list of strings, each element of the list representing a sentence,
    based on the below regex rule.
    Args:
        text: Text to be parsed into sentences.
    Returns:
        List of sentences.
    """
    no_url_text = re.sub(r'^https?:\/\/.*[\r\n]*', '',
                         text, flags=re.MULTILINE)

    # Split based on periods.
    parse_1 = re.split(
        "(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", no_url_text
    )
    # Split based on commas.
    parse_2 = []
    for phrase in parse_1:
        parse_2.extend(
            re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\,|\;)\s", phrase)
        )
    # Split based on semicolons.
    parse_3 = []
    for phrase in parse_2:
        parse_3.extend(
            re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\,|\;)\s", phrase)
        )
    # Split based on periods + quotes and whitespace or question marks +
    # quotations and whitespace
    parse_4 = []
    for phrase in parse_3:
        parse_4.extend(
            re.split(r"(?<=\.\"|\?\")\s", phrase)
        )

    return parse_4

