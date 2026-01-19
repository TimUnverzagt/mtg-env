# Generating python environment
cd $REPO_ROOT
conda env create -f environment.yaml --prefix ./envs/mtg-py-env

# Updating python environment
cd $REPO_ROOT
conda env update -f environment.yaml --prefix ./envs/mtg-py-env

# Activating python environment
conda activate $REPO_ROOT/envs/mtg-py-env


# Running main.py as root (req by keyboard)
cd $REPO_ROOT/src
export ENV_PATH=$(readlink -f $(which python))
sudo $ENV_PATH main.py

# Profiling main.py
cd $REPO_ROOT/src
spy_py record -o profile.svg -- python main.py