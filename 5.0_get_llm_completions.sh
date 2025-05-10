#!/bin/bash
#SBATCH --job-name=python_job      # Job name
#SBATCH --output=job_%j.out        # Standard output file
#SBATCH --error=job_%j.err         # Standard error file
#SBATCH --ntasks=1                 # Run a single task
#SBATCH --cpus-per-task=32          # Request 4 CPU cores
#SBATCH --mem=8G                   # Request 8GB RAM
#SBATCH --time=04:00:00            # Time limit (4 hours)
#SBATCH --mail-type=END,FAIL       # Mail events
#SBATCH --mail-user=jashkina@umich.edu
#SBATCH --account=eegg0            # Account
#SBATCH --partition=standard      # Partition

# Print job info
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURM_JOB_NODELIST"
echo "Date: $(date)"

# Set up Python virtual environment
cd $HOME
python3 -m venv venv
source venv/bin/activate

pip install -r $HOME/dvb_wrapper/dvb/requirements.txt

cd $HOME/dvb_wrapper/dvb

python $HOME/dvb_wrapper/dvb/5.0_get_llm_completions.py --full

# Deactivate venv
deactivate

echo "Job completed: $(date)"