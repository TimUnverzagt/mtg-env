# Generating python environment
cd $REPO_ROOT
conda env create -f environment.yaml --prefix ./envs/mtg-py-env

# Updating python environment
conda env update -f environment.yaml --prefix ./envs/mtg-py-env