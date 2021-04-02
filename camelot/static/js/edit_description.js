$(document).ready(function(){

    // todo: currently multiple inputs can be opened at once, desired behavior?
    $('.edit-desc').click(promptForDesc);

});

function promptForDesc() {
    console.log("clicked edit desc");
    var originaltext = $(this).text();
    console.log(originaltext);
    var input = $("<input type='text' autofocus='autofocus' onKeyPress='checkEnter(event)' />");
    input.val(originaltext);
    input.focusout(function () {
        $(event.target).replaceWith(createSpanRestore(originaltext));
    });
    $(this).replaceWith(input);
    input.focus();
}

function createSpanRestore(t) {
    var spanRestore = $("<span class='edit-desc'></span>");
    spanRestore.click(promptForDesc);
    spanRestore.text(t);
    return spanRestore;
}

// http://jennifermadden.com/javascript/stringEnterKeyDetector.html
// todo: this is not just a check, change function name and return values
function checkEnter(e) { //e is event object passed from function invocation
    var characterCode; //literal character code will be stored in this variable

    if(e && e.which) { //if which property of event object is supported (NN4)
        e = e;
        characterCode = e.which //character code is contained in NN4's which property
    }
    else {
        e = event;
        characterCode = e.keyCode; //character code is contained in IE's keyCode property
    }

    if(characterCode == 13) { //if generated character code is equal to ascii 13 (if enter key)
        console.log("enter pressed");
        var new_desc = $(e.target).val();
        console.log(new_desc);

        var photoid = $(e.target).siblings(".photoid").val();
        console.log(photoid);

        // send new description to api
        var xhr = new XMLHttpRequest();
        // define success check
        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4) {
                if (xhr.status === 204) {
                    console.log('successful description update');
                    //window.location.href = '/album/' + albumid + '/';
                    // replace text on screen
                    $(e.target).replaceWith(createSpanRestore(new_desc));
                } else {
                    console.log('failed description update');
                    alert('Failed to update photo description.');
                    // todo: do we actually want to reload?
                    window.location.href = '/album/' + $("#albumid").val() + '/';
                }
            }
        }
        xhr.open("POST", '/api/update/photo/desc/' + photoid, true);
        xhr.setRequestHeader("Content-Type", "application/json");
        var csrftoken = getCookie('csrftoken');
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
        var data = JSON.stringify({"description": new_desc});
        xhr.send(data);

        console.log("Desc update sent!");

        return false;
    }
    else{
        return true;
    }

}
