# Taylor-Lyric-Guessing-Game

This is a command-line game about guessing the Taylor Swift song
based on a few words from the lyrics.

## build instructions

A Unix executable can be built using the python module pyinstaller. Pyinstaller can be installed by running
`pip3 install pyinstaller`
And after the spec file is in place you can run `pyinstaller game.spec` to create an executable file in the `dist` directory. The spec file contains instructions to bundle json files in `lyrics` and `lyrics-compiled` directories in the executable.

Note: it seems like executables built on an M1 mac will not run on older machines, but executables built on intel macs will run on an M1 mac.
