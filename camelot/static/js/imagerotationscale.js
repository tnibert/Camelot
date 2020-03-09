$(window).on("load", function(){
    $('.rotate90').each(function() {
        // NB: because this is a rotated image, width and height will be swapped

        // max height for the image
        var maxWidth = $('.gallery-wrap').first().innerHeight();

        var width = $(this).width();    // Current image width
        var height = $(this).height();  // Current image height

        // Check if current height is larger than max
        if(width > maxWidth){
            ratio = maxWidth / width; // get ratio for scaling image
            $(this).css("height", height * ratio);   // Scale height based on ratio
            $(this).css("width", maxWidth);    // set new width
        }
    });
});