try:
    from importlib.metadata import version  # type: ignore
except ImportError:
    from importlib_metadata import version  # type: ignore

# App Version
VERSION = version("awesome-dl")

# ENVs
ADL_KEY = "ADL_KEY"
YTDL_CONFIG_PATH = "YTDL_CONFIG_PATH"

# App specifics
API_KEY_HEADER = "X-ADL-Key"
