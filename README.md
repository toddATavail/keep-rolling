# Keep Rolling!

I'm dating myself, but I grew up playing games like Wizardry, Bard's Tale, and
Ultima. Though I now enjoy a much broader set of games, and certainly
appreciate the advances in graphics and sound, I still have a soft spot for the
old school RPGs. They have become harder to find, but I still seek out this
kind of game.

I recently recalled that it's possible to play a lot of iPad games on a Mac,
and iPad has quite a few Wizardry clones. Rolling up your party is a staple of
these games, and that usually involves a short, repetitive workflow of rolling
a stat pool until you have enough for some class assignment (like Samurai or
even Lord). Well, strangely enough, I now feel less charmed by repetitive
processes like this and more concerned about RSI!

But yesterday I remembered that I've been programming for nearly 30 years (!)
and that automation is easier than ever. So I decided to automate the tedious
part — rerolling the stat pool. It goes without saying that games like this
don't offer an API to control character creation, so that means getting
creative. I decided to use the accessibility features of macOS to automate the
process. Yep, screen scraping!

# Will it work for you?

The scope of applicability is rather limited, I'm afraid, but you're in luck if
you're in the sweet spot. Here's what you need:

1. A Mac running a "recent" version of macOS. Which one exactly? I'm not sure,
   but I'm on Sonoma 14.5.
2. A game that runs in a window on your Mac. I'm currently playing
   [Wandroid#1R](https://apps.apple.com/us/app/wandroid-1r/id1624246098) by
   Takashi Miura, but I suspect that it will work on other games in the series
   and potentially other similar games.
3. A game that permits rerolling the stat pool by pressing _only one key_. This
   is the key that the Python program will send to the game window. In the case
   of Wandroid#1R, it's the Escape (`esc`) key.
4. You may need to grant Accessibility permissions to the terminal from which
   you run the Python program. You can do this in
   `System Settings > Privacy & Security > Accessibility`. I needed to grant
   permissions to [WezTerm](https://wezfurlong.org/wezterm/index.html), the
   terminal I use, but you may need to grant permissions to
   [iTerm](https://iterm2.com/), Terminal, or whatever you use.
5. You may need to grant Screen & System Audio Recording permissions to the
   terminal from which you run the Python program. You can do this in
   `System Settings > Privacy & Security > Screen Recording`. I also needed to
   grant permissions to WezTerm.

It's also possible that you might find entirely different use cases for this
program. I'm not sure what they might be, but you lot are a creative bunch, so
I'm sure you'll think of something!

## Architecture

`Keep Rolling` comprises two components:

1. A Swift program that enables the user to draw a selection rectange on the
   screen and then reports the coordinates of that rectangle via standard
   output.
2. A Python 3 program that captures the content of that screen rectangle, OCRs
   the text, and sends keyboard input to the game window that owns the region
   in order to reroll the pool until it meets the user's specified threshold.

Python invokes the Swift program to get the screen coordinates, and then Python
does the rest.

## Setup

The Swift program doesn't have any special dependencies, but the
[`Makefile`](Makefile) assumes that you have the Xcode command line tools
installed. So do that if you haven't already.

The Python 3 program uses [`pillow`](https://pypi.org/project/pillow/) for
image processing, [`pytesseract`](https://pypi.org/project/pytesseract/) to OCR
the text and [`pyautogui`](https://pypi.org/project/PyAutoGUI/) to send
keyboard input to the game window, and
[`typing_extensions`](https://pypi.org/project/pillow/) for static typing, so
you'll want to install those:

```bash
pip install pillow pytesseract pyautogui typing_extensions
```

The Python program also assumes that you have
[Tesseract](https://github.com/tesseract-ocr/tesseract) installed. You can
install it via Homebrew:

```bash
brew install tesseract
```

## Building

To build the Swift program, run:

```bash
make
```

## Usage

You shouldn't need to run the Swift program directly, but you can if you think
of some crafty use for it. You can run it with:

```bash
./screen_selection
```

You can specify the `-v` or `--verbose` flag to get diagnostic output. It isn't
even able to print a usage message, but I double-dog promise that this is the
only flag it accepts.

The Python program is the one you'll want to run. Here's the synopsis:

```text
$ python3 keep_rolling.py -h
usage: keep_rolling.py [-h] -t THRESHOLD [-k KEYSTROKE] [-v]

Screen monitoring stat re-roller for Wizardry clones.

options:
  -h, --help            show this help message and exit
  -t THRESHOLD, --threshold THRESHOLD
                        Threshold value for OCR result
  -k KEYSTROKE, --keystroke KEYSTROKE
                        Keystroke to send (default: esc)
  -v, --verbose         Enable verbose output
```

The main thing you'll want to specify is the `-t` or `--threshold` flag, which
sets the threshold for the OCR result. So if you want to keep rolling until
your stat pool is $\ge 35$, use `-t 35`. You can also specify the `-k` or
`--keystroke` flag to set the keystroke to send to the game window. The default
is `esc`, which is the key used by the Wandroid series of games to reroll the
stat pool.

When you run the program, you'll be prompted to draw a selection rectangle on
the screen; the whole screen will darken slightly, and the selection rectangle
will be red. The program will then monitor that region for changes, OCR the
text, and send the keystroke to the game window every 0.5 seconds until the OCR
result meets the threshold. It will definitely tie up your mouse and keyboard,
because it works by bringing the game window to the front and sending
keystrokes to it. To stop the program, quickly yank the mouse to one of the
corners of the screen to engage `pyautogui`'s fail safe. (You can also press
`Ctrl+C` in the terminal, but you may have to race the program to do so.)

How do you know when it's done? Well, just look at the game window! The stat
pool will show a value over the threshold you specified (and it will stop
changing every half second). The terminal will also show the next prompt.

Enjoy your primo level 1 characters!
