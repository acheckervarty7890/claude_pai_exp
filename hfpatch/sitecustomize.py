"""Bypass huggingface_hub's login round-trip when the HF token has expired.

The gemma-3-27b-it weights are already fully in the local HF cache, but
``tuberlens.utils.hf_login`` calls ``huggingface_hub.login`` unconditionally, which
needs a live /whoami-v2 call. With an expired token that call 401s (and under
HF_HUB_OFFLINE=1 it raises outright), so model loading fails even though nothing
needs to be fetched. Activated only when HF_LOGIN_NOOP=1, and only ever combined
with HF_HUB_OFFLINE=1 so every resolution comes from the local cache.
"""

import os

if os.environ.get("HF_LOGIN_NOOP") == "1":
    try:
        import huggingface_hub

        huggingface_hub.login = lambda *a, **k: None
        huggingface_hub.interpreter_login = lambda *a, **k: None
    except Exception:
        pass
