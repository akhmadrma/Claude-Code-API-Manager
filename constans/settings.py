# The Dictionary for Settings.json
# TODO still dont interact with actual settings
SETTINGS_DICT: object = {
    "env": {
        "ANTHROPIC_DEFAULT_HAIKU_MODEL": str,
        "ANTHROPIC_DEFAULT_SONNET_MODEL": str,
        "ANTHROPIC_DEFAULT_OPUS_MODEL": str,
        "ANTHROPIC_AUTH_TOKEN": str,
        "ANTHROPIC_BASE_URL": str,
        "API_TIMEOUT_MS": int,
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": bool,
    },
    "always_thinking_enabled": bool,
}
