import argparse
import os.path
import re
import random
import string
from google.cloud import texttospeech

tts_dir="tts_output"
tts_metadata="tts_output/metadata.tsv"

def read_script(filename):
    lines = []
    with open(filename, "r") as f:
        for line in f.readlines():
            lines.append(line.strip())
    return lines

def get_audio_names(script):
    audio_pattern = r"\[(.*)\]"
    audio_names = []
    for line in script:
        matches = re.findall(audio_pattern, line)
        # print(matches)
        for m in matches:
            audio_names.append(m)
    return audio_names

def check_audio(audio_names, asset_dir):
    extensions=[".wav",".WAV",".mp3"]
    audio_dict = {}
    count = 0
    for a in audio_names:
        found=False
        for ext in extensions:
            fname = asset_dir+"/"+a+ext
            if os.path.isfile(fname):
                audio_dict[a] = fname
                found=True
                count += 1
        if not found:
            raise FileNotFoundError(1, "no audio file for \"" + a +  "\" in directory "+asset_dir)
    print("Audio check complete!")
    print(f'Found {count} audio files matching {len(audio_names)} phrases')
    return audio_dict

def render_phrase(client, phrase):

    # format filename, remove punctuation
    out_filename=phrase[:25]
    out_filename = out_filename.translate(str.maketrans('', '', string.punctuation))  
    out_filename=out_filename.replace(" ","-")+str(random.randint(1,100))+".mp3"
    out_filename=out_filename.lower()
    
    synthesis_input = texttospeech.SynthesisInput(text=phrase)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )
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
    audio_pattern = r"\[.*\]"
    if overwrite:
        phrase_dict = {}
    else:
        phrase_dict = read_dict(tts_metadata)

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # speak all the phrases
    count = 0
    for line in script:
        phrases = re.split(audio_pattern, line)
        # print(phrases)
        for p in phrases:
            p = p.strip()
            if p and p!="..." and p not in phrase_dict:
                phrase_file = render_phrase(client, p)
                phrase_dict[p] = phrase_file
                count += 1

    #save phrase dict to file
    write_dict(phrase_dict, tts_metadata)
    print(f'Generated {count} new audio files')
    print(f'Total audio files: {len(phrase_dict)}')
    print(f'Audio metadata saved to {tts_metadata}')

    return phrase_dict

def write_dict(data, filename):
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
    audio_dict = check_audio(audios, args.asset_folder)
    narrator_lines = render_tts(script, args.overwrite)
    print('Done.')