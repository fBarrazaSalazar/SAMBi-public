# SAMBi: Sistema de Autenticación MultiBiométrica

Proyecto de título desarrollado por Vicente Salgado Jadue y Felipe Barraza Salazar.

Consiste en una aplicación web que utiliza 5 modelos de reconocimiento biométricos pre-entrenados para autenticación mediante la captura del rostro, la voz y la huella dactilar.

## Modelos pre-entrenados utilizados:

### ***Rostro:***

#### YuNet
**Propósito:** Detección de rostros <br/>
**Paper:** [YuNet: A Tiny Millisecond-level Face Detector](https://link.springer.com/content/pdf/10.1007/s11633-023-1423-y.pdf) <br/>
**Link modelo:** [https://github.com/ShiqiYu/libfacedetection](https://github.com/ShiqiYu/libfacedetection) <br/>

#### SFace
**Propósito:** Reconocimiento de rostros <br/>
**Paper:** [SFace: Sigmoid-Constrained Hypersphere Loss for Robust Face Recognition](https://arxiv.org/abs/2205.12010) <br/>
**Link modelo:** [https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface) <br/>

### ***Voz:***

#### QuartNet
**Propósito:** Transcripción de voz a texto <br/>
**Paper:** [QuartzNet: Deep Automatic Speech Recognition with 1D Time-Channel Separable Convolutions](https://arxiv.org/abs/1910.10261) <br/>
**Link modelo:** [https://huggingface.co/carlosdanielhernandezmena/stt_mt_quartznet15x5_sp_ep255_64h](https://huggingface.co/carlosdanielhernandezmena/stt_mt_quartznet15x5_sp_ep255_64h) <br/>

#### TitaNet
**Propósito:** Reconocimiento del hablante por voz <br/>
**Paper:** [TitaNet: Neural Model for speaker representation with 1D Depth-wise separable convolutions and global context](https://arxiv.org/abs/2110.04410) <br/>
**Link modelo:** [https://huggingface.co/nvidia/speakerverification_en_titanet_large](https://huggingface.co/nvidia/speakerverification_en_titanet_large) <br/>

### ***Huella dactilar:***

#### Red siamés con función de pérdida Triplet Loss
**Propósito:** Reconocimiento mediante huella dactilar <br/>
**Paper:** [Application of convolutional neural networks for fingerprint recognition](http://lup.lub.lu.se/student-papers/record/8949667/file/8949687.pdf) <br/>
**Link modelo:** [https://github.com/Abuzariii/Fingerprint-Matching-with-Siamese-Networks-Tensorflow](https://github.com/Abuzariii/Fingerprint-Matching-with-Siamese-Networks-Tensorflow) <br/>
**Nota:** Este modelo fue puesto a prueba utilizando el dispositivo de captura dactilar [Secugen Hamster Pro 20](https://secugen.com/products/hamster-pro-20/). Los drivers se encuentran en este [LINK](https://secugen.com/drivers/)
