# Generating python environment
cd $REPO_ROOT
conda env create -f environment.yaml --prefix ./envs/mtg-py-env

# Updating python environment
cd $REPO_ROOT
conda env update -f environment.yaml --prefix ./envs/mtg-py-env

# Running main.py as root (req by keyboard)
cd $REPO_ROOT/src
export ENVPATH=$(readlink -f $(which python))
sudo $ENVPATH main.py