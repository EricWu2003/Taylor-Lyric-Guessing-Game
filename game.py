import os, json, random
from os.path import join
import sys

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
			if filtered_word.lower() in [w.lower() for w in wordlist]:
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

def print_help():
	print("""Here is a list of all the commands:

	s: Show the song from which the words were selected. This action is chosen by default if you enter a blank command.
	show: Show the entire lyrics of the song from which the words were selected.
	n: Progress to the next song.
	a: Reveal another word from the song.
	help: Show this list
	exit: quit the game.
""")


def find_tag_pattern_within_song (tag_pattern, song):
	# tag pattern is a list of tags (strings)
	# song is a list of tuples, each of which is a tagged word
	patterns = []
	for i in range(0, len(song) - len(tag_pattern)):
		is_match = True
		for j in range(len(tag_pattern)):
			if tag_pattern[j] != song[i+j][1]:
				is_match = False
		if is_match:
			patterns.append(song[i: i+len(tag_pattern)])

	return patterns









MAX_WORD_FREQ = 8 # the progam will choose to use words appearing in at most this many songs.
N_WORDS_START = 3 # the program will show these many words to start.
N_WORD_CANDIDATE = 12 # the size of the pool of words from which the program randomly selects words to show
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
else:
    print('running in a normal Python process')

comp_lyrics_dir = "lyrics-compiled"
lyrics_dir = "lyrics"

word_freq_dir = "main.py"
working_dir = os.path.dirname(__file__)
print(f"Working directory: {working_dir}")
print("---")

os.chdir(working_dir)
with open(join(comp_lyrics_dir, "word-frequencies.json")) as f:
	word_freq = json.loads(f.read())
with open(join(comp_lyrics_dir, "lyrics.json")) as f:
	song_word_list = json.loads(f.read())
with open(join(comp_lyrics_dir, "raw-lyric-dirs.json")) as f:
	song_dir_list = json.loads(f.read())

print_help()
action =  "n"
while True:
	if action == "exit":
		break
	elif action == "s" or action == "":
		print(f"The answer was: \033[1;34m{format_song_title(song_to_guess)}\033[1;00m")
	elif action == "show":
		show_song(song_to_guess, words_shown)
		print(f"The answer was: \033[1;34m{format_song_title(song_to_guess)}\033[1;00m")
	elif action == "n":
		song_to_guess = random.choice(list(song_dir_list.keys()))
		candidate_words = [i[0] for i in song_word_list[song_to_guess][:N_WORD_CANDIDATE]]
		words_shown = random.sample(candidate_words, N_WORDS_START)
		for word in words_shown:
			candidate_words.remove(word)
		print(f"Words in the song: \033[1;32m{'/'.join(words_shown)}\033[1;00m")
	elif action == "a":
		# add a new word and then display the word list
		if len(candidate_words) > 0:
			words_shown.append(random.choice(candidate_words))
			candidate_words.remove(words_shown[-1])
		else:
			print("Sorry, there are no more candidate words! ")
		print(f"Words in the song: \033[1;32m{'/'.join(words_shown)}\033[1;00m")
	elif action == "help":
		print_help()
	else:
		print("Sorry, that did not match any of my known commands")
	action = input("--->>> ")

print('Bye!')

