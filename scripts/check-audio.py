import argparse
import os.path
import re

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"
space = r"\*+"
mvskoke_audio_pattern = r"\[(.*?)\]"

def read_script(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f.readlines():
            lines.append(line.strip())
    return lines

def get_audio_names(script):
    audio_names = []
    for line in script:
        matches = re.findall(mvskoke_audio_pattern, line)
        # print(matches)
        for m in matches:
            # remove spaces
            m = m.replace(" ", "-")
            audio_names.append(m)
    return audio_names

def check_audio(audio_names, asset_dir):
    extensions=[".wav",".WAV",".mp3"]
    audio_dict = {}
    count = 0
    missing = []
    for a in audio_names:
        found=False
        for ext in extensions:
            fname = asset_dir+"/"+a+ext
            if os.path.isfile(fname):
                audio_dict[a] = fname
                found=True
                count += 1
        if not found:
            missing.append(a)
    print("Audio check complete!")
    print(f'Found {count} audio files matching {len(audio_names)} phrases in {asset_dir}')
    print(f'missing {len(missing)} audio files: {missing}')
    return audio_dict

if __name__ == '__main__':
    # read input 
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_folder")
    parser.add_argument("script_file")
    args = parser.parse_args()

    script = read_script(args.script_file)
    audios = get_audio_names(script)
    audio_dict = check_audio(audios, args.asset_folder)
    print('Done.')