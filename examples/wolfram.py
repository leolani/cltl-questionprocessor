from cltl.combot.infra.config import ConfigurationManager
from cltl.factual_question_processing.wolfram_responder import WolframResponder

config_manager = ConfigurationManager()
config = config_manager.get_config("credentials")
credentials = config.get("wolfram")

replier = WolframResponder(credentials=credentials)

reply = replier.factual_respond("search the height of the Eiffel tower")
print(reply)
