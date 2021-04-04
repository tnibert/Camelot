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
        var set_of_promises = Array();
        photofiles.forEach(function (file) {
            console.log("uploading " + String(file));
    	    set_of_promises.push(uploadPhoto(file, csrftoken, albumid));
        });

        // wait for all uploads to complete
        Promise.all(set_of_promises).then(function(values) {
            // all AJAX requests are successfully finished
            // "values" is array containing AJAX responses of all requests
            console.log("all uploads have finished");
            window.location.href = '/album/' + albumid + '/';
        }).catch(function(reason) {
            // one of the AJAX calls failed
            console.log("A photo failed to upload");
            alert(reason);
            window.location.href = '/album/' + albumid + '/';
        });
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
    return new Promise(function(resolve, reject) {
        var formData = new FormData();
        var xhr = new XMLHttpRequest();

        xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if (xhr.status === 201) {
                        console.log('successful photo upload');
                        resolve('successful photo upload');
                    } else {
                        console.log('failed to upload photo');
                        console.log(xhr.status);
                        console.log(xhr.responseText);
                        reject('A photo failed to upload: ' + xhr.status);
                    }
                }
            }

        formData.set('image', file);
        xhr.open("POST", '/api/upload/' + album_id);
        xhr.setRequestHeader("X-CSRFToken", token);
        xhr.send(formData);
    });
}
