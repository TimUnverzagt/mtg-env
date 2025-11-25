# Generating python environment
cd $REPO_ROOT
conda env create -f environment.yaml --prefix ./envs/mtg-py-env

# Updating python environment
conda env update -f environment.yaml --prefix ./envs/mtg-py-env

# Running main.py as root (req by keyboard)
export ENVPATH=$(readlink -f $(which python))
sudo $ENVPATH main.py