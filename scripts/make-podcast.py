import argparse
import re
import os
import pydub

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"
space = r"\*+"
audio_pattern = r"\[.*?\]"

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

def get_mvskoke_audio(line, asset_dir) -> pydub.AudioSegment:
    filename = line.strip("[]")
    filename = filename.replace(" ", "-")
    sound = None
    # search asset_dir for filename ending in .mp3 or .wav
    if os.path.isfile(os.path.join(asset_dir, filename+".wav")):
        sound = pydub.AudioSegment.from_file(os.path.join(asset_dir, filename+".wav"))
    elif os.path.isfile(os.path.join(asset_dir, filename+".mp3")):
        sound = pydub.AudioSegment.from_file(os.path.join(asset_dir, filename+".mp3"))
    else:
        # print error
        print("no audio file for \"" + filename +  "\" in directory "+asset_dir)
        # return silence at approximate duration of the line
        length = max(int(len(line) / 10), 1) * 200
        sound = pydub.AudioSegment.silent(duration=length)
    return sound.pan(-1)
    
def get_en_audio(line, tts_dir, audio_dict):
    line = line.strip()
    # if line is only '*'
    sound = None
    if re.match(space, line):
        # silence
        return pydub.AudioSegment.silent(duration=500*len(line))
    sound = pydub.AudioSegment.from_file(os.path.join(tts_dir, audio_dict[line]))
    return sound.pan(1)

def split_audio(line):
    spans = []
    prev_end = 0
    for m in re.finditer(audio_pattern, line):
        if m.start() > prev_end:
            spans.append(line[prev_end:m.start()])
        spans.append(m.group())
        prev_end = m.end()
    if prev_end < len(line):
        spans.append(line[prev_end:])
    return spans
    

def compile(script, asset_dir, tts_dir, audio_dict):

    audio_list = []

    for line in script:
        line = line.strip()
        if not line:
            continue
        elif re.search(audio_pattern, line):
            # has mvskoke audio
            phrases = split_audio(line)
            for phrase in phrases:
                phrase = phrase.strip()
                phrase = phrase.strip('.')
                phrase = phrase.strip(',')
                if not phrase:
                    continue
                if re.match(audio_pattern, phrase):
                    audio_list.append(get_mvskoke_audio(phrase, asset_dir))
                else:
                    if phrase:
                        audio_list.append(get_en_audio(phrase, tts_dir, audio_dict))
        else:
            audio_list.append(get_en_audio(line, tts_dir, audio_dict))

    print("Compilation complete.")
    return audio_list

def render(audio_list, output_file):
    # combine audio files
    combined = pydub.AudioSegment.silent(duration=0)
    mini_silence = pydub.AudioSegment.silent(duration=100)
    for a in audio_list:
        combined += mini_silence
        combined += a
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