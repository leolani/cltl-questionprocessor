"""
Query the Wikipedia API using Natural Language.
"""

import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional, Tuple, Union

import nltk
import requests
from cltl.factual_question_processing.api import FactualResponder


class Wikipedia:
    FULL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&titles="
    SUMMARY = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&titles="
    LINKS = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=max&titles="
    THUMBNAIL = "http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=1000&titles="
    DISAMBIGUATION = ["refer to:", "refers to:"]

    PARENTHESES = re.compile('\(.*?\)')
    DUPLICATE_SPACES = re.compile('[ )(]+')

    @staticmethod
    def query(query):
        # type: (Union[str, unicode]) -> Optional[Tuple[unicode, Optional[unicode]]]
        """
        Query Wikipedia

        Parameters
        ----------
        query: str or unicode
            Simple Natural Language Query (about something Wikipedia would know)

        Returns
        -------
        result: Optional[Tuple[unicode, str]]
            Wikipedia Answer and thumbnail image URL
        """

        # Tokenize, Tag Part of Speeches and Combine adjacent nouns into one token
        pos = Wikipedia._combine_nouns(nltk.pos_tag(nltk.word_tokenize(query)))

        # If this is a proper question about a Noun (quite hacky here)
        if pos and pos[0][1].startswith("VB") or pos[0][1] in ["MD"] or Wikipedia._is_queryable(pos[0][1]) or pos[0][
            0].lower() in ["what", "who"]:

            # And there is only one Noun in Question (a.k.a., question is simple enough)
            if sum([Wikipedia._is_queryable(tag) for word, tag in pos]) == 1:

                for word, tag in pos[::-1]:

                    # Try to Query Wikipedia about last object in sentence
                    if Wikipedia._is_queryable(tag):
                        result = Wikipedia._query(word)

                        if result:

                            # If Successful, Obtain Result and Image URL and return
                            query, answer, url = result
                            answer = re.sub(Wikipedia.DUPLICATE_SPACES, ' ', re.sub(Wikipedia.PARENTHESES, '', answer))
                            return answer, url
                        else:
                            return None
        return None

    def _query(self, query):
        query_websafe = urllib.parse.quote(query)

        try:
            # Query Summary
            json = requests.get(Wikipedia.FULL + query_websafe).json()
            extract = Wikipedia._find_key(json, 'extract')

            # Query Thumbnail
            json = requests.get(Wikipedia.THUMBNAIL + query_websafe).json()
            url = Wikipedia._find_key(json, 'source')

            if extract:
                if any([disambiguation in extract for disambiguation in Wikipedia.DISAMBIGUATION]):
                    links = Wikipedia._find_key(requests.get(Wikipedia.LINKS + query_websafe).json(), 'links')

                    for link in links:
                        new_query = link['title']
                        extract = Wikipedia._query(new_query)
                        if extract:
                            return new_query, "{} may refer to {}: {}".format(query, new_query, extract), url
                else:
                    return query, extract, url
        except:
            self._log.exception("Failed to query Wikipedia")
            return

    @staticmethod
    def _find_key(dictionary, key):
        for k, v in list(dictionary.items()):
            if k == key: return v
            if isinstance(v, dict): return Wikipedia._find_key(v, key)
        return None

    @staticmethod
    def _combine_nouns(pos):
        combined_pos = [list(pos[0])]
        for (word, tag) in pos[1:]:
            if Wikipedia._is_queryable(tag) and Wikipedia._is_queryable(combined_pos[-1][1]):
                combined_pos[-1][0] += " " + word
            else:
                combined_pos.append([word, tag])
        return combined_pos

    @staticmethod
    def _is_queryable(tag):
        return tag.startswith('NN') or tag.startswith("JJ")


class WikipediaResponder(FactualResponder):
    WEB_CUE = [
        "can you search ",
        "can you look up ",
        "can you query ",
        "google ",
        "what does the internet say about ",
        "quick question ",
        "can you find out ",
        "can you google ",
    ]

    def __init__(self):
        self._log = logger.getChild(self.__class__.__name__)

    def factual_respond(self, questions):
        # type: (str) -> Optional[str]

        for que in self.WEB_CUE:
            if utterance.transcript.lower().startswith(que):
                result = Wikipedia.query(utterance.transcript.lower().replace(que, ""))

                if result:
                    # Get Answer and Image URL from Wikipedia Query
                    answer, url = result

                    # Take Summary (a.k.a. First Sentence) from Wikipedia Query
                    answer = re.split('[.\n]', answer)[0]

                    # Return Result
                    return answer

                break
