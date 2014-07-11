from ConfigParser import ConfigParser
from os import path
from atexit import register

CONFIG_TEMPLATE = """
[jarvis]
# To customize your jarvis configuration, uncomment one of the following
# settings and add your custom value.
#
# aspect_ratio = 16./9. # the aspect ratio of the osg view
# width_ratio = 0.4 # the width ratio of jarvis on the screen
# padding_bottom = 0 # an optional padding at the bottom
# font_family = 'Monaco' # the font to use for debug and errors
# font_size = 12 # the size of this font
# hide_slider = False # whether add the slider in the UI
# wrap_text = False # whether wrap debug and error text
# device_pixel_ratio = 1.0 # set this variable to 2.0 for retina displays
# frame_slider_step = 30.0 # the number of frames between each slider step.
# frame_interval = 33.33 # the time interval between 2 steps (in seconds)
# audio_sync_tolerance = 1.0/60.0
"""

default_config = {
    'aspect_ratio': 16./9.,
    'width_ratio': 0.4,
    'padding_bottom': 0,
    'font_family': 'Monaco',
    'font_size': 12,
    'hide_slider': False,
    'wrap_text': False,
    'frame_slider_step': 30.0,
    'frame_interval': 33.33,
    'audio_sync_tolerance': 1.0/60.0,
    'device_pixel_ratio': 1.0,
}

try:

    # Copy default config if no config yet
    config_path = path.expanduser('~/.jarvisconfig')
    if not path.exists(config_path):
        with open(config_path, 'wb') as f:
            f.write(CONFIG_TEMPLATE)

    # Load defaults
    for name, value in default_config.items():
        globals()[name.upper()] = value

    # Update with config
    cfg = ConfigParser()
    cfg.readfp(open(config_path))
    for name, value in cfg.items('jarvis'):
        globals()[name.upper()] = eval(value)

    # Save config
    def save_config():
        for name, _ in default_config.items():
            old = cfg.get('jarvis', name) if cfg.has_option('jarvis', name) else default_config[name]
            new = globals()[name.upper()]
            if old != new:
                cfg.set('jarvis', name, '"%s"' % new if isinstance(new, str) else str(new))
        with open(config_path, 'wb') as f:
            cfg.write(f)
    register(save_config)

except:
    raise RuntimeError("The config file ~/.jarvisconfig is invalid, please remove it or replace it by a valid one.")