import argparse
import re

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"

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

def compile(script, audio_dict, output_file):
    
    audio_pattern = r"\[(.*)\]"

    audio_list = []
    for line in script:
        if re.search(audio_pattern, line):
            for match in re.finditer(audio_pattern, line):
                audio_list.append(match.group(1))
                # TODO: add remainder of line to audio_list

    print(audio_list)

    print("Compilation complete.")
    return True

if __name__ == '__main__':
    # read input 
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_folder")
    parser.add_argument("script_file")
    parser.add_argument("audio_metadata")
    parser.add_argument("output_file")
    parser.add_argument("-o", "--overwrite", action='store_true', default=False)
    args = parser.parse_args()

    script = read_script(args.script_file)
    tts_audios = read_audio_info(args.audio_metadata)
    compile(script, tts_audios, args.output_file)