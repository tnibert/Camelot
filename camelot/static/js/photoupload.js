// https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form
// https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html
// todo: reset uploading text on failure
// todo: can fail to update description and hang on this screen during upload

$(document).ready(function(){

    // submit photos via API calls
    $("form").on('submit', function (e) {

        //stop form submission
        e.preventDefault();

        // gather data
        var photos = new FormData(this);
        var photofiles = photos.getAll("file");
        var albumid = document.getElementById("albumid").value;
        var csrftoken = getCookie('csrftoken');

        // replace submit button with "uploading..."
        var myAnchor = document.getElementById("sendupload");
        var mySpan = document.createElement("span");
        mySpan.innerHTML = "Uploading...";
        myAnchor.parentNode.replaceChild(mySpan, myAnchor);

        // upload photos
        photofiles.forEach(function (file) {
            console.log("uploading " + String(file));
    	    uploadPhoto(file, csrftoken, albumid);
        });

        /*
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                // use csrf token
                if (!(/^http:..test(settings.url) || /^https:..test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
                

            }
        });

        $.ajax({
            type: 'POST',
            data: photos,
            url: '/api/upload/' + albumid,
            dataType: 'json',
            contentType: false,
            processData: false,
            statusCode: {
                201: function (response) {
                    console.log("Uploaded!");
                    window.location.href = '/album/' + albumid + '/';
                }
            },
            // handle error case
            error: function(jqXHR, textStatus, errorThrown) {
                alert('Ooowee.. we could not upload that photo.  Check javascript console for more info if so inclined.');

                //$('#result').html('<p>status code: '+jqXHR.status+'</p><p>errorThrown: ' + errorThrown + '</p><p>jqXHR.responseText:</p><div>'+jqXHR.responseText + '</div>');
                console.log('jqXHR:');
                console.log(jqXHR);
                console.log('textStatus:');
                console.log(textStatus);
                console.log('errorThrown:');
                console.log(errorThrown);
            }
        }).done(function (response) {
            console.log("In done...");
        });
        */

    });
});

// probably wont use this but keeping for now
function DuplicateIn() {

  var formInvalid = false;
  $('#register_form input').each(function() {
    if ($(this).val() === '') {
      formInvalid = true;
    }
  });

  if (formInvalid)
    alert('One or Two fields are empty. Please fill up all fields');
}

function uploadPhoto(file, token, album_id) {
  	var formData = new FormData();
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 201) {
                    console.log('successful photo upload');
                } else {
                    console.log('failed to upload photo');
                    //window.location.href = '/album/' + $("#albumid").val() + '/';
                }
            }
        }

    formData.set('image', file);
    xhr.open("POST", '/api/upload/' + album_id);
    xhr.setRequestHeader("X-CSRFToken", token);
    xhr.send(formData);
}
