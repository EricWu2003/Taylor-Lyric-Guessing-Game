from math import trunc
import os
from os.path import join
import json
from re import A
import sys
import random
from Levenshtein import distance as levenshtein_distance
import difflib


if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    print('running in a PyInstaller bundle')
else:
    print('running in a normal Python process')

def printIntroduction():
    print("""\033[1;34mWelcome to a Taylor Swift lyric guessing game!\033[1;00m
    
In this game, you will be shown a line from a Taylor Swift song. You will then be prompted to enter the following line. If your guess is close enough to the correct answer, you will score a certain number of points (and you earn a bonus if your guess is a perfect match).

If you do not know what the next line is, simply enter a question mark ('?') and you will be given 17 choices for the next line. Upon seeing the choices, enter a number 1-17, and you will score only 1 point for the correct answer.

After each round, press the enter key to continue, or enter '?' to view the full lyrics of the song.

The game ends as soon as you submit an incorrect answer.

Good luck! And have fun!""")
    input("Press enter to begin.")

MAX_ACCEPTABLE_DIST = 13
POINTS_FOR_PERFECT_MATCH = 26

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

def areCloseEnough(s1, s2):
    return levenshtein_distance(s1, s2) / min(len(s1), len(s2)) < 0.1

def isAcceptableGuess(guess, lines):
    if guess not in lines[:-1]:
        return False
    possibleContinuations = []
    for index, line in enumerate(lines[:-1]):
        if areCloseEnough(line, guess):
            possibleContinuations.append(lines[index+1])
    for c1 in possibleContinuations:
        for c2 in possibleContinuations:
            if not areCloseEnough(c1, c2):
                return False
    return True
def pickAcceptableGuess():
    randomSong = random.choice(list(raw_lyrics.keys()))
    randomLine = random.choice(raw_lyrics[randomSong][:-1])
    while not isAcceptableGuess(randomLine, raw_lyrics[randomSong]):
        randomLine = random.choice(raw_lyrics[randomSong][:-1])
    answer = raw_lyrics[randomSong][raw_lyrics[randomSong].index(randomLine) + 1]
    return randomSong, randomLine, answer

def pickDistractors(correctAnswer):
    NUM_DISTRACTORS = 16
    distractors = []
    for _ in range(NUM_DISTRACTORS):
        randomSong = random.choice(list(raw_lyrics.keys()))
        randomLine = random.choice(raw_lyrics[randomSong][:-1])
        while areCloseEnough(randomLine, correctAnswer):
            randomLine = random.choice(raw_lyrics[randomSong][:-1])
        distractors.append(randomLine)

    return distractors

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
    
    print("   \033[1;34mYour answer:\033[1;00m ", end = "")
    printWithFlags(truncatedUserGuess, userGuessFlags)
    print(f"\033[1;33m{choppedOffPartOfGuess}\033[1;00m")

    print("\033[1;34mCorrect answer:\033[1;00m ", end = "")
    printWithFlags(truncatedAnswer, answerFlags)
    print(f"\033[1;33m{choppedOffPartOfAnswer}\033[1;00m")


    return minimalDist

def takeUserMultipleChoiceGuess(answer, choices):
    
    for i, choice in enumerate(choices):
        print(f"\033[1;34m{i+1})\033[1;00m {choice}")
    acceptableInputs = [str(i+1) for i in range(len(choices))]
    guess = ""
    while True:
        guess = input(">>> ")
        if guess in acceptableInputs:
            break
        print("That's not a valid choice.")
    return choices[int(guess)-1] == answer

def printSong(song, lineToHighlight):
    album, _, name = song.partition("--")
    album = " ".join([word.capitalize() for word in album.split("-")])
    if name.endswith("-tv"):
        name = name[:-3]
    if name.endswith("-tv-ftv"):
        name = name[:-6]
    name = " ".join([word.capitalize() for word in name.split("-")])
    print(f"\033[1;32m{album} : {name}\033[1;00m")

    with open(join(comp_lyrics_dir, "raw-lyric-dirs.json")) as f1:
        d = json.loads(f1.read())
        with open(d[song]) as f2:
            for line in f2.readlines():
                l = line.rstrip("\n")
                if l == lineToHighlight:
                    print(f"\033[1;32m{l}\033[1;00m")
                else:
                    print(l)

printIntroduction()
score = 0
while True:
    randomSong, randomLine, answer = pickAcceptableGuess()
    print(f"Your current score is {score}. What line follows: \033[1;34m{randomLine}\033[1;00m")
    while True:
        guess = input(">>> ")
        dist = 0
        if guess == "?":
            distractors = pickDistractors(answer)
            distractors.append(answer)
            random.shuffle(distractors)
            print("Reducing to a multiple choice challenge:")
            res = takeUserMultipleChoiceGuess(answer, distractors)
            if res:
                dist = MAX_ACCEPTABLE_DIST
            else: 
                dist = MAX_ACCEPTABLE_DIST+1
        else:
            dist = compare(guess, answer)
        if guess != '?' and len(guess) + 5 < len(answer):
            print(f"Try guessing again: your guess was shorter than the programmed answer")
        else:
            break
    if dist > MAX_ACCEPTABLE_DIST:
        print(f"That wasn't it! The game ends, and your final score is {score}. Good game!")
        response = input(f"Press enter to quit ('?' to show song):")
        if response == "?":
            printSong(randomSong, randomLine)
            input("Press enter to quit:")
        sys.exit()
    if dist != 0:
        print(f"Correct! You scored {MAX_ACCEPTABLE_DIST - dist + 1} points for your answer.")
        score += MAX_ACCEPTABLE_DIST - dist + 1
    else:
        print(f"Yes! You scored {POINTS_FOR_PERFECT_MATCH} points for your \033[1;32mperfect match\033[1;00m!")
        score += POINTS_FOR_PERFECT_MATCH
    response = input(f"Press enter to continue ('?' to show song):")
    if response == '?':
        printSong(randomSong, randomLine)
        input("Press enter to continue:")

