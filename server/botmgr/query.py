import os

from .. import socketio
from flask_socketio import emit
from .open_ai.conv_ai import ConversationalAiModel
from .dflow import DialogFlowHandler, DialogFlowResults
from .lookups import *
from server.common import Singleton

@Singleton
class QueryHandler():

    def __init__(self):
        self.dflow = DialogFlowHandler()

        self.openai_enabled: bool = os.getenv('openai.enabled') == 'true'
        if self.openai_enabled:
            self.conv_ai = ConversationalAiModel(os.getenv('openai_model'))

    def handle_query(self, text: str):
        intent: DialogFlowResults = self.dflow.process(text)
        response = intent.fulfillment_text if intent is not None and intent.fulfillment_text != '' else ''

        print(intent.intent)

        if intent.intent == "weather":
            response = lookup_weather(intent.response)
        elif intent.intent == "time.get":
            response = lookup_time(intent.response)

        # if self.openai_enabled and (response is None or response == ''):
        response = self.conv_ai.process(text)

        if response is None or response == '':
            response = 'Sorry, my brain is dead'

        emit('message', {'msg': response, 'sender': 'bot'}, broadcast=True)