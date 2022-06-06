"""
Query the Wolfram Alpha API using Natural Language.
"""

from typing import Optional

import requests

from cltl.factual_question_processing.api import FactualResponder


class Wolfram:
    API_SPOKEN = r"https://api.wolframalpha.com/v1/spoken?appid={}&i={}"
    API_QUERY = r"http://www.wolframalpha.com/queryrecognizer/query.jsp?&appid={}&mode=Voice&i={}"

    ERRORS = [
        "Wolfram Alpha did not understand your input",
        "No spoken result available",
        "Information about"
    ]

    TOO_BROAD = "Information about "

    def __init__(self, app_id):
        """
        Interact with Wolfram Spoken Results API

        Parameters
        ----------
        app_id: str
            Wolfram Application Identifier
        """
        self._app_id = app_id

    def is_query(self, query):
        return requests.get(self.API_QUERY.format(self._app_id, query.replace(' ', '+'))).text

    def query(self, query):
        """
        Get spoken result from WolframAlpha query

        Parameters
        ----------
        query: str
            Question to ask the WolframAlpha Engine

        Returns
        -------
        result: str or None
            Answer to Question or None if no answer could be found
        """

        result = requests.get(self.API_SPOKEN.format(self._app_id, query.replace(' ', '+'))).text
        if any([result.startswith(error) for error in self.ERRORS]):
            if result.startswith(self.TOO_BROAD):
                topic = result.replace(self.TOO_BROAD, "")
                return "What would you like to know about {}?".format(topic)
        else:
            return result


class WolframResponder(FactualResponder):
    WEB_CUE = [
        "can you search ",
        "can you look up ",
        "can you query ",
        "google ",
        "what does the internet say about ",
        "quick question ",
        "can you find out ",
        "can you google ",
        "search ",
        "go online ",
        "find me ",
    ]

    def __init__(self, credentials):
        super(FactualResponder, self).__init__()
        self._app_id = credentials
        self._wolfram = Wolfram(self._app_id)

    def factual_respond(self, question):
        # type: (str) -> Optional[str]

        transcript = question.lower().strip()
        wellformed_query = self._wolfram.is_query(transcript)

        for que in self.WEB_CUE:
            # if transcript.lower().startswith(que) or wellformed_query:
            if transcript.find(que.strip()) >= 0 or wellformed_query:
                transcript = transcript.replace(que, "")

                if self._wolfram.is_query(transcript):
                    result = self._wolfram.query(transcript)

                    if result:
                        return result

                else:
                    self._log.info("Ill-formed query for Wolfram : {}".format(transcript))

                break
