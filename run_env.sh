# Shared env for train/eval runs on this box.
export PYTHONPATH=/workspace/claude_pai_exp/hfpatch:$PYTHONPATH
export HF_LOGIN_NOOP=1
export HF_HUB_OFFLINE=1
export TUBERLENS_MAX_MEMORY="cuda:0=22GiB,cpu=45GiB"
export MAX_MEMORY="cuda:0=22GiB,cpu=45GiB"
