$('.noSpecialCharacters').keypress(function (e) {
    var keyCode = e.which;
    if( !( (keyCode >= 48 && keyCode <= 57) ||(keyCode >= 65 && keyCode <= 90) || (keyCode >= 97 && keyCode <= 122)) && keyCode != 8 && keyCode != 32){
        e.preventDefault();
    }
});

$('.onlyNumbers').keypress(function (e) {
    var keyCode = e.which;
    if ( (keyCode != 8 || keyCode ==32 ) && (keyCode < 48 || keyCode > 57)) {
      return false;
    }
});

$('.onlyDecimals').keypress(function (e) {
    var keyCode = e.which;
    if ( (keyCode != 8 || keyCode ==32 ) && (keyCode < 48 || keyCode > 57) && (keyCode != 46)) {
      return false;
    }
});