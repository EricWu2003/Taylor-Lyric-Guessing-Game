from math import trunc
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

def lev_dist_case_i(str1, str2):
    s1 = str1.lower()
    s2 = str2.lower()
    return levenshtein_distance(s1, s2)

def optimalTruncatedDist(l1, l2):
    # first we will see how many characters we can truncate from the end of the guess to minimize lev_dist_case_i(userGuess, answer)

    # A positive optimalK means that we truncate the user's guess (l1) to get the minimal distance
    # A negative optimalK means that we truncate the answer (l2) to get the minimal distance
    optimalK = 0
    minimalDist = lev_dist_case_i(l1, l2)
    k = 1
    while len(l1) - k >= 0:
        d = lev_dist_case_i(l1[:-k], l2)
        if d < minimalDist:
            optimalK = k
            minimalDist = d
        k += 1
    k = 1
    while len(l2) - k >= 0:
        d = lev_dist_case_i(l1, l2[:-k])
        if d < minimalDist:
            optimalK = -k
            minimalDist = d
        k += 1
    
    return optimalK, minimalDist


differ = difflib.Differ()
def compare(userGuess, answer):
    # returns a dist of -k if the program should prompt the user for more words
    # where k represents how many more characters the user might want to input

    truncateAmount, minimalDist = optimalTruncatedDist(userGuess.lower(), answer.lower())
    
    truncatedUserGuess, choppedOffPartOfGuess = userGuess, ""
    truncatedAnswer, choppedOffPartOfAnswer = answer, ""
    if truncateAmount > 0:
        truncatedUserGuess = userGuess[:-truncateAmount]
        choppedOffPartOfGuess = userGuess[-truncateAmount:]
    elif truncateAmount < 0:
        return truncateAmount

    diffs = list(differ.compare(truncatedUserGuess.lower(), truncatedAnswer.lower()))
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
    print(f"\033[1;33m{choppedOffPartOfGuess}\033[1;00m")

    print("Correct answer: ", end = "")
    printWithFlags(truncatedAnswer, answerFlags)
    print(f"\033[1;33m{choppedOffPartOfAnswer}\033[1;00m")


    return minimalDist



randomSong = random.choice(list(raw_lyrics.keys()))
randomLine = random.choice(raw_lyrics[randomSong][:-1])
print(f"What line follows: {randomLine}")
answer = raw_lyrics[randomSong][raw_lyrics[randomSong].index(randomLine) + 1]
guess = input(">>> ")
dist = compare(guess, answer)
while dist < 0:
    print(f"Try guessing again: your guess was shorter than the programmed answer")
    guess = input(">>> ")
    dist = compare(guess, answer)
print(f"The dist was {dist}")

print('done')

