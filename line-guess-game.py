import os
from os.path import join
import json
import sys
import random
from Levenshtein import distance as levenshtein_distance
import difflib


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
else:
    print('running in a normal Python process')

def lev_dist_case_i(str1, str2):
    s1 = str1.lower()
    s2 = str2.lower()
    return levenshtein_distance(s1, s2)

working_dir = os.path.dirname(__file__)
os.chdir(working_dir)
comp_lyrics_dir = "lyrics-compiled"

raw_lyrics = {}
with open(join(comp_lyrics_dir, "raw-lyric-dirs.json")) as f:
    d = json.loads(f.read())
    for k, v in d.items():
        with open(v) as f2:
            lines = f2.readlines()

            raw_lyrics[k] = [line.rstrip('\n') for line in lines if (not line.startswith('[') and line != '\n')]

differ = difflib.Differ()
def compare(userGuess, answer):

    # first we will see how many characters we can truncate from the end of the guess to minimize lev_dist_case_i(userGuess, answer)
    optimalLength = len(userGuess)
    minimalDist = lev_dist_case_i(userGuess, answer)
    k = 1
    while len(userGuess) - k >= 0:
        d = lev_dist_case_i(userGuess[:-k], answer)
        if d < minimalDist:
            optimalLength = len(userGuess) - k
            minimalDist = d
        k += 1
    truncatedUserGuess = userGuess[:optimalLength]
    choppedOffPartofGuess = userGuess[optimalLength:]

    diffs = list(differ.compare(truncatedUserGuess.lower(), answer.lower()))
    userGuessFlags = []
    answerFlags = []
    for line in diffs:
        if line.startswith("? "):
            continue
        elif line.startswith("+ "):
            answerFlags.append(True)
        elif line.startswith("- "):
            userGuessFlags.append(True)
        elif line.startswith("  "):
            answerFlags.append(False)
            userGuessFlags.append(False)
        else:
            assert(False)
    

    def printWithFlags(str, flagList):
        assert(len(str) == len(flagList))
        for char, flag in zip(str, flagList):
            if not flag:
                print(char, end = "")
            else:
                print(f"\033[1;31m{char}\033[1;00m", end= "")
    
    print("   Your answer: ", end = "")
    printWithFlags(truncatedUserGuess, userGuessFlags)
    print(f"\033[1;33m{choppedOffPartofGuess}\033[1;00m")

    print("Correct answer: ", end = "")
    printWithFlags(answer, answerFlags)
    print("")
    

    return minimalDist



randomSong = random.choice(list(raw_lyrics.keys()))
randomLine = random.choice(raw_lyrics[randomSong][:-1])
print(f"What line follows: {randomLine}")
answer = raw_lyrics[randomSong][raw_lyrics[randomSong].index(randomLine) + 1]
guess = input(">>> ")
dist = compare(guess, answer)
print(f"Dist: {dist}")

print('done')

