import multiprocessing
import subprocess
import time
import logging
from threading import Thread
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import By
from appium.webdriver.appium_service import AppiumService
from appium.options.common import AppiumOptions
import socket
#import auto testing steps from auto test file
from  auto_test import *

class IgnoreConnectionErrors(logging.Filter):
    def filter(self, record):
        if 'NewConnectionError' in record.getMessage() and 'Connection refused' in record.getMessage():
            return False
        return True


def find_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def interact_with_element(wait, by_type, identifier, action="click", keys=None, log_queue=None, udid=None):
    try:
        element = wait.until(EC.element_to_be_clickable((by_type, identifier)))
        if action == "click":
            element.click()
        elif action == "send_keys":
            element.clear()
            element.send_keys(keys)
        log_queue.put(f"{udid}: {identifier} - successfully interacted.")
    except Exception as e:
        log_queue.put(f"{udid}: Failed to interact with {identifier} - {str(e)}")

def logging_worker(log_queue, stop_event):
    while not stop_event.is_set() or not log_queue.empty():
        while not log_queue.empty():
            log_entry = log_queue.get()
            logging.info(log_entry)
        time.sleep(0.1)

def session_manager(instance_port, udid, barrier):
    log_queue = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    log_thread = Thread(target=logging_worker, args=(log_queue, stop_event))
    log_thread.start()

    try:
        if not check_adb_connection(udid):
            log_queue.put(f"Failed to connect to adb instance {udid}")
            return
        log_queue.put(f"adb connected to {udid}")

        appium_service = AppiumService()
        appium_service.start(args=['--address', '127.0.0.1', '--port', str(instance_port), '-pa', '/wd/hub'])

        desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'udid': str(udid),
            "appPackage": "com.spotify.music",
            "appActivity": "com.spotify.music.MainActivity",
            "noReset": True,  # Preserve app data & state
        }
        option = AppiumOptions().load_capabilities(desired_caps)
        driver = webdriver.Remote(f'http://127.0.0.1:{instance_port}/wd/hub', options=option)

        #wait for all instance to be ready at the same time : if there is a problem with appium server
        barrier.wait()

        #run auto testing
        Auto_test_steps()
        
        # Wait for all processes to reach this point
        barrier.wait()

        log_queue.put("testing is completed")

    except Exception as e:
        log_queue.put(f"Exception occurred in instance {udid}: {str(e)}")

    finally:
        stop_event.set()  # Signal the logging thread to stop
        log_thread.join()  # Wait for the logging thread to finish

def check_adb_connection(udid):
    adb_command = "adb devices"
    process = subprocess.Popen(adb_command.split(), stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output_lines = output.decode().strip().split("\n")
    devices = [line.split()[0] for line in output_lines[1:] if line.strip()]
    return udid in devices

def read_udids_from_file(file_path):
    with open(file_path, 'r') as file:
        udids = [line.strip() for line in file.readlines()]
    return udids

if __name__ == "__main__":
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.basicConfig(filename="automation_log.txt", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger()
    #filter loggin of appium server connection problem
    logger.addFilter(IgnoreConnectionErrors())

    start_time = time.time()  # Start timing here

    num_devices = len(read_udids_from_file('devices.txt'))  # Assume devices.txt has been populated correctly
    barrier = multiprocessing.Barrier(num_devices)  # Create a barrier for all processes

    udids = read_udids_from_file('devices.txt')
    processes = []
    for udid in udids:
        port = find_free_port()
        process = multiprocessing.Process(target=session_manager, args=(port, udid, barrier))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()  # Wait for all processes to finish

    end_time = time.time()  # End timing here
    total_duration = end_time - start_time  # Calculate total duration
    logging.info(f"Automation complete. Total execution time: {total_duration:.2f} seconds.")
