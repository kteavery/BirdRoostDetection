#!/usr/bin/bash

#SBATCH --job-name=train_cnn
#SBATCH --ntasks=1
#SBATCH -o log.out
#SBATCH -e log.err
#SBATCH --mail-user=carmenchilson@ou.edu
#SBATCH --mail-type=ALL
#SBATCH -p swat_plus
#SBATCH -t 47:00:00
#SBATCH -D /home/cchilson/schoonerJobs/train
#SBATCH --array=0-3

# cd to directory where job was submitted from
cd $SLURM_SUBMIT_DIR

RADARS_PRODUCTS=(0 1 2 3)
# get the day information from the array
RADARS_PRODUCT=${RADARS_PRODUCTS[$SLURM_ARRAY_TASK_ID]}

echo $SLURM_ARRAY_TASK_ID

python /home/cchilson/gitRepositories/BirdRoostDetection/BirdRoostDetection/\
BuildModels/ShallowCNN/train.py \
--radar_product=$RADARS_PRODUCT \
--log_path=model/Reflectivity/ \
--eval_increment=5 \
--num_iterations=10000 \
--checkpoint_frequency=100 \
--learning_rate=.0001












