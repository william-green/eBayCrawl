import os


def test_telegram_api_key_env_var_is_set():
    """Telegram_API_KEY must be set in the environment before the app can run."""
    api_key = os.environ.get("Telegram_API_KEY")
    assert api_key, (
        "Telegram_API_KEY is not set. "
        "Set it as a Jenkins credential or environment variable."
    )


def test_telegram_channel_id_env_var_is_set():
    """Telegram_Channel_id must be set in the environment before the app can run."""
    channel_id = os.environ.get("Telegram_Channel_id")
    assert channel_id, (
        "Telegram_Channel_id is not set. "
        "Set it as a Jenkins credential or environment variable."
    )
