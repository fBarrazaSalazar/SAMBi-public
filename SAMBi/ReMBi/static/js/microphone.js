//CREDIT TO davidgrcias https://github.com/davidgrcias/VoiceRecorderJavaScript/blob/main/vrecorder.js

const display = document.querySelector('.display')
const controllerWrapper = document.querySelector('.controllers')


const State = ['Initial', 'Record', 'Download']
let stateIndex = 0
let mediaRecorder, chunks = [], audioURL = ''
var data = [];

// mediaRecorder setup for audio
if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia){
    console.log('mediaDevices supported..')

    navigator.mediaDevices.getUserMedia({
        audio: true,
        video:false
    }).then(stream => {
        mediaRecorder = new MediaRecorder(stream)

        mediaRecorder.ondataavailable = (e) => {
            chunks.push(e.data)
        }

        mediaRecorder.onstop = (e) => {

            document.getElementById('loading'). innerHTML = 'Procesando la entrada de audio... Por favor, espere unos segundos.'
            const blob = new Blob(chunks, {'type': 'audio/ogg; codecs=opus'})
            chunks = []
            audioURL = window.URL.createObjectURL(blob)
            document.querySelector('audio').src = audioURL
    
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

           //const audio = new Audio(audioURL);
           const reader = new FileReader();
           reader.readAsDataURL(blob);
           reader.onloadend = function(){
            
                var base64 = reader.result;
                base64 = base64.split(',')[1];
                console.log(window.location.href.split('/')[5])

                $.ajax({
                    type:'POST',
                    url: 'ajax/post/audio',
                    data: {"audio":base64,"token":window.location.href.split('/')[5]},
                    success: function(response){
                        console.log(response);
                    
                        var usuario = response['usuario'];
                        var token = response['token'];
        
                        if(usuario != "NOT FOUND"){
                            document.getElementById('loading').innerHTML = 'Audio procesado exitosamente.'
                            document.getElementById("message-content2").innerHTML = "<h4> Voz verificada exitosamente, " + usuario + "</h4>";
                            document.getElementById("redirect-button").innerHTML = "<a class='btn btn-success' href=''>Continuar</a>";
                        }
                        else{
                            document.getElementById('loading').innerHTML = 'Audio procesado exitosamente.'
                            document.getElementById("message-content2").innerHTML = "Usuario no encontrado. Intente Nuevamente";
                        }
                        
                    }
        
        
                    })
    
           }
           //==============================================================================================================================
           
           console.log('sending binary data!')
           /*var form = new FormData();
           form.append('base64',base64);
           form.append('action', 'wwd_save_audio');*/

          

        }
    }).catch(error => {
        console.log('Following error has occured : ',error)
    })
}else{
    stateIndex = ''
    application(stateIndex)
}

const clearDisplay = () => {
    display.textContent = ''
}

const clearControls = () => {
    controllerWrapper.textContent = ''
}

const record = () => {
    stateIndex = 1
    mediaRecorder.start()
    application(stateIndex)
}

const stopRecording = () => {
    stateIndex = 2
    mediaRecorder.stop()
    application(stateIndex)
}

const downloadAudio = () => {
    const downloadLink = document.createElement('a')
    downloadLink.href = audioURL
    downloadLink.setAttribute('controlsList','nodownload')
}

const addButton = (id, funString, text) => {
    const btn = document.createElement('button')
    btn.id = id
    btn.setAttribute('class','btn btn-dark')
    btn.setAttribute('onclick', funString)
    btn.textContent = text
    controllerWrapper.append(btn)
}

const addMessage = (text) => {
    const msg = document.createElement('p')
    msg.textContent = text
    display.append(msg)
}

const addAudio = () => {
    const audio = document.createElement('audio')
    audio.controls = true
    audio.src = audioURL
    display.append(audio)
}
 //le pasamos un arreglo con frases para poder mostrar en la vista.
//var frases = ['Hola, muy buenos dias','El delfin comia perdiz'];

const application = (index) => {
    switch (State[index]) {
        case 'Initial':
            clearDisplay()
            clearControls()

            var timeleft = 3;
            var downloadTimer = setInterval(function(){
                if(timeleft <= 0){
                    clearInterval(downloadTimer);

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

                    $.ajax({
                        type:'POST',
                        url: 'ajax/post/frase',
                        data: false,
                        success: function(response){
                            var frase = response['frase'];
                            document.getElementById("frase").innerHTML = "<h4>Repita: "+ frase +"</h4>";
                        }
            
                    })
                    record();
                } else {
                    document.getElementById("message-content").innerHTML = "<p>Comenzando grabacion de voz en " + timeleft + " seg</p>";
                }
                timeleft -= 1;
            }, 1000);
            
            //addButton('record', 'record()', 'Start Recording')
            break;

        case 'Record':
            clearDisplay()
            clearControls()

            addMessage('Grabando voz...')
            var timeleft = 3;
            var downloadTimer = setInterval(function(){
                if(timeleft <= 0){
                    clearInterval(downloadTimer);
                    stopRecording();
                    document.getElementById("message-content").innerHTML = "<p>Grabacion Finalizada ";
                } else {
                    document.getElementById("message-content").innerHTML = "<p>Terminando grabacion en " + timeleft + " seg<p>";
                }
                timeleft -= 1;
            }, 1000);
        
            break;

        case 'Download':
            clearControls()
            clearDisplay()

            addAudio()
            addButton('record', 'record()', 'Grabar de Nuevo');
            break;

        default:
            clearControls()
            clearDisplay()

            addMessage('Your browser does not support mediaDevices')
            break;
    }

}

application(stateIndex)


function sendData(data){
let csrftoken = getCookie('csrftoken');
    let response=fetch("/voice_request", {
    method: "post",
    body: data,
    headers: { "X-CSRFToken": csrftoken },
    })
}