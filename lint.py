import sys
import subprocess
from pylint import lint

# Perfect code: Some organizations strive for perfection and aim for a pylint score of 10. 
# Good code: Many organizations consider a pylint score between 8 and 9 as acceptable. 
# Acceptable code: For less critical projects or projects with specific constraints, a pylint score between 6 and 7 might be acceptable. 
# Minimum threshold: In some cases, a project may have a minimum threshold to ensure a basic level of code quality. This threshold could be set anywhere between 4 and 6.
 
THRESHOLD = 3
folder_path = "."

file_list = subprocess.check_output(["find", folder_path, "-type", "f", "-name", "*.py"]).decode().splitlines()

scores = []
for file_path in file_list:
    run = lint.Run(["--rcfile=.pylintrc", file_path], do_exit=False)
    score = run.linter.stats.global_note
    scores.append(score)

print("Scores:", scores)
print("Length:", len(scores))
average_score = sum(scores) / len(scores)

print("Average score:", average_score)
if average_score < THRESHOLD:
    print("Linter failed: Average score < threshold value="+str(THRESHOLD))
    sys.exit(1)
sys.exit(0)


#-------------------------------

# import os
# import sys
# from pylint import lint

# THRESHOLD = 5
# folder_path = "src/import-script/res"

# # Get a list of all Python files in the folder
# file_list = [os.path.join(folder_path, filename) for filename in os.listdir(folder_path) if filename.endswith(".py")]

# # Run pylint on each file
# lint_output = []
# for file_path in file_list:
#     run = lint.Run(["--rcfile=.pylintrc", file_path], do_exit=False)
#     score = run.linter.stats.global_note
#     lint_output.append(score)

# print(lint_output)
# # Calculate the average score
# scores = [float(output) for output in lint_output]

# print("Scores: ", scores)
# print("Length: ", len(scores))
# average_score = sum(scores) / len(scores)

# print("Average score: ", average_score)
# if average_score < THRESHOLD:
#     print("Linter failed: Average score < threshold value")
#     sys.exit(1)
# sys.exit(0)
