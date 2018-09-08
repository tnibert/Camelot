function getOffset() {
    // this isn't used anymore
    var offset = new Date().getTimezoneOffset();
    console.log(offset);
    return offset;
}

function applyOffset(UTCepoch) {
    var d = new Date(0);
    d.setUTCSeconds(UTCepoch);
    document.write(d);
}