import os, json, random
from os.path import join
from os import path

import sys
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
else:
    print('running in a normal Python process')

comp_lyrics_dir = "lyrics-compiled"
lyrics_dir = "lyrics"

word_freq_dir = "main.py"
working_dir = path.dirname(__file__)
print(f"Working directory: {working_dir}")

MAX_WORD_FREQ = 8 # the progam will choose to use words appearing in at most this many songs.
N_WORDS_START = 3 # the program will show these many words to start.
N_WORD_CANDIDATE = 12 # the size of the pool of words from which the program randomly selects words to show

def format_song_title(song):
	album, _, name = song.partition("--")
	album = " ".join([word.capitalize() for word in album.split("-")])
	if name.endswith("-tv"):
		name = name[:-3]
	if name.endswith("-tv-ftv"):
		name = name[:-6]
	name = " ".join([word.capitalize() for word in name.split("-")])
	return f"{album} : {name}"

def show_song(song, wordlist, showOnlyColoredLines = False):
	with open(song_dir_list[song]) as f:
		full_lyrics = f.read()
	lyrics_with_color = ""
	for line in full_lyrics.split("\n"):
		line = line.strip()
		if line == "":
			lyrics_with_color += '\n'
			continue
		if line.startswith("["):
			lyrics_with_color += f"\033[35m{line}\033[0m" + '\n'
			continue
		words = line.split()
		in_color = [False for _ in words]
		for index, word in enumerate(words):
			filtered_word = ""
			for char in word:
				if char in {'"', "'", "(", ")", ",", ".", "?", "!"}:
					continue
				filtered_word += char
			if filtered_word.lower() in wordlist:
				in_color[index] = True

		line = ""
		for word, is_in_color in zip(words, in_color):
			if not is_in_color:
				line += f"{word} "
			else:
				line += f"\033[1;32m{word}\033[1;00m "
		if showOnlyColoredLines:
			if any(in_color):
				lyrics_with_color += line + '\n'
		else:
			lyrics_with_color += line + '\n'
	print(lyrics_with_color)


os.chdir(working_dir)
with open(join(comp_lyrics_dir, "word-frequencies.json")) as f:
	word_freq = json.loads(f.read())
with open(join(comp_lyrics_dir, "lyrics.json")) as f:
	song_word_list = json.loads(f.read())
	song_word_list = {k: sorted(v, key = lambda v: word_freq[v[0].lower()]) for k,v in song_word_list.items()}
with open(join(comp_lyrics_dir, "raw-lyric-dirs.json")) as f:
	song_dir_list = json.loads(f.read())


action =  "n"
while True:
	if action == "exit":
		break
	elif action == "s" or action == "":
		print(f"The answer was: \033[1;34m{format_song_title(song_to_guess)}\033[1;00m")
	elif action == "show":
		show_song(song_to_guess, words_shown)
		print(f"The answer was: \033[1;34m{format_song_title(song_to_guess)}\033[1;00m")
	elif action == "show -l":
		show_song(song_to_guess, words_shown, True)
		print(f"The answer was: \033[1;34m{format_song_title(song_to_guess)}\033[1;00m")
	elif action == "n":
		print("---")
		song_to_guess = random.choice(list(song_dir_list.keys()))
		# candidate_words = [word.lower() for word in song_word_list[song_to_guess] if word_freq[word.lower()] <= MAX_WORD_FREQ]
		candidate_words = [i[0] for i in song_word_list[song_to_guess][:N_WORD_CANDIDATE]]
		words_shown = random.sample(candidate_words, N_WORDS_START)
		for word in words_shown:
			candidate_words.remove(word)
		print(f"Words in the song: \033[1;32m{'/'.join(words_shown)}\033[1;00m")
	elif action == "a" or action == "add":
		# add a new word and then display the word list
		if len(candidate_words) > 0:
			words_shown.append(random.choice(candidate_words))
			candidate_words.remove(words_shown[-1])
		else:
			print("Sorry, there are no more candidate words! ")
		print(f"Words in the song: \033[1;32m{'/'.join(words_shown)}\033[1;00m")
	action = input("[s (default), show, n, exit, add] ")

print('Bye!')

