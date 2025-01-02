import threading
import time

class EventWithClear:
    def __init__(self):
        self.condition = threading.Condition()
        self._is_set = False

    def set(self):
        with self.condition:
            self._is_set = True
            self.condition.notify_all()  # Notify threads waiting for the event to be set

    def clear(self):
        with self.condition:
            self._is_set = False
            self.condition.notify_all()  # Notify threads waiting for the event to be cleared

    def wait_for_set(self):
        with self.condition:
            while not self._is_set:
                self.condition.wait()  # Wait for the event to be set

    def wait_for_clear(self):
        with self.condition:
            while self._is_set:
                self.condition.wait()  # Wait for the event to be cleared

# Shared event object
event = EventWithClear()

def wait_for_set():
    while True:
        print("Wait-for-Set: Waiting for event to be set...")
        event.wait_for_set()
        print("Wait-for-Set: Event is set! Performing task.")
        time.sleep(1)  # Simulate task
        print("Wait-for-Set: Task complete.")

def wait_for_clear():
    while True:
        print("Wait-for-Clear: Waiting for event to be cleared...")
        event.wait_for_clear()
        print("Wait-for-Clear: Event is cleared! Performing task.")
        time.sleep(1)  # Simulate task
        print("Wait-for-Clear: Task complete.")

def controller():
    while True:
        print("Controller: Setting event.")
        event.set()
        time.sleep(3)  # Keep it set for a while
        print("Controller: Clearing event.")
        event.clear()
        time.sleep(3)  # Keep it cleared for a while

# Create threads
set_thread = threading.Thread(target=wait_for_set, daemon=True)
clear_thread = threading.Thread(target=wait_for_clear, daemon=True)
controller_thread = threading.Thread(target=controller, daemon=True)

# Start threads
set_thread.start()
clear_thread.start()
controller_thread.start()

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Program terminated.")
