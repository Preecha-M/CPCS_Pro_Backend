from gradio_client import Client as GradioClient, handle_file
from . import config

gr_client = GradioClient(config.HF_SPACE)

__all__ = ["GradioClient", "handle_file", "gr_client"]
