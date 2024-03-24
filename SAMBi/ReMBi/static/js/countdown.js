// TIMER DE LA FOTO
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

// TIMER DEL SITIO WEB
var timeleft = 5;
var downloadTimer = setInterval(function(){
    if(timeleft <= 0){
        clearInterval(downloadTimer);
        document.getElementById("message-content").innerHTML = "Foto Tomada";
    } else {
        document.getElementById("message-content").innerHTML = "<h3>Foto en " + timeleft + " seg</h3>";
    }
    timeleft -= 1;
    
    if(timeleft == -1){
        var canvas = document.createElement('canvas');
        canvas.setAttribute('id','face-snapshot'); //se le pone un id a la imagen, en este caso "face-snapshot"
        canvas.setAttribute('width',500);
        canvas.setAttribute('height',340);
        var context = canvas.getContext('2d');

        canvas.className = 'canvas';
        document.getElementById("image-taken").appendChild(canvas);
        context.drawImage(video,0,0,500,340);
        document.getElementById("button-box").innerHTML = "<a id='reset' class='btn btn-dark' href='facerecon'> Tomar Nueva Foto </a>";

        var flag = true;

        if(flag){

            //segundo timer del sitio para hacer el proceso y darle tiempo al usuario de poder tomar una nueva foto
            var new_timeleft = 3;
            var newTimer = setInterval(function(){
                if(new_timeleft <= 0){
                    clearInterval(newTimer);
                    document.getElementById("message-content2").innerHTML = "Comenzando identificacion de imagen... " ;
                } else {
                    document.getElementById("message-content2").innerHTML = "Comenzando identificacion de imagen... " + new_timeleft + " seg";
                }
                new_timeleft -= 1;

                if(new_timeleft == -1){
                    $.ajaxSetup({       //cookies security 
                        beforeSend: function(xhr, settings) {
                            function getCookie(name) {
                                var cookieValue = null;
                                if (document.cookie && document.cookie != '') {
                                    var cookies = document.cookie.split(';');
                                    for (var i = 0; i < cookies.length; i++) {
                                        var cookie = jQuery.trim(cookies[i]);
                                        // Does this cookie string begin with the name we want?
                                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                            break;
                                        }
                                    }
                                }
                                return cookieValue;
                            }
                            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                                // Only send the token to relative URLs i.e. locally.
                                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                            }
                        } 
                   });
                    
                    var image = document.getElementById('face-snapshot'); //se busca el canvas por el id
                    var imageURL = image.toDataURL("image/jpeg",1); //se transforma la imagen en un string de URL para insertarlo por GET al ajax.

                    
                    $.ajax({
                        type:'POST',
                        url: 'ajax/post/image',
                        data: {image: imageURL},
                        success: function(response){
                            console.log(response);
                            var usuario = response['usuario'];
                            var token = response['token'];

                            if(usuario != "NOT FOUND"){
                                document.getElementById("message-content2").innerHTML = "<h4>Bienvenido, " + usuario + ".</h4>";
                                document.getElementById("redirect-button").innerHTML = "<a class='btn btn-success' href='voicerecon/"+token+"'>Continuar</a>";
                            }
                            else{
                                document.getElementById("message-content2").innerHTML = "Usuario no encontrado. Intente Nuevamente";
                            }
                            
                        }
    
                    })
    
                }
        
            }, 1000);

            
        }

    }


}, 1000);


