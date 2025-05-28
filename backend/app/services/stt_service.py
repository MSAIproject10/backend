# services/stt_service.py
import os
# (SpeechRecognizer, AudioConfig, SpeechConfig)
# https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechrecognizer?view=azure-python
# https://learn.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.speechconfig?view=azure-python

from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer

AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_REGION")

def transcribe_audio(file_path: str) -> str:
    speech_config = SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_REGION)
    audio_config = AudioConfig(filename=file_path)
    recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once()
    if result.reason.name == "RecognizedSpeech":
        return result.text
    else:
        return "음성을 인식하지 못했습니다."

