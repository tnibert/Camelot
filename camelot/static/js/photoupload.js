//https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form

$(document).ready(function(){
    form_count = Number($("[name=extra_field_count]").val());
    // get extra form count so we know what index to use for the next item.
    //console.log(form_count)

    $("#add-another").click(function() {
        form_count ++;
        //console.log(form_count)

        // build elements and append to our forms container
        enclose = $('<p>')

        element = $('<label>File: </label>');
        enclose.append(element);

        element = $('<input type="file"/>');
        element.attr('name', 'file');
        enclose.append(element);

        $("#forms").append(enclose);

        // create new p element
        enclose = $('<p>')

        element = $('<label>Description: </label>');
        enclose.append(element);

        element = $('<input type="text"/>');
        element.attr('name', 'desc_' + form_count);
        enclose.append(element);

        $("#forms").append(enclose);

        //$("#forms").append($('</p>'));

        $("[name=extra_field_count]").val(form_count);
        // increment form count so our view knows to populate
        // that many fields for validation
    });

    // submit photos via API calls
    $("form").on('submit', function (e) {
        // todo: https://simpleisbetterthancomplex.com/tutorial/2016/11/22/django-multiple-file-upload-using-ajax.html
        var photos = new FormData(); //new FormData(document.getElementById("uploadphotosform"));

        photos.append('image', $('#id_file')[0].files[0]);

        var albumid = document.getElementById("albumid").value;

        /*oForm = document.getElementById("uploadphotosform");
        console.log(oForm.elements.length);
        console.log(oForm.elements);
        for (var prop in oForm.elements) {
            console.log(prop.value);
        }*/

        /*var oReq = new XMLHttpRequest();
        oReq.open("POST", "api/upload/id", true);
        oReq.onload = function(oEvent) {
        if (oReq.status == 201) {
            oOutput.innerHTML = "Uploaded!";
        } else {
            oOutput.innerHTML = "Error " + oReq.status + " occurred when trying to upload your file.<br \/>";
        }*/

        $.ajax({
            type: 'POST',
            data: photos,
            url: '/api/upload/' + albumid,
            dataType: 'multipart/form-data',
            contentType: false,
            processData: false,
            statusCode: {
                201: function () {
                    console.log("Uploaded!");
                    window.location.href = '/album/' + albumid + '/';
                }
                // todo: handle error
            }
        }).done(function (response) {
            console.log("In done...");
        });

        //stop form submission
        e.preventDefault();
    });
});

/*
<p>
        <label for="id_file">File:</label><br>
        <input type="file" name="file" required id="id_file" />


      </p>
*/

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