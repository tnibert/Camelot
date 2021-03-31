console.log("loaded");
$(document).ready(function(){

    // todo: currently multiple inputs can be opened at once, desired behavior?
    $('.edit-desc').click(function(){
        console.log("clicked edit desc");
        var input = document.createElement("INPUT");
        input.type = "text";
        $(this).replaceWith("<input type='text' onKeyPress='checkEnter(event)' />");
    });

});

// http://jennifermadden.com/javascript/stringEnterKeyDetector.html
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

        // todo: send new description via api

        // replace text on screen
        var span = document.createElement("SPAN");
        span.textContent = new_desc;
        $(e.target).replaceWith(span);
        return false;
    }
    else{
        return true;
    }

}
