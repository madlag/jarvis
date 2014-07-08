from ConfigParser import ConfigParser
from os import path
from atexit import register

DEFAULT_CONFIG = """
[graphics]
aspect_ratio = 16./9.
width_ratio = 0.4
padding_bottom = 0
font_family = 'Monaco'
font_size = 12
hide_slider = False

[timing]
frame_slider_step = 30.0
frame_interval = 33.33
audio_sync_tolerance = 1.0/60.0
"""

# Copy default config if no config yet
config_path = path.expanduser('~/.jarvisconfig')
if not path.exists(config_path):
    with open(config_path, 'wb') as f:
        f.write(DEFAULT_CONFIG)

# Load config
cfg = ConfigParser()
cfg.readfp(open(config_path))
for section in cfg.sections():
    for name, value in cfg.items(section):
        globals()[name.upper()] = eval(value)

# Save config
def save_config():
    for section in cfg.sections():
        for name, value in cfg.items(section):
            value = globals()[name.upper()]
            cfg.set(section, name, '"%s"' % value if isinstance(value, str) else str(value))
    with open(config_path, 'wb') as f:
        cfg.write(f)
register(save_config)
