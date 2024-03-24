from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.core.files.storage import default_storage
from .models import User,Face,Voice,Finger,Logs,Person
from django.core.files.storage import default_storage
from binascii import a2b_base64
from subprocess import Popen,PIPE
import re
import cv2 as cv
import os
from cryptography.fernet import Fernet ## pip install cryptography
from facial_recognition.faceID import FaceID
from speaker_recognition.VoiceID import VoiceID
from .apps import RembiConfig
from pydub import AudioSegment
import base64

# Create your views here.
def autherror(request):
    return render(request,"html/autherror.html",{})

def base(request):
    return redirect('inicio')

def index(request):
    return render(request,"html/inicio.html",{})

def facerecon(request):
    return render(request,"html/facerecon.html",{})

def voicerecon(request,token):
    ##data base request si existe la contrasena y la retorna
    user = User.objects.get(token=token)
    user_data = user.__dict__
    #busca la llave dentro de la base de datos
    key = user_data['key']
    clave_basedatos = user_data['username']
    fernet = Fernet(key)

    ## VER EXCEPTION PARA REDIRECCIONAR 
    decMessage = fernet.decrypt(token).decode()
    if(request.method == "GET"):
        if(clave_basedatos == decMessage):
            return render(request,"html/voicerecon.html",{
                'token' : token
            })

def fingerrecon(request):
    return 0

def detect_face(request):
    if (request.method == 'POST'):

        #carga las imagenes en una lista
        data_rostros = list(Face.objects.values())
 
        image = request.POST.get('image')

        imgstr = re.search(r'base64,(.*)', image).group(1)

        binary_data = a2b_base64(imgstr)

        Out = open('tmp/snapshot.jpg', 'wb') ## guarda el snapshot de la pagina
        Out.write(binary_data)
        Out.close()

        #lo que se puede hacer despues es guardar en la base de datos el url de la imagen y al traerlo desde la base de datos, transformarlo.
        #La imagen hay que guardarla en tipo text, ya que es un string muy largo.

        faceID = RembiConfig.faceID
        print("faceID creado!")
        
        #face1 = cv.resize(cv.imread('/root/SAMBi/interfaz/SAMBi/snapshot.jpg'), (720,1280))
        #face2 = cv.resize(cv.imread('/root/SAMBi/database/face/7_Vicente_Salgado/vs.jpg'),(720,1280))

        for data in data_rostros:
            face1 = cv.resize(cv.imread(os.path.join(os.getcwd(), 'tmp/snapshot.jpg')), (1280,720))
            print("rostro detectado? face1",faceID.is_face_detected(face1))
            face2 = cv.resize(cv.imread(os.path.join(os.getcwd(), data['face_data'])),(1280,720))
            print("rostro detectado? face2",faceID.is_face_detected(face2))

            print("Implementando reconocimiento...")
            was_recognized = faceID.is_face_authenticated(face1, face2)
            print("Fin!")
            print(was_recognized)
            if(was_recognized):
                user_id = data['user_id_id']#obtiene el id del usuario
                user = User.objects.get(user_id=user_id) #busca en la tabla users

                user_data = user.__dict__ #adquiere todos los datos de la fila para obtener el token
                person = Person.objects.get(user_id=user_id) #obtiene los datos de la persona
                person_data = person.__dict__

                break    
        
    

        if (was_recognized == True):
            message = {"usuario":person_data['name']+' '+person_data['last_name'],"token":user_data['token']}#codigo}
        else:
            message = {"usuario":"NOT FOUND"}


        
    return JsonResponse(message)

def set_and_return_phrase(request):
    voiceID = RembiConfig.voiceID
    voiceID.qn_choose_random_phrase()
    frase = {'frase':voiceID.get_phrase()}

    print(frase)

    return JsonResponse(frase)

def detect_voice(request):
    if(request.method =="POST"):    
        
        voiceID = RembiConfig.voiceID
        print("voiceID creado!")

        encoded_audio = request.POST.get('audio')
        token = request.POST.get('token')
        print(token)
        user = User.objects.get(token = token) #se llama al usuario
        user_data = user.__dict__   #se pone la data en un diccionario
        user_id = user_data['user_id'] #se extrae el user id

        voice = Voice.objects.get(user_id=user_id)
        voice_data = voice.__dict__
        voice_file = voice_data['voice_data']

        #se escribe como webm
        wav_file = open('tmp/audio_sample.ogg','wb')
        decode_string = base64.b64decode(encoded_audio)
        wav_file.write(decode_string)

        #ahora transformamos a wav usando ffmpeg ya que es la unica perra forma de poder transformarlo y que conserve bien el formato de los headers.
        #por ende el sistema debe tener instalado FFMPEG
        input = os.getcwd() + '/tmp/audio_sample.ogg'
        output = os.getcwd() + '/tmp/audio_sample.wav'
        os.system('ffmpeg -y -i '+input+' -vn -ar 16000 '+ output)


        print("Implementando reconocimiento...")
        
        voz_capturada = output
        voz_guardada = voice_file   #la voz de cada persona

        frase_transcrita = voiceID.qn_transcribe_wav(voz_capturada)
        similar_phrase_flag = voiceID.qn_is_sentence_correct(frase_transcrita) 
        print(similar_phrase_flag)
        was_recognized = voiceID.tn_verify_speakers(voz_capturada, voz_guardada)  #se verifica si existe la persona
        print(was_recognized)
        if (was_recognized == True & similar_phrase_flag == True):
            person = Person.objects.get(user_id=user_id) #obtiene los datos de la persona
            person_data = person.__dict__
            message = {"usuario":person_data['name']+' '+person_data['last_name'],"token":token}#codigo}   
        else:
            message = {"usuario":"NOT FOUND"}
    
        
    return JsonResponse(message)

