# With sounds

import os
import controlTypes
from controlTypes import OutputReason
import globalPluginHandler
import speech
from speech.types import SpeechSequence

SOUNDS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")	

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._NVDA_getSpeechTextForProperties = speech.speech.getPropertiesSpeech
		speech.speech.getPropertiesSpeech = self._hook_getSpeechTextForProperties

	def _hook_getSpeechTextForProperties(self, reason: OutputReason = OutputReason.QUERY, **propertyValues) -> SpeechSequence:
		before = []
		states = propertyValues.get('states', None)
		if states and controlTypes.STATE_VISITED in states:
			states.remove(controlTypes.STATE_VISITED)
		role = propertyValues.get('role', None)
		if role and role == controlTypes.ROLE_LINK:
			del propertyValues['role']
			before.append(speech.commands.WaveFileCommand(os.path.join(SOUNDS_PATH, "link.wav")))
		return before + self._NVDA_getSpeechTextForProperties(reason, **propertyValues)

	def terminate(self):
		speech.speech.getPropertiesSpeech = self._NVDA_getSpeechTextForProperties
		super().terminate()
