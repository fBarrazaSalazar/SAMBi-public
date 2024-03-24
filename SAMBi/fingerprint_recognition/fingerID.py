from fingerprint_recognition.lib_secugen.pysgfplib import *
from ctypes import *
from PIL import Image
from keras import backend as K
from keras.models import load_model
import cv2

import numpy as np
import cv2
import datetime
import os
import time

class FingerID:
    _instance = None
    def __new__(cls, root_path):
        if not cls._instance:
            cls._instance = super(FingerID, cls).__new__(cls)
            # Ruta carpeta fingerprint_recognition
            cls._instance.path_finger_dir = os.path.join(root_path, 'fingerprint_recognition')

            # Ubicacion base de datos de huellas
            cls._instance.path_local_database = os.path.join(root_path, '..', '..', 'database', 'finger')

            cls._instance.path_tmp_dir = os.path.join(root_path, 'ReMBi', 'media', 'tmp')

            cls._instance.model_path = os.path.join(root_path, 'fingerprint_recognition', 
                                          'models', 'model_siamese_net1_r.h5')
            cls._instance.model = load_model(cls._instance.model_path, compile=False, custom_objects={'K': K})

            cls._instance.threshold = 0.1

            cls._instance.sgfplib = PYSGFPLib()
        return cls._instance

    
    @property
    def name(cls):
        return cls._instance.__class__.__name__


    @classmethod
    def StartAutoOn(cls):
        StartAutoOn = False
        print('Calling EnableAutoOnEvent(True) ... ')
        result = cls._instance.sgfplib.EnableAutoOnEvent(True)
        print("\treturned "+ str(result));  
        if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
            StartAutoOn = True
        return StartAutoOn

    @classmethod
    def StopAutoOn(cls):
        StopAutoOn = False
        print('Calling EnableAutoOnEvent(False) ... ')
        result = cls._instance.sgfplib.EnableAutoOnEvent(False)
        print("\treturned "+ str(result));  
        if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
            StopAutoOn = True
        return StopAutoOn


    @classmethod
    def init(cls):
      print("(init) Create...")
      try:
        result = cls._instance.sgfplib.Create()
      except:
        raise SystemError("Dispositivo SecuGen no conectado/detectado!")

      
      if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
        print("  ERROR - Unable to open SecuGen library. Exiting\n")
        exit()

      result = cls._instance.sgfplib.Init(SGFDxDeviceName.SG_DEV_AUTO)

      if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
        print("  ERROR - Unable to initialize SecuGen library. Exiting\n")
        exit()

      return True


    @classmethod
    def scan(cls):

      print('Call sgfplib.OpenDevice()')
      result = cls._instance.sgfplib.OpenDevice(0)
      print('  Returned : ' + str(result))

      if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
      #{
        print("  ERROR - Unable to open the SecuGen device. Exiting\n")
        exit()
      else:

        #///////////////////////////////////////////////
        #// GetDeviceInfo()
        cImageWidth = c_int(0)
        cImageHeight = c_int(0)
        print('+++ Call sgfplib.GetDeviceInfo()')
        result = cls._instance.sgfplib.GetDeviceInfo(byref(cImageWidth), byref(cImageHeight))
        print('  Returned : ' + str(result)) 
        print('  ImageWidth  : ' + str(cImageWidth.value))
        print('  ImageHeight : ' + str(cImageHeight.value))

        #///////////////////////////////////////////////
        cls._instance.cImageBuffer1 = (c_char*cImageWidth.value*cImageHeight.value)()

        #///////////////////////////////////////////////
        #// Set Callback Function
        result = cls._instance.sgfplib.SetCallBackFunction()
        print("SetCallBackFunction()  returned ... " + str(result));
        if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
          print("\tFAIL\n")
          exit();
        else:
          print("\tSUCCESS\n");

          if (cls._instance.StartAutoOn()):
            n=0  #//Visual feedback
            while (True):
              if (cls._instance.sgfplib.FingerPresent()):
                n=0  #//Reset visual feedback
                print("Finger Present\n")
                if (cls._instance.StopAutoOn() == 0):
                  print("StopAutoOn() returned False.\n")
                  break
                print("Call GetImage()\n")
                result = cls._instance.sgfplib.GetImage(cls._instance.cImageBuffer1)
                print('GetImage() returned ... '  + str(n)+ '\n')
                if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
                  print("FAIL\n")
                else:
                  print("SUCCESS\n")
                  #path_raw = os.path.join(os.getcwd(), 'fingerprint_recognition', 'testing', "auto_on_test.raw")
                  path_pgm = os.path.join(os.getcwd(), 'ReMBi', 'media', 'tmp', "fp.pgm")
                  path_bmp = os.path.join(os.getcwd(), 'ReMBi', 'media', 'tmp', "fp.bmp")
                  
                  print(path_pgm)
                  print(path_bmp)
                  print("Generando .bmp...", end=" ")
                  """ with open(path_raw, "wb") as image1File:
                      print(path_raw)
                      image1File.write(cls._instance.cImageBuffer1) """

                  pgmImageBuffer1 = b"P5\n300 400\n255\n" + cls._instance.cImageBuffer1
                  with open(path_pgm, "wb") as pgmimage1File:
                      pgmimage1File.write(pgmImageBuffer1)
                  print("pgm creado (300x400)...", end=" ")

                  img_pgm = Image.open(path_pgm)
                  img_pgm_resized = img_pgm.resize((96,103))
                  img_pgm_resized.save(path_bmp)
                  print("bmp creado (96x103)...")
                  print(".............................................................\n")
                  cls._instance.cImageBuffer1 = None
                  is_authenticated, person_dir = cls._instance.match_localdb(path_bmp)
                  break
              else:
                print("Finger Not Present\n")
                time.sleep(0.5)
                n=n+1 #//Visual feedback
                print('place finger on sensor ... '  + str(n))     
              #}if fingerPresent
            #}end while
          else:
            print("StartAutoOn() returned False.\n")
        #}

        #//////////////////////////////////////////////////////////////////////////
        #// EnableAutoOnEvent(false)
        print("Call sgfplib->EnableAutoOnEvent(false) ... \n");
        result = cls._instance.sgfplib.EnableAutoOnEvent(False);
      
        print('+++ Call sgfplib.CloseDevice()')
        result = cls._instance.sgfplib.CloseDevice()
        print('  Returned : ' + str(result))

        return is_authenticated, person_dir

    @classmethod
    def terminate(cls):
        print('+++ Call sgfplib.Terminate()')
        result = cls._instance.sgfplib.Terminate()
        print('  Returned : ' + str(result))


    @classmethod
    def compute_distance(cls, fp1, fp2):
      fp1 = np.around(np.transpose(cv2.resize(fp1, (96, 96))/255.0, \
                                         (2, 0, 1)), \
                                          decimals=6)
      fp2 = np.around(np.transpose(cv2.resize(fp2, (96, 96))/255.0, \
                                         (2, 0, 1)), \
                                          decimals=6)
      
      fp1_enc = cls._instance.model.predict_on_batch(np.expand_dims(fp1, 0))
      fp2_enc = cls._instance.model.predict_on_batch(np.expand_dims(fp2, 0))
      print(np.linalg.norm(abs(fp1_enc - fp2_enc)))
      return np.linalg.norm(abs(fp1_enc - fp2_enc))
    

    @classmethod
    def match_fp(cls, fp1, fp2):
       return True if cls._instance.compute_distance(fp1, fp2) <= cls._instance.threshold else False


    @classmethod
    def match_localdb(cls, path_bmp):
      labels = os.listdir(cls._instance.path_local_database)

      print(f'(*) Buscando...')
      
      for person_dir in labels:
          person_path = os.path.join(cls._instance.path_local_database, person_dir)
          img_list = os.listdir(person_path)
          
          for img_item in img_list:
              path_fpdb = os.path.join(person_path, img_item)
              if os.path.isdir(path_fpdb): continue

              fpdb_bmp = cv2.imread(path_fpdb)
              img_bmp = cv2.imread(path_bmp)

              if cls._instance.match_fp(img_bmp, fpdb_bmp):
                 return True, person_dir
      return False, None









              
              
