from threading import Thread
import threading
from appium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
#from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions import interaction
import time
from appium.webdriver.common.appiumby import By
from appium.webdriver.appium_service import AppiumService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
from appium.options.common import AppiumOptions
import multiprocessing
import logging

#this function for handle interacting with elements and handle their error
def interact_with_element(wait, by_type, identifier, action="click", keys=None, log_queue=None, udid=None):
    try:
        element = wait.until(EC.element_to_be_clickable((by_type, identifier)))
        if action == "click":
            element.click()
        elif action == "send_keys":
            element.clear()  # Clear the field before sending keys if needed
            element.send_keys(keys)
        log_queue.put(f"{udid}: {identifier} - successfully interacted.")
    except Exception as e:
        log_queue.put(f"{udid}: Failed to interact with {identifier} - {str(e)}")


# Function to read UDIDs from file
def read_udids_from_file(file_path):
    with open(file_path, 'r') as file:
        udids = file.readlines()
    return [udid.strip() for udid in udids]


#function to check adb connection 
def check_adb_connection(udid):
    adb_command = "adb devices"
    process = subprocess.Popen(adb_command.split(), stdout=subprocess.PIPE)
    output, _ = process.communicate()
    output_lines = output.decode().strip().split("\n")

    devices = [line.split()[0] for line in output_lines[1:] if line.strip()]

    if udid in devices:
        return True
    else:
        return False
    
# Logging thread function to handle log messages
def logging_thread(log_queue):
    logging.basicConfig(filename="automation_log.txt", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    running = True
    while running:
        while not log_queue.empty():
            log_entry = log_queue.get()
            if log_entry == "STOP_LOGGING":
                running = False
            else:
                logging.info(log_entry)  # Log to file
        time.sleep(0.1)  # Reduce CPU usage by sleeping a bit

def login_and_download(instance_port,  udid , log_queue):

    # Start logging thread /* for every process */
    logging_thread = threading.Thread(target=logging_thread, args=(log_queue,))
    logging_thread.start()

    try :
        ######################################## ADB Connection #################################################
        log_queue.put("starting ..............")
        adb_command = f"adb connect {udid}"
        process = subprocess.Popen(adb_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        process.wait()
        #check adb connection
        if not check_adb_connection(udid):
            log_queue.put(f"Failed to connect to adb instance {udid}")
            return
        log_queue.put(f"adb connected to {udid}")
        #########################################################################################################

        ########################################## Appium Connection ############################################
        appium_service = AppiumService()
        appium_service.start(args=['--address', '127.0.0.1', '--port', str(instance_port),'-pa' ,'/wd/hub'])
        desired_caps = {
            'platformName': 'Android',
            'automationName' : 'UiAutomator2',
            'udid':str(udid),
            #additional
            }
        option = AppiumOptions().load_capabilities(desired_caps)
        driver = webdriver.Remote(f'http://127.0.0.1:{instance_port}/wd/hub',  options=option)
        #########################################################################################################
        #                                           Auto Test                                                   #
        #########################################################################################################
        wait = WebDriverWait(driver, 60)# /* definition of element wait delay */

        interact_with_element(wait, By.XPATH, "//android.widget.TextView[@resource-id=\"com.spotify.music:id/bottom_navigation_item_title\" and @text=\"Search\"]", log_queue=log_queue, udid=udid)
        interact_with_element(wait, By.ID, "com.spotify.music:id/find_search_field_text", log_queue=log_queue, udid=udid)
        interact_with_element(wait, By.ID, "com.spotify.music:id/query", action="send_keys", keys="mozart", log_queue=log_queue, udid=udid)
        interact_with_element(wait, By.XPATH, "(//android.view.ViewGroup[@resource-id=\"com.spotify.music:id/row_root\"])[5]", log_queue=log_queue, udid=udid)
        interact_with_element(wait, By.ID, "com.spotify.music:id/button_play_and_pause", log_queue=log_queue, udid=udid)

        log_queue.put("testing is completed")
        time.sleep(1)
        #########################################################################################################

    except Exception as e:
        log_queue.put(f"Exception occurred in instance {udid}: {str(e)}")
    


if __name__ == "__main__":

    # Create a queue for logging
    log_queue = multiprocessing.Queue()
    
    udids_file = "devices.txt"  # Path to the file containing UDIDs
    udids = read_udids_from_file(udids_file)
    processes = []
    # Create and start multi process
    for i, udid in enumerate(udids):
        instance_port = 4723 + i   # every instance should connect to different appium server port
        
        process = multiprocessing.Process(target=login_and_download, args=(instance_port, udid, log_queue))
        processes.append(process)
        process.start()

    # Wait for all threads to complete
    for process in processes:
        process.join()

    log_queue.put("STOP_LOGGING")  # Signal to stop the logging thread
    logging_thread.join()  # Wait for the logging thread to terminate
    
    # Log final completion message with timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp} - Automation complete.")