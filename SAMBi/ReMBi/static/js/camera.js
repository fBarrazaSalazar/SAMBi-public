

var video = document.getElementById('video');

//obtener el acceso a la camara del computador
//con este metodo se verifica la informacion del navegador. 
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
    navigator.mediaDevices.getUserMedia({
        video: true,
    }).then(function(stream){
        video.srcObject = stream;
        video.play();
    }) 
}