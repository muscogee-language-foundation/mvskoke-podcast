import argparse
import os.path

def clean_dir(tts_dir, audio_dict):
    files = list(audio_dict.values())
    files.append('metadata.tsv') # keep metadata file
    count = 0
    # remove files not in audio_dict
    for f in os.listdir(tts_dir):
        if f not in files:
            os.remove(os.path.join(tts_dir, f))
            count += 1

    print(f'Removed {count} files not in metadata')
    return audio_dict

def read_dict(filename) -> dict:
    dict = {}
    # read dictionary from file
    if os.path.isfile(filename):
        with open(filename, 'r') as infile:
            for line in infile.readlines():
                line=line.strip().split('\t')
                dict[line[0]] = line[1]
    else:
        raise FileNotFoundError(f'File not found: {filename}')
    if len(dict) == 0:
        raise ValueError(f'No lines found in {filename}')
    return dict

if __name__ == '__main__':
    # read input 
    parser = argparse.ArgumentParser()
    parser.add_argument("tts_dir")
    parser.add_argument("-o", "--overwrite", action='store_true', default=False)
    args = parser.parse_args()

    metadata = read_dict(os.path.join(args.tts_dir, "metadata.tsv"))
    print(metadata)
    clean_dir(args.tts_dir, metadata)
    print('Done.')