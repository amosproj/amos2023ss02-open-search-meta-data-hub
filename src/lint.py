import sys

from pylint.lint import Run

THRESHOLD = 2
score = Run(["test.py"], exit=False).linter.stats.global_note

print(score)
if score < THRESHOLD:
    print("Linter failed: Score < threshold value")
    sys.exit(1)
sys.exit(0)