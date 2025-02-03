import argparse
import re
import os
import pydub

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"
space = r"\*+"

def read_script(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f.readlines():
            lines.append(line.strip())
    return lines

def read_audio_info(filename):
    audio_dict = {}
    with open(filename, "r") as f:
        print('reading audio metadata '+filename)
        for line in f.readlines():
            line = line.strip().split("\t")
            audio_dict[line[0]] = line[1]
    return audio_dict

def get_mvskoke_audio(line, asset_dir):
    filename = line.strip("[]")
    # search asset_dir for filename ending in .mp3 or .wav
    if os.path.isfile(os.path.join(asset_dir, filename+".wav")):
        return os.path.join(asset_dir, filename+".wav")
    elif os.path.isfile(os.path.join(asset_dir, filename+".mp3")):
        return os.path.join(asset_dir, filename+".mp3")
    else:
        raise FileNotFoundError(1, "no audio file for \"" + filename +  "\" in directory "+asset_dir)

def get_en_audio(line, tts_dir, audio_dict):
    # if line is only periods
    if re.match(space, line):
        # silence
        return line
    return os.path.join(tts_dir, audio_dict[line])

def compile(script, asset_dir, tts_dir, audio_dict):
    
    audio_pattern = r"\[.*?\]"

    audio_list = []
    for line in script:
        # match brackets and text between brackets
        if re.match(audio_pattern, line):
            # mvskoke audio
            audio_list.append(get_mvskoke_audio(line, asset_dir))
        else:
            audio_list.append(get_en_audio(line, tts_dir, audio_dict))

    print(audio_list)

    print("Compilation complete.")
    return audio_list

def render(audio_list, output_file):
    # combine audio files
    combined = pydub.AudioSegment.silent(duration=0)
    mini_silence = pydub.AudioSegment.silent(duration=100)
    silence = pydub.AudioSegment.silent(duration=500)
    for a in audio_list:
        if re.match(space, a):
            for i in range(len(a)):
                combined += silence
        else:
            audio = pydub.AudioSegment.from_file(a)
            combined += audio
        combined += mini_silence
    combined.export(output_file, format="wav")

    print("Exported to "+output_file)
    return True

if __name__ == '__main__':
    # read input 
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_dir")
    parser.add_argument("script_file")
    parser.add_argument("tts_dir")
    parser.add_argument("output_file")
    parser.add_argument("-o", "--overwrite", action='store_true', default=False)
    args = parser.parse_args()

    script = read_script(args.script_file)
    audio_metadata = os.path.join(args.tts_dir, "metadata.tsv")
    tts_audios = read_audio_info(audio_metadata)
    audio_files = compile(script, args.asset_dir, args.tts_dir, tts_audios)
    render(audio_files, args.output_file)