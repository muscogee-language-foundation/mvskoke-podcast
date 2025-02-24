import argparse
import os.path
import re
import random
import string
from google.cloud import texttospeech

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"
space = r"\*+"
mvskoke_audio_pattern = r"\[.*?\]"

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
            audio_names.append(m)
    return audio_names

def render_phrase(client, phrase):

    # format filename, remove punctuation
    out_filename=phrase[:25]
    out_filename = out_filename.translate(str.maketrans('', '', string.punctuation))  
    out_filename=out_filename.replace(" ","-")+str(random.randint(1,100))+".mp3"
    out_filename=out_filename.lower()
    
    synthesis_input = texttospeech.SynthesisInput(text=phrase)
    # standard voice
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Standard-G"
    )

    # # premium voice
    # voice = texttospeech.VoiceSelectionParams(
    #     language_code="en-US", name="en-US-Journey-D"
    # )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    # The response's audio_content is binary.
    with open(tts_dir+"/"+out_filename, "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
    print(f'Audio content written to file "{out_filename}"')
    return out_filename

def render_tts(script, overwrite):

    if overwrite:
        phrase_dict = {}
    else:
        phrase_dict = read_dict(tts_metadata)

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # speak all the phrases
    count = 0
    for line in script:
        line = line.strip()
        if not line:
            continue
        if re.match(space, line):
            continue
        elif re.search(mvskoke_audio_pattern, line):
            # has mvskoke audio
            for phrase in re.split(mvskoke_audio_pattern, line):
                if re.match(mvskoke_audio_pattern, phrase):
                    # skip mvskoke audio
                    continue
                phrase = phrase.strip()
                phrase = phrase.strip('.')
                phrase = phrase.strip(',')
                if phrase:
                    if phrase not in phrase_dict:
                        phrase_file = render_phrase(client, phrase)
                        phrase_dict[phrase] = phrase_file
                        count += 1
        elif line not in phrase_dict:
            phrase_file = render_phrase(client, line)
            phrase_dict[line] = phrase_file
            count += 1

    #save phrase dict to file
    write_dict(phrase_dict, tts_metadata)
    print(f'Generated {count} new audio files')
    print(f'Total audio files: {len(phrase_dict)}')
    print(f'Audio metadata saved to {tts_metadata}')

    return phrase_dict

def write_dict(data, filename):
    # make sure directory exists
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    # create list of strings
    list_of_strings = [ f'{key}\t{data[key]}' for key in data ]

    # write string one by one adding newline
    with open(filename, 'w') as outfile:
        [ outfile.write(f'{st}\n') for st in list_of_strings ]

def read_dict(filename) -> dict:
    dict = {}
    # read dictionary from file
    if os.path.isfile(filename):
        with open(filename, 'r') as infile:
            for line in infile.readlines():
                line=line.strip().split('\t')
                dict[line[0]] = line[1]
    return dict

if __name__ == '__main__':
    # read input 
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_folder")
    parser.add_argument("script_file")
    parser.add_argument("-o", "--overwrite", action='store_true', default=False)
    args = parser.parse_args()

    script = read_script(args.script_file)
    audios = get_audio_names(script)
    narrator_lines = render_tts(script, args.overwrite)
    print('Done.')