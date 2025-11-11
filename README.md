# certifying-formal-llm-judge

## Setup

Install uv:
```bash
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
mkdir -p $HOME/uv_envs 

# For BM $HOME points to lfs, due to repos at df
mkdir -p $HOME/uv_envs
# create uv virtual env
uv venv $HOME/uv_envs/veribench
```

Install project and depedencies it in uv env folder:
```bash
cd ~/no-gold-ref-judge
source $HOME/uv_envs/no-gold-ref-judge/bin/activate
uv pip install -e ~/no-gold-ref-judge
# activate uv env
uv sync --active

# TODO test later
# uv sync --active --extra lean4_pypantograph
# TODO install lean
# lake...
# if really needed see: `/lfs/skampere1/0/brando9/veribench/experiments/snap_setup.sh`
```
