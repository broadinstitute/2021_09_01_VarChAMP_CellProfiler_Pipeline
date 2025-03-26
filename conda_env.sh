# conda create -n cellprofiler python=3.8.10

conda activate cellprofiler

git clone https://github.com/broadinstitute/pe2loaddata.git
cd pe2loaddata/
pip install -e .