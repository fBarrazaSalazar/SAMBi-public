from facial_recognition.detection.yunet import YuNet
from facial_recognition.recognition.sface import SFace

import cv2 as cv
import numpy as np
import os



class FaceID:

    _instance = None

    def __new__(cls, root_path):
        if not cls._instance:
            cls._instance = super(FaceID, cls).__new__(cls)
            cls._instance.path = root_path

            # Ruta carpeta face_recognition
            cls._instance.facial_recognition_path = root_path + '/facial_recognition/'  

            # Ubicacion base de datos de rostros
            cls._instance.local_database_path = root_path + '/database/face/'

            # Ubicación de SFace
            cls._instance.yunet_path = cls._instance.facial_recognition_path + 'detection/face_detection_yunet_2022mar.onnx'
            cls._instance.sface_path = cls._instance.facial_recognition_path + 'recognition/face_recognition_sface_2021dec.onnx'

            # YuNet y SFace
            cls._instance.recognizer = cls._instance.init_sface()
            
            cls._instance.detector = cls._instance.init_yunet()

            # Buffers
            cls._instance.__camera_initialized = False
            cls._instance.__capture = None
            cls._instance.__frame = None
            cls._instance.__face = None
        return cls._instance


        


    




    @property
    def name(cls):
        return cls._instance.__class__.__name__
    


    @classmethod
    def init_yunet(cls):
        '''
        Inicializa el detector de rostros (YuNet)

        yunet_path: ruta del archivo .onxx de YuNet

        --------------------

        returns: YuNet object
        '''

        # Valid combinations of backends and targets
        """backend_target_pairs = [
            [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_TARGET_CPU],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA_FP16],
            [cv.dnn.DNN_BACKEND_TIMVX,  cv.dnn.DNN_TARGET_NPU],
            [cv.dnn.DNN_BACKEND_CANN,   cv.dnn.DNN_TARGET_NPU]
        ]"""

        backend_id = cv.dnn.DNN_BACKEND_OPENCV # cv.dnn.DNN_BACKEND_OPENCV
        target_id = cv.dnn.DNN_TARGET_CPU # cv.dnn.DNN_TARGET_CPU

        # Instantiate YuNet for face detection
        detector = YuNet(modelPath=cls._instance.yunet_path,
                        inputSize=[320, 320],
                        confThreshold=0.9,
                        nmsThreshold=0.3,
                        topK=5000,
                        backendId=backend_id,
                        targetId=target_id)
        
        return detector
    

    @classmethod
    def init_sface(cls):
        '''
        Inicializa el reconocimiento de rostros (SFace)

        -----------------------

        return: SFace object
        '''
        # Valid combinations of backends and targets
        """backend_target_pairs = [
            [cv.dnn.DNN_BACKEND_OPENCV, cv.dnn.DNN_TARGET_CPU],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA],
            [cv.dnn.DNN_BACKEND_CUDA,   cv.dnn.DNN_TARGET_CUDA_FP16],
            [cv.dnn.DNN_BACKEND_TIMVX,  cv.dnn.DNN_TARGET_NPU],
            [cv.dnn.DNN_BACKEND_CANN,   cv.dnn.DNN_TARGET_NPU]
        ]"""

        backend_id = cv.dnn.DNN_BACKEND_OPENCV # cv.dnn.DNN_BACKEND_OPENCV
        target_id = cv.dnn.DNN_TARGET_CPU # cv.dnn.DNN_TARGET_CPU

        dis_type = 0

        # Instantiate SFace for face recognition
        recognizer = SFace(modelPath=cls._instance.sface_path,
                        disType=dis_type,
                        backendId=backend_id,
                        targetId=target_id)
        
        
        return recognizer


    @classmethod
    def match_localdb(cls, frame):
        '''
        Se busca si el rostro capturado se encuentra en el dataset. 
        Retorna True si encuentra el rostro en la base de datos, False en caso contrario.

        input: imagen capturada por la camara
        yunet_dataset_path: ruta donde se encuentra el directorio del dataset

        Returns: boolean
        '''
        labels = os.listdir(cls._instance.local_database_path)
        cls._instance.detector.setInputSize([frame.shape[1], frame.shape[0]])
        face1 = cls._instance.detector.infer(frame)

        print(f'(*) Buscando...')
        
        for person_dir in labels:
            img_list = os.listdir(cls._instance.local_database_path + person_dir)
            
            for img_item in img_list:
                img_path = os.path.join(cls._instance.local_database_path, person_dir, img_item)
                img = cv.imread(img_path)
                #print(f'(*) Buscando: {img_path}')
                
                cls._instance.detector.setInputSize([img.shape[1], img.shape[0]])
                face2 = cls._instance.detector.infer(img)
                if face2.shape[0] == 0:
                    continue

                result = cls._instance.recognizer.match(frame, face1[0][:-1], img, face2[0][:-1])
                if result:
                    #print(f'(+) ENCONTRADO!: {yunet_dataset_path + person_dir}')
                    person_id = person_dir.split("_", 1)[0]
                    person_name = person_dir.split("_", 1)[1]
                    return True, person_id, person_name
            
        #print('(-) NO SE ENCUENTRA EN LA BASE DE DATOS')
        return False, None, None


    @classmethod
    def visualize(cls, image, results, text_color=(0, 0, 255), fps=None):
        '''
        Funcion que muestra donde se detectó el rostro, utilizando un rectángulo.
        También muestra los fps de la cámara.
        '''
        output = image.copy()
        '''
        landmark_color = [
            (255,   0,   0), # right eye
            (  0,   0, 255), # left eye
            (  0, 255,   0), # nose tip
            (255,   0, 255), # right mouth corner
            (  0, 255, 255)  # left mouth corner
        ]
        '''

        box_color = (0,255,255)

        if fps is not None:
            cv.putText(output, 'FPS: {:.2f}'.format(fps), (0, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, text_color)

        for det in (results if results is not None else []):
            bbox = det[0:4].astype(np.int32)
            cv.rectangle(output, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), box_color, 2)

            conf = det[-1]
            cv.putText(output, '{:.4f}'.format(conf), (bbox[0], bbox[1]+12), cv.FONT_HERSHEY_DUPLEX, 0.5, text_color)

        return output
    

    @classmethod
    def search_face_id(cls):
        deviceId = 0
        cap = cv.VideoCapture(deviceId)
        w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        cls._instance.detector.setInputSize([w, h])

        tm = cv.TickMeter()
        while cv.waitKey(1) < 0:
            hasFrame, frame = cap.read()
            if not hasFrame:
                print('No frames grabbed!')
                break

            # Inference
            tm.start()
            cls._instance.detector.setInputSize([frame.shape[1], frame.shape[0]])
            results = cls._instance.detector.infer(frame) # results is a tuple
            found = False
            if results is not None:
                print("(+) Rostro detectado.")
                found, person_id, person_name = cls._instance.match_localdb(frame)

                if person_id is not None and person_name is not None:
                    return person_id, person_name
            tm.stop()

            # Draw results on the input image
            frame = cls._instance.visualize(frame, results, fps=tm.getFPS())

            # Visualize results in a new Window
            cv.imshow('YuNet Demo', frame)

    def is_face_detected(cls, img):
        cls._instance.detector.setInputSize([img.shape[1], img.shape[0]])
        results = cls._instance.detector.infer(img)
        if results is not None:
            img = cls._instance.visualize(img, results)
            return True, img
        return False, img


    @classmethod
    def is_face_authenticated(cls, img1, img2):
        cls._instance.detector.setInputSize([img1.shape[1], img1.shape[0]])
        face1 = cls._instance.detector.infer(img1)
        face2 = cls._instance.detector.infer(img2)
        print("img1")
        print(img1)
        print("img2")
        print(img2)
        if face1 is not None and face2 is not None:
            result = cls._instance.recognizer.match(img1, face1[0][:-1], img2, face2[0][:-1])
            if result == 1:
                return True
        
        return False

            
