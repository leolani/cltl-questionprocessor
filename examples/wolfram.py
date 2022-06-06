from cltl.combot.infra.config.k8config import K8LocalConfigurationContainer
from cltl.factual_question_processing.wolfram_responder import WolframResponder

config_manager = K8LocalConfigurationContainer()
config_manager.load_configuration("./../config/credentials.config")
credentials = config_manager.get_config("credentials", "wolfram")

replier = WolframResponder(credentials=credentials)

reply = replier.factual_respond("search the height of the Eiffel tower")
print(reply)
