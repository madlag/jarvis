# ---------------------------------------------------------------------------- #
# Configuration file for Jarvis window                                         #
# ---------------------------------------------------------------------------- #

# Reprensentes the percentage of the screen to display jarvis window (for
# instance 0.5 takes an half screen)

WIDTH_RATIO=1.0/3.0

# By default the window takes all the height of the screen. But, if you want to
# add a little padding you can set the padding value here (in pixel)

PADDING_BOTTOM=0.0

# Set the default aspect ratio for the osg view. It can be square or large.

ASPECT_RATIO_HINT="large"

# The number of frame by second. It is the step used to manually update current
# time on video.

FRAME_SLIDER_STEP=30.0

# The number of milliseconds between each frame actually display on the screen.

FRAME_INTERVAL=1.0

# Set this variable to use a custom font for the debug logs and exceptions
# displayed in jarvis window.

FONT_FAMILY="Monospace"

# Set the size of the font.

FONT_SIZE=14

# Hide the slider

HIDE_SLIDER=False