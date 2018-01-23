#!/usr/bin/env sh
#PBS -N script
#PBS -P ee
#PBS -l select=1:ngpus=1
#PBS -l walltime=06:00:00

units=70
layers=3

module load apps/tensorflow/1.1.0/gpu
cd ~/scratch/BridgeBidding/System
python main.py
#rm -r ~/scratch/BridgeBidding/EpisodeData/Train/$layers-$units
