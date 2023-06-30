from croniter import croniter
import time

cron_expression = "*/30 * * * *"
iter = croniter(cron_expression)


def run_import_pipeline():
    # Code to run the import pipeline goes here
    print("Running import pipeline...")
    # Replace the following line with the actual import pipeline code


# Define the cron expression for the desired interval
cron_expression = "*/30 * * * *"

# Main loop to execute the import pipeline at the scheduled intervals
while True:
    current_time = time.time()

    next_run_time = time.mktime(time.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                              '%Y-%m-%d %H:%M:%S'))
    if current_time < next_run_time:
        time.sleep(next_run_time - current_time)

    run_import_pipeline()
