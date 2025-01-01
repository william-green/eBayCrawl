import threading
import time
import queue
from datetime import datetime, timedelta

# Task function that each thread will execute
def process_task(task_id, scheduled_time):
    print(f"Processing task {task_id} scheduled at {scheduled_time}...")
    time.sleep(1)  # Simulating work being done
    print(f"{task_id} completed.")

# Worker thread function that processes tasks from the queue
def worker(task_queue):
    while True:
        # Get the task with the earliest timestamp (priority)
        scheduled_time, task_id = task_queue.get()
        
        if task_id is None:
            print("Received None, breaking loop.")
            break

        # If task's scheduled time is in the future, wait until that time
        current_time = datetime.now()
        if scheduled_time > current_time:
            wait_time = (scheduled_time - current_time).total_seconds()
            print(f"Waiting {wait_time:.2f} seconds for task {task_id} to execute...")
            time.sleep(wait_time)
        
        # Process the task
        process_task(task_id, scheduled_time)
        task_queue.task_done()

# Create a priority queue to hold tasks, with each task consisting of (scheduled_time, task_id)
task_queue = queue.PriorityQueue()

# Number of worker threads
num_worker_threads = 2

# Create worker threads
threads = []
for _ in range(num_worker_threads):
    thread = threading.Thread(target=worker, args=(task_queue,))
    thread.start()
    threads.append(thread)

# Add tasks to the queue with timestamps (scheduled_time, task_id)
tasks = [
    (datetime.now() + timedelta(seconds=5), "Task 1"),  # 5 seconds from now
    (datetime.now() + timedelta(seconds=3), "Task 2"),  # 3 seconds from now
    (datetime.now() + timedelta(seconds=10), "Task 3"), # 10 seconds from now
]

for task in tasks:
    task_queue.put(task)

# Wait for all tasks to be processed
task_queue.join()

# Stop the worker threads by adding None for each worker
for _ in range(num_worker_threads):
    task_queue.put((datetime.now(), None))  # Use the current time to break the worker loop

# Wait for all threads to finish
for thread in threads:
    thread.join()

print("All tasks completed.")
