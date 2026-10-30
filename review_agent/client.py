"""Thin wrapper around the OpenAI-compatible Nebius Token Factory API."""
import os

from openai import OpenAI

DEFAULT_BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b"

ENV_API_KEY = "NEBIUS_API_KEY"
ENV_BASE_URL = "NEBIUS_BASE_URL"
ENV_MODEL = "NEMOTRON_MODEL"


def get_api_key(explicit=None):
    key = explicit or os.environ.get(ENV_API_KEY)
    if not key:
        raise RuntimeError(
            f"{ENV_API_KEY} is not set. Create a key at "
            f"https://tokenfactory.nebius.com/ and export {ENV_API_KEY}=<your-key>."
        )
    return key


def get_client(base_url=None, api_key=None):
    return OpenAI(
        base_url=base_url or os.environ.get(ENV_BASE_URL, DEFAULT_BASE_URL),
        api_key=get_api_key(api_key),
    )


def get_model(explicit=None):
    return explicit or os.environ.get(ENV_MODEL, DEFAULT_MODEL)


def list_models(client):
    """Return [(model_id, owned_by), ...] for models served by Token Factory."""
    models = client.models.list()
    return [(m.id, getattr(m, "owned_by", "")) for m in models.data]
