#!/bin/sh
source ~/miniconda3/etc/profile.d/conda.sh
conda activate '/Users/juliamainzinger/miniconda3/envs/audio'

# First, check audio files and generate tts
python \
    ../scripts/provision-audio.py \
    ./assets script.txt

python \
    ../scripts/make-podcast.py \
    ./assets script.txt ./tts_output/metadata.tsv ep4.wav