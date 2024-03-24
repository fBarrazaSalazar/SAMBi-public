from django.urls import path

from . import views

# el param name es para la redirección dentro de las views.
urlpatterns = [
    path("inicio", views.index, name="inicio"),
    path("facerecon",views.facerecon,name="facerecon"),
    path("voicerecon/<str:token>",views.voicerecon,name="voicerecon"),
    path("autherror",views.autherror,name="autherror"),
    path("ajax/post/image",views.detect_face,name="detect_face"),
    path("voicerecon/ajax/post/audio",views.detect_voice,name="detect_voice"),
    path("voicerecon/ajax/post/frase",views.set_and_return_phrase,name ='get_phrase')
]
