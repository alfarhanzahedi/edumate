/*
helper.js
Description: helper.js contains all the functions that are required by all the other JS 
             scripts across the codebase.
Author: Alfarhan Zahedi
Date: 11th February, 2020
*/

// This function copies the text of the jQuery 'element' passed to it to the clipboard.
function copyToClipboard(element) {
    let inputElement = $("<input>");
    $("body").append(inputElement);
    inputElement.val($(element).text()).select();
    document.execCommand("copy");
    inputElement.remove();
}

/**
 * ``getCookie`` extracts and returns the value of the cookie identified by ``name``.
 * @param {string} name The name of the cookie.
 * @returns {string} The value of the cookie identified by ``name``.
 */
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
