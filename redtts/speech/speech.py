from typing import Dict, List
from . import intros
import os
import praw
import pyttsx3
import random


VOICE_IDS = {
    'Alex': 'com.apple.speech.synthesis.voice.Alex',  # US
    'Daniel': 'com.apple.speech.synthesis.voice.daniel',  # GB
    'Fiona': 'com.apple.speech.synthesis.voice.fiona',  # Scotland
    'Fred': 'com.apple.speech.synthesis.voice.Fred',  # US
    'Karen': 'com.apple.speech.synthesis.voice.karen',  # AU
    'Moira': 'com.apple.speech.synthesis.voice.moira',  # IE
    'Samantha': 'com.apple.speech.synthesis.voice.samantha',  # US
    'Tessa': 'com.apple.speech.synthesis.voice.tessa',  # ZA
    'Veena': 'com.apple.speech.synthesis.voice.veena',  # IN
    'Victoria': 'com.apple.speech.synthesis.voice.Victoria'  # US
}


class VoiceBot(object):
    """Voice bot generates synthesized speech."""

    def __init__(self, rate_delta=0, voice="Daniel"):
        """ Initialize voice bot.

        VoiceBot to speak lines and generate text to speech data.
        Args:
            rate_delta: Amount to add to the default voice rate.
            voice: Name of supported voice.
        """
        super(VoiceBot, self).__init__()

        # Initialize text to speech engine.
        self.engine = pyttsx3.init()

        # Set voice.
        assert voice in VOICE_IDS.keys()
        self.voice = voice
        self.engine.setProperty('voice', VOICE_IDS[voice])

        # Adjust speaking speed.
        self.rate = rate_delta
        self.engine.setProperty(
            'rate', self.engine.getProperty('rate') + self.rate
        )

    def _preprocess(self, text):
        """Preprocess text, handle acronyms and censorship."""
        words = {
            "WIBTA": "would I be the A hole",
            "AmItheAsshole": "am I the A hole",
            "AITA": "am I the A hole", "aita": "am I the A hole",
            "Aita": "am I the A hole",
            "Asshole": "A hole", "ASSHOLE": "A hole", "asshole": "A hole",
            "JPOW": "J pow", "jpow": "J pow",
            "coronavirus": "corona virus",
            "hentai": "hen tie", "Hentai": "hen tie",
        }
        for k, v in words.items():
            text = text.replace(k, v)
        return text

    def generate_speech_files(self, text_list: List[str],
                              filepath: str,
                              submission,
                              include_intro=False) -> Dict[str, str]:
        """Generate voice speech files.

        Generate mp3 of text to speech for each given sentence.
        Map given sentences to filenames that point to where mp3's of the
        generated voices are stored.
        Args:
            text_list: List of phrases to be translated.
            filepath: Where to store the mp3 files.
            submission: Reddit submission.
            include_intro: Whether this should include intro voice.
        Returns:
            Dictionary mapping sentence of filename.
        """
        speech_map = {}
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        for i, text in enumerate(text_list):
            # Generate text to speech.
            filename = filepath + "/recording_%s.mp3" % str(i)
            audio_key = text

            if i == 0 and include_intro:
                subreddit = submission.subreddit.display_name
                intro = (
                    random.choice(intros.intros) +
                    " Welcome to R slash %s..., , , "
                    % subreddit
                )
                text = intro + text

            self.engine.save_to_file(
                self._preprocess(text), filename
            )
            self.engine.runAndWait()

            # Prevent the engine from getting caught.
            self._refresh_engine()

            # Map file name to text.
            print(text, filename)
            speech_map[audio_key + str(i)] = filename
        return speech_map

    def speak(self, text: str):
        """Speak given text.

        Use to engine to do immediate text to audio conversion and output.
        Run and wait for speech to audio to finish playing.
        Args:
            text: Text to be translated to audio.
        """
        self.engine.say(text)
        self.engine.runAndWait()

    def _refresh_engine(self):
        """Text to speech engine needs to be remade.

        Text to speech engine needs to be re-instantiated after every call of
        engine.runAndWait() to avoid getting caught.
        """
        del self.engine
        self.__init__(self.rate, self.voice)
