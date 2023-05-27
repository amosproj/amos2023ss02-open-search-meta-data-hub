import os
import sys
from pylint import epylint as lint

THRESHOLD = 5
folder_path = "test"
folder_path = "src/import-script/res"

# Get a list of all Python files in the folder
file_list = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".py")]

# Run pylint on each file
lint_output = []
for file_path in file_list:
    (pylint_stdout, _) = lint.py_run(file_path, return_std=True)
    lint_output.append(pylint_stdout.getvalue())

print(lint_output)
# Calculate the average score
scores = [float(output.split(":")[1].strip()) for output in lint_output]
average_score = sum(scores) / len(scores)

print("Average score:", average_score)
if average_score < THRESHOLD:
    print("Linter failed: Average score < threshold value")
    sys.exit(1)
sys.exit(0)