$(window).on("load", function(){
    $('.rotate90').each(function() {
        // NB: because this is a rotated image, width and height will be swapped

        var maxWidth = 240;    // Max height for the image

        var width = $(this).width();    // Current image width
        var height = $(this).height();  // Current image height
        console.log(width);
        console.log(height);

        // Check if current height is larger than max
        if(width > maxWidth){
            console.log("in height adjustment");
            ratio = maxWidth / width; // get ratio for scaling image
            $(this).css("height", height * ratio);   // Scale height based on ratio
            $(this).css("width", maxWidth);    // set new width
        }
    });
});