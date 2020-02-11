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
