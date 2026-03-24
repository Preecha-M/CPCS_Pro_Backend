from gradio_client import Client as GradioClient, handle_file
from . import config

gr_client = None


def get_gradio_client():
    global gr_client
    if gr_client is not None:
        return gr_client
    gr_client = GradioClient(config.HF_SPACE)
    return gr_client

__all__ = ["GradioClient", "handle_file", "gr_client", "get_gradio_client"]
