import os
import torch
import random
import nemo.collections.asr as nemo_asr
import sounddevice as sd
import soundfile as sf
import Levenshtein


class VoiceID:
    _instance = None

    def __new__(cls, root_path):
        if not cls._instance:
            cls._instance = super(VoiceID, cls).__new__(cls)
            # Rutas
            cls._instance.voicedb_path = os.path.join(root_path, "database", "voice")
            cls._instance.tmp_voice_path = os.path.join(root_path, "tmp", "voice_tmp.wav")
            cls._instance.quartznet_model_path = os.path.join(root_path, "speaker_recognition", "models", "quartznet", "stt_es_quartznet15x5_ft_ep53_944h.nemo")
            cls._instance.titanet_model_path = os.path.join(root_path, "speaker_recognition", "models", "titanet", "speakerverification_en_titanet_large.nemo")

            # Modelos pre-entrenados
            cls._instance.titanet_model = nemo_asr.models.EncDecSpeakerLabelModel.restore_from(cls._instance.titanet_model_path)
            cls._instance.quartznet_model = nemo_asr.models.ASRModel.restore_from(cls._instance.quartznet_model_path)

            # Diccionario de frases o palabras
            cls._instance.diccionario = ["un zorro gris comia perdiz",
                                         "el zorro gris comia perdiz",
                                         "un zorro gris come perdiz",
                                         "el zorro gris come perdiz",
                                         "hola buenos dias",
                                         "hola buenas tardes",
                                        ]
            cls._instance.frase = ""

            cls._instance.quartznet_threshold = 0.7
            cls._instance.titanet_threshold = 0.7

        return cls._instance

        
    @property
    def name(cls):
        return cls._instance.__class__.__name__
    

    @classmethod
    def get_phrase(cls):
        return cls._instance.frase
    

    @classmethod
    def qn_get_similarity_score(cls, real_text, transcription_text):
        real_text = real_text.replace(" ","")
        transcription_text = transcription_text.replace(" ","")
        distance = Levenshtein.distance(real_text, transcription_text)
        max_len = max(len(real_text), len(transcription_text))
        similarity = 1 - (distance / max_len)
        return similarity
    

    @classmethod
    def qn_check_similarity(cls, similarity):
        return True if similarity >= cls._instance.quartznet_threshold else False
    

    @classmethod
    def tn_check_similarity(cls, similarity):
        return True if similarity >= cls._instance.titanet_threshold else False
    

    @classmethod
    def qn_transcribe_wav(cls, path_wav):
        return cls._instance.quartznet_model.transcribe([path_wav])[0]
    

    @classmethod
    def qn_get_similarity_score_and_best_phrase(cls, path_wav):
        transcription = cls._instance.qn_transcribe_wav(path_wav)

        best_phrase = ""
        best_sim_score = 0
        for phrase in cls._instance.diccionario:
            sim_score = cls._instance.qn_get_similarity_score(phrase, transcription)
            if sim_score > best_sim_score:
                best_sim_score = sim_score
                best_phrase = phrase
        
        return best_sim_score, best_phrase
    

    @classmethod
    def tn_get_embedding(cls, audio_path):
        return cls._instance.titanet_model.get_embedding(audio_path)
    

    @classmethod
    def tn_get_similarity_score(cls, embedding_1, embedding_2):
        embedding_1 = embedding_1.squeeze()
        embedding_2 = embedding_2.squeeze()

        X = embedding_1 / torch.linalg.norm(embedding_1)
        Y = embedding_2 / torch.linalg.norm(embedding_2)

        similarity_score = torch.dot(X, Y) / ((torch.dot(X, X) * torch.dot(Y, Y)) ** 0.5)
        similarity_score = (similarity_score + 1) / 2

        return similarity_score.item()
    

    @classmethod
    def qn_choose_random_phrase(cls):
        cls._instance.frase = random.choice(cls._instance.diccionario)

    
    @classmethod
    def record_audio(cls):
        fs = 16000  
        seconds = 3  

        cls._instance.frase = random.choice(cls._instance.diccionario)
        print("(*) Frase: '",cls._instance.frase,"'")
        print("(*) Grabando voz...")
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
        sd.wait() 
        print("(+) Audio capturado (3 seg)")
        sf.write(cls._instance.tmp_voice_path, recording, fs)
    

    @classmethod
    def qn_is_sentence_correct(cls,transcripted_phrase):
        print("(*) Frase:", cls._instance.frase)
        print("(*) Transcripcion:", transcripted_phrase)

        similarity_score = cls._instance.qn_get_similarity_score(cls._instance.frase, transcripted_phrase)
        if cls._instance.qn_check_similarity(similarity_score):
            print("Frase correcta")
            return True
        print("Frase incorrecta")
        return False
    

    @classmethod
    def verify_speaker_localdb(cls):
        """
        Busca si la voz de entrada coincide con algun audio de la base de datos local.

        Returns: boolean, id_usuario, nombre_usuario
        """
        for user_dir in os.listdir(cls._instance.voicedb_path):
            userpath = os.path.join(cls._instance.voicedb_path, user_dir)
            if user_dir == "tmp":
                continue

            if os.path.isdir(os.path.join(userpath)):
                for voicefile in os.listdir(userpath):
                    if voicefile == ".gitignore":
                        continue

                    audiopath = os.path.join(userpath, voicefile)
                    print(voicefile)

                    if not cls._instance.is_sentence_correct():
                        break

                    if cls._instance.titanet_model.verify_speakers(cls._instance.tmp_voice_path, audiopath):
                        print("Verificado")
                        return True, user_dir.split("_", 1)[0], user_dir.split("_", 1)[1]

        print("No autorizado")
        return False, 0, ""
    

    @classmethod
    def qn_transcribe(cls, audiopath):
        transcription = cls._instance.quartznet_model.transcribe([audiopath])
        return transcription if len(transcription) == 1 else ""
    

    @classmethod
    def tn_verify_speakers(cls, voice1path, voice2path):
        embs1 = cls._instance.tn_get_embedding(voice1path).squeeze()
        embs2 = cls._instance.tn_get_embedding(voice2path).squeeze()

        # Length Normalize
        X = embs1 / torch.linalg.norm(embs1)
        Y = embs2 / torch.linalg.norm(embs2)

        # Score
        similarity_score = torch.dot(X, Y) / ((torch.dot(X, X) * torch.dot(Y, Y)) ** 0.5)
        similarity_score = (similarity_score + 1) / 2

        # Decision
        if similarity_score >= cls._instance.titanet_threshold:
            return True
        else:
            return False