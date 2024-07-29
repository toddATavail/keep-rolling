#!/usr/bin/env python

"""
Screen monitoring re-roller for Wizardry clones.
"""

from argparse import ArgumentParser, Namespace
from subprocess import CompletedProcess
import subprocess
import time

import pyautogui
import pytesseract
from typing_extensions import Any, List, Optional
from PIL import Image, ImageEnhance, UnidentifiedImageError

verbose: bool = False

def verbose_print(*print_args: Any, **kwargs: Any) -> None:
	"""
	Print the given arguments if the `verbose` flag is set.
	"""
	if verbose:
		print(*print_args, **kwargs)

def run_swift_script() -> tuple[int, int, int, int]:
	"""
	Run the Swift utility `screen_selection` to select a screen region and
	return the coordinates.
	"""
	result: CompletedProcess = subprocess.run(
		['./screen_selection'],
		check=True,
		capture_output=True,
		text=True
	)
	output_lines: List[str] = result.stdout.strip().split('\n')

	# Find the last non-empty line starting with "Selection:".
	selection_line: Optional[str] = None
	for line in reversed(output_lines):
		if line.strip().startswith("Selection:"):
			selection_line = line.strip()
			break

	if selection_line is None:
		raise ValueError("No selection data found in the output")

	# Parse the selection line: "Selection: x1, y1, width, height"
	coords_str: str = selection_line.split("Selection:")[1].strip()
	coords: List[int] = list(map(int, coords_str.split(', ')))

	if len(coords) != 4:
		raise ValueError(f"Unexpected number of coordinates: {coords}")

	return (coords[0], coords[1], coords[2], coords[3])

def capture_screen_region(
	x: int,
	y: int,
	width: int,
	height: int
) -> Image.Image:
	"""
	Capture a screenshot of the specified region on the screen.
	"""
	screenshot: Image.Image = pyautogui.screenshot(region=(x, y, width, height))
	return screenshot

def activate_window_at_position(x: int, y: int) -> None:
	"""
	Activate the window at the specified position on the screen.
	"""
	# Adding a small offset to ensure we're inside the region.
	pyautogui.moveTo(x + 2, y + 2)
	# Click to focus the window.
	pyautogui.click()
	# Short pause to allow focus to change.
	time.sleep(0.1)

def perform_ocr(image: Image.Image) -> Optional[int]:
	"""
	Perform OCR on the given image and return the extracted text as an integer.
	"""
	# Increase the image size to improve OCR accuracy.
	width, height = image.size
	# pylint: disable=no-member
	image = image.resize((width*2, height*2), Image.LANCZOS)

	# Convert image to black and white.
	image = image.convert('L')

	# Increase the contrast.
	enhancer: ImageEnhance.Contrast = ImageEnhance.Contrast(image)
	image = enhancer.enhance(2)

	# Perform OCR with specific configuration. Allow ) to be recognized as 9.
	custom_config: str = r'--psm 6 -c tessedit_char_whitelist=0123456789)'
	text: str = pytesseract.image_to_string(image, config=custom_config).strip()

	# Replace any ')' with '9'.
	text = text.replace(')', '9')

	try:
		return int(text)
	except ValueError:
		print(f"OCR failed to convert text to integer: {text}")
		return None

def send_keystroke(keystroke: str) -> None:
	"""
	Send the specified key press to the active window.
	"""
	pyautogui.press(keystroke)

def build_parser() -> ArgumentParser:
	"""
	Build the argument parser for the script.
	"""
	parser: ArgumentParser = ArgumentParser(
		description="Screen monitoring stat re-roller for Wizardry clones."
	)
	parser.add_argument(
		"-t",
		"--threshold",
		type=int,
		required=True,
		help="Threshold value for OCR result"
	)
	parser.add_argument(
		"-k",
		"--keystroke",
		default="esc",
		help="Keystroke to send (default: esc)"
	)
	parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help="Enable verbose output"
	)
	return parser

def main(threshold: int, keystroke: str) -> None:
	"""
	Main function to run the script.
	"""
	print("Please select the screen region...")
	try:
		x, y, width, height = run_swift_script()
		verbose_print(
			f"Selected region: x={x}, y={y}, width={width}, height={height}"
		)
	# pylint: disable=broad-exception-caught
	except Exception as e:
		print(f"Error running screen selection: {e}")
		return

	print(
		"(Move the mouse to the screen corner to stop the script prematurely.)"
	)

	try:
		while True:
			screenshot: Image.Image = capture_screen_region(x, y, width, height)
			ocr_result: Optional[int] = perform_ocr(screenshot)

			if ocr_result is not None:
				verbose_print(f"OCR Result: {ocr_result}")

				if ocr_result >= threshold:
					verbose_print(f"Stopping at {ocr_result}...")
					break

				activate_window_at_position(x, y)
				send_keystroke(keystroke)
				verbose_print(f"Sent escape keystroke to window at {x}, {y}")

			# Wait a bit before next iteration.
			time.sleep(0.5)
	except pyautogui.FailSafeException:
		print("Aborted by mouse movement.")
		return
	except UnidentifiedImageError:
		print("Error capturing screen region.")
		return
	# pylint: disable=broad-exception-caught
	except Exception as e:
		print(f"Unexpected error: {e}")
		return



# Run the script if executed directly.
if __name__ == "__main__":
	args: Namespace = build_parser().parse_args()

	verbose: bool = args.verbose

	main(args.threshold, args.keystroke)
