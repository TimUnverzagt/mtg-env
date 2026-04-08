# Exporting RepoRoot
export REPO_ROOT=$(pwd)

# Generating/Updatin python environment
cd $REPO_ROOT
uv sync


# Running main.py as root (req by keyboard)
cd $REPO_ROOT/src/mtggympy
uv  main.py

# Profiling main.py (Untested with uv)
cd $REPO_ROOT/src/mtggympy
spy_py record -o profile.svg -- python main.py 