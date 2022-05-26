# Taylor Swift line guessing game

This game asks the user to type the very next line of a Taylor Swift song. For example:

    What line follows: I have this dream you're doing cool shit
    >>> havin adventures on your own

Where `havin adventures on your own` is the user input. After the user types in their next line, they should see something like:

    What line follows: I have this dream you're doing cool shit
    >>> Having adventures on your own
    Your answer    : havin adventures on your own
    Correct answer : Having adventures on your own
    Good guess! You scored 14 points

And in this case the 'g' on the second line will be highlighted red to indicate that there is a difference between the user's guess and the correct answer. This should work similarly to how vsCode compares lines of code, but should not be case sensitive.

If the user types extra words (if the correct answer's line ends prematurely), the user should not be penalized and should still earn a full score. Case insensitive. Let `d` be the distance between the user's guess and the correct answer.

The user should be awarded a certain number of points based on how many characters the guess differs from the correct answer. The number of points is simply `(15 - d)`. If `d > 15`, the user should see:

    What line follows: I have this dream you're doing cool shit
    >>> been saying yes instead of no
    Your answer    : been saying yes instead of no
    Correct answer : Having adventures on your own
    No, that wasn't it! Good game, your score was xxxxxx.
    Here are the full lyrics to the song, with your line highlighted...

The user should be allowed to use a lifeline a predetermined number of times (maybe 4 times?) during the entire game. The lifeline narrows down the guess to a multiple choice question between 17 choices. A wrong answer ends the game, and a correct answer always scores only 1 point.

    What line follows: I have this dream you're doing cool shit
    >>> been saying yes instead of no
    Your answer    : .lifeline
    You used a lifeline, You have x lifelines remaining. Here are 17 choices:
        1) My barren land
        2) Most times, but this time it was true
        3) There goes the maddest woman this town has ever seen
        ...
        17)  Having adventures on your own
