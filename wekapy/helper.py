from .WekaPyException import WekaPyException
import subprocess
import time
import os

def decode_data(data):
    return data.decode('utf-8').strip()

def run_process(options):
    start_time = time.time()
    process = subprocess.Popen(options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process_output, process_error = map(decode_data, process.communicate())
    if any(word.lower() in process_error for word in ["exception", "error"]):
        for line in process_error.split("\n"):
            if any(word.lower() in line for word in ["exception", "error"]):
                raise WekaPyException(line.split(' ', 1)[1])
    end_time = time.time()
    return process_output, end_time - start_time

def clear(session_id):
    os.remove(os.path.join(os.path.dirname(__file__), f"temp/{session_id}.arff"))
