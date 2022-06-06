import logging

from cltl.combot.event.emissor import TextSignalEvent
from cltl.combot.infra.config import ConfigurationManager
from cltl.combot.infra.event import Event, EventBus
from cltl.combot.infra.resource import ResourceManager
from cltl.combot.infra.time_util import timestamp_now
from cltl.combot.infra.topic_worker import TopicWorker
from cltl_service.emissordata.client import EmissorDataClient
from emissor.representation.scenario import TextSignal

from cltl.factual_question_processing.api import FactualResponder

logger = logging.getLogger(__name__)

CONTENT_TYPE_SEPARATOR = ';'


class FactualResponderService:
    @classmethod
    def from_config(cls, responder: FactualResponder, emissor_data: EmissorDataClient, event_bus: EventBus,
                    resource_manager: ResourceManager, config_manager: ConfigurationManager):
        config = config_manager.get_config("cltl.factual_question_processing")

        return cls(config.get("topic_input"), config.get("topic_output"), responder, emissor_data, event_bus,
                   resource_manager)

    def __init__(self, input_topic: str, output_topic: str, responder: FactualResponder,
                 emissor_data: EmissorDataClient, event_bus: EventBus, resource_manager: ResourceManager):
        self._responder = responder

        self._emissor_data = emissor_data
        self._event_bus = event_bus
        self._resource_manager = resource_manager

        self._input_topic = input_topic
        self._output_topic = output_topic

        self._topic_worker = None

    @property
    def app(self):
        return None

    def start(self, timeout=30):
        self._topic_worker = TopicWorker([self._input_topic], self._event_bus, provides=[self._output_topic],
                                         resource_manager=self._resource_manager, processor=self._process,
                                         name=self.__class__.__name__)
        self._topic_worker.start().wait()

    def stop(self):
        if not self._topic_worker:
            pass

        self._topic_worker.stop()
        self._topic_worker.await_stop()
        self._topic_worker = None

    def _process(self, event: Event[str]):
        response = None
        try:
            response = self._responder.factual_respond(event.payload)
        except:
            logger.exception("Factual responder error on question: %s", event.payload)

        if response:
            extractor_event = self._create_payload(response)
            self._event_bus.publish(self._output_topic, Event.for_payload(extractor_event))

    def _create_payload(self, response):
        scenario_id = self._emissor_data.get_current_scenario_id()
        signal = TextSignal.for_scenario(scenario_id, timestamp_now(), timestamp_now(), None, response)

        return TextSignalEvent.create(signal)
