from django.apps import AppConfig
from facial_recognition.faceID import FaceID
from speaker_recognition.VoiceID import VoiceID
import os


class RembiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ReMBi'

    faceID = FaceID(os.getcwd())
    voiceID = VoiceID(os.getcwd())
