KARA_FOLDER_PATH = ""
SERVER_URL = "http://127.0.0.1:8000/"
CREDENTIALS = ()
LOGGING_LEVEL = "INFO"
DELAY_BETWEEN_REQUESTS = 1
REQUESTS_LOGGING_DISABLED = True
FULLSCREEN_MODE = False
VLC_PARAMETERS = ""
LOADER_TEXT_TEMPLATE_NAME = "loader.ass"
LOADER_TEXT_TEMPLATE_DEFAULT_NAME = "loader.ass.default"
LOADER_TEXT_NAME = "loader.ass"
LOADER_BG_NAME = "loader.png"
LOADER_BG_DEFAULT_NAME = "loader.png.default"
LOADER_DURATION = 2

try:
    from local_settings import *

except ImportError:
    pass
