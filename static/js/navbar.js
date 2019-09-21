/*
navbar.js
Description: navbar.js handles the visibility of the brand's logo in the navbar.
Author: Alfarhan Zahedi
Date: 7th September, 2019
*/

// This function checks if the passed DOM element is in the current viewport or not, and
// returns the appropriate boolean.
function isElementInViewport (element) {
    if (typeof jQuery === 'function' && element instanceof jQuery) {
        element = element[0];
    }

    var y = element.offsetTop;
    var height = element.offsetHeight;

    while (element = element.offsetParent)
        y += element.offsetTop;

    var maxHeight = y + height;
    var isVisible = (y < (window.pageYOffset + window.innerHeight)) 
                    && (maxHeight >= window.pageYOffset);
    return isVisible; 
}

// This function calls the callback function whenever the 'visibility' of the element changes
// i.e. when the element goes out of the viewport or when it comes into the viewport.
function onVisibilityChange(element, callback) {
    var old_visible;
    return function () {
        var visible = isElementInViewport(element);
        if (visible != old_visible) {
            old_visible = visible;
            if (typeof callback == 'function') {
                callback();
            }
        }
    }
}

// Grab the banner.
var element = $('#banner');

var handler = onVisibilityChange(element, function() {
    // If the banner is in the viewport, hide the logo in the navbar and center-align the
    // contents of the navbar.
    if (isElementInViewport(element)) {
        $('#navbar-logo').fadeOut(0);
        $('.navbar-nav').removeClass('ml-auto');
        $('.navbar-nav').addClass('justify-content-center');
    } 
    // If the banner is not in the viewport, show the logo in the navbar and right-align the 
    // contents of the navbar.
    else {
        $('#navbar-logo').fadeIn(0);
        $('.navbar-nav').addClass('ml-auto');
        $('.navbar-nav').removeClass('justify-content-center');
    }
});

// Trigger the 'handler' (defined above) on resize, load and scroll!
$(window).on('DOMContentLoaded load resize scroll', handler); 