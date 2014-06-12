# ---------------------------------------------------------------------------- #
# Configuration file for Jarvis window                                         #
# ---------------------------------------------------------------------------- #

# Reprensents the percentage of the screen to display jarvis window (for
# instance 0.5 takes an half screen)

WIDTH_RATIO=1.0/3.0

# By default the window takes all the height of the screen. But, if you want to
# add a little padding you can set the padding value here (in pixel)

PADDING_BOTTOM=0.0

# Set the default aspect ratio for the osg view. It can be 16.0/9.0 or 1.0.

ASPECT_RATIO=16.0/9.0

# The number of frame by second. It is the step used to manually update current
# time on video.

FRAME_SLIDER_STEP=30.0

# The number of milliseconds between each frame actually display on the screen.

FRAME_INTERVAL=1000.0/30.0

# Max out of sync time between audio and video allowed 

AUDIO_SYNC_TOLERANCE=1.0/60.0

# Set this variable to use a custom font for the debug logs and exceptions
# displayed in jarvis window.

FONT_FAMILY="Monaco"

# Set the size of the font.

FONT_SIZE=12

# Hide the slider

HIDE_SLIDER=False