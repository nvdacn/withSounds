# Copyright (C) 2026 zh-yx <zhyx-work@outlook.com>, Cary-rowen <cary-rowen@outlook.com>
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import os
import controlTypes
from controlTypes import OutputReason
import globalPluginHandler
import speech
from speech.types import SpeechSequence

SOUNDS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sounds")
LINK_SOUND_PATH = os.path.join(SOUNDS_PATH, "link.wav")
VISITED_LINK_SOUND_PATH = os.path.join(SOUNDS_PATH, "visitedLink.wav")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._pendingLinkSpeech = False
		self._NVDA_getSpeechTextForProperties = speech.speech.getPropertiesSpeech
		speech.speech.getPropertiesSpeech = self._hook_getSpeechTextForProperties

	def _hook_getSpeechTextForProperties(
		self,
		reason: OutputReason = OutputReason.QUERY,
		**propertyValues,
	) -> SpeechSequence:
		"""Insert the link earcon and suppress the spoken visited state."""
		before = []
		visited = False
		isLink = propertyValues.get("role", None) == controlTypes.ROLE_LINK
		states = propertyValues.get("states", None)
		if isLink:
			del propertyValues["role"]
			if states is None:
				self._pendingLinkSpeech = True
		if states is not None:
			if controlTypes.STATE_VISITED in states:
				visited = True
				states = set(states)
				states.discard(controlTypes.STATE_VISITED)
				propertyValues["states"] = states
		soundPath = VISITED_LINK_SOUND_PATH if visited else LINK_SOUND_PATH
		if self._pendingLinkSpeech and "_role" in propertyValues:
			before.append(speech.commands.WaveFileCommand(soundPath))
			self._pendingLinkSpeech = False
		elif isLink and states is not None:
			before.append(speech.commands.WaveFileCommand(soundPath))
		return before + self._NVDA_getSpeechTextForProperties(reason, **propertyValues)

	def terminate(self):
		speech.speech.getPropertiesSpeech = self._NVDA_getSpeechTextForProperties
		super().terminate()
