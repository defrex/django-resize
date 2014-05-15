[![Build Status](https://travis-ci.org/defrex/django-resize.svg)](https://travis-ci.org/defrex/django-resize)

## django-resize

Simple Django Image Resizing

This template tag resizes images.

It will resize the image once, saving the result to disk. Subquestion calls
for the same resize will then result in returning the saved result, so that
the resizing action isn't performed each time.

The size argument can be in one of two forms: `width` or `widthxheight`. `auto`
is an acceptable value for either. Some examples:

`{{ img|resize:50 }}` - this will set with width to 50, with the height scaled
accordingly.

`{{ img|resize:'auto' }}` - this won't resize the image at all

`{{ img|resize:'50x50' }}` - the width and height will be 50px, causing the
image to be letterboxed (never stretched).

`{{ img|resize:'autox50' }}` - this will set the height and scale the width
