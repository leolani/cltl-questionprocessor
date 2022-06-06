from cltl.factual_question_processing import logger


class FactualResponder(object):

    def __init__(self):
        # type: () -> None
        """
        Generate answer to a factual question

        Parameters
        ----------
        """

        self._log = logger.getChild(self.__class__.__name__)
        self._log.info("Booted")

    def factual_respond(self, question):
        raise NotImplementedError()
