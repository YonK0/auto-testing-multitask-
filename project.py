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
    while True:
        while not log_queue.empty():
            log_entry = log_queue.get()
            # Add timestamp to log entry
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"{timestamp} - {log_entry}"
            # Log the message to console or file
            logging.info(log_message)  # root logger

        time.sleep(0.1)  # 0.1 second


def login_and_download(instance_port,  udid ):
    try : 
        # ADB Connection ########################################################################################
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

        # Appium Connection #####################################################################################
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
        
        time.sleep(1.5)
        el1 = wait.until(EC.element_to_be_clickable((By.XPATH,"//androidx.viewpager.widget.b[@resource-id=\"com.uncube.launcher3:id/desktop\"]/android.view.ViewGroup/android.view.View[3]")))
        el1.click()
        log_queue.put(f"{udid}: button one clicked ")
        el2 = wait.until(EC.element_to_be_clickable((By.ID, "tn.mobipost:id/btn_welcome_with_card")))
        el2.click()
        el3 = wait.until(EC.element_to_be_clickable((By.ID,"tn.mobipost:id/et_register_cin")))
        el3.clear()
        el3.send_keys("99999999")
        el5 = wait.until(EC.element_to_be_clickable((By.ID,"tn.mobipost:id/et_register_cart_code")))
        el5.clear()
        el5.send_keys(1234)
        # el6 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/button1")))
        # el6.click()
        # el7 = wait.until(EC.element_to_be_clickable((By.XPATH,'(//android.widget.CheckBox[@resource-id="android:id/checkbox"])[3]')))
        # el7.click()
        # el8 = wait.until(EC.element_to_be_clickable((By.XPATH,"/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout[8]/android.widget.RelativeLayout/android.widget.TextView")))
        # el8.click()
        # #el9 = wait.until(EC.element_to_be_clickable((By.XPATH,"/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout[5]/android.widget.RelativeLayout")))
        # #el9.click()
        # el10 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/edit")))
        # log_queue.put(username)
        # el10.clear()
        # el10.send_keys(username)
        # el11 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/button1")))
        # el11.click()
        # el12 = wait.until(EC.element_to_be_clickable((By.XPATH,"/hierarchy/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.ListView/android.widget.LinearLayout[9]/android.widget.RelativeLayout")))
        # el12.click()
        # el13 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/edit")))
        # el13.clear()
        # el13.send_keys(password)
        # el14 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/button1")))
        # el14.click()
        # el14 = wait.until(EC.element_to_be_clickable((By.ID,"net.typeblog.socks:id/switch_action_button")))
        # el14.click()
        # try :
        #     el14 = wait.until(EC.element_to_be_clickable((By.ID,"android:id/button1")))
        #     el14.click()
        # except : 
        #     log_queue.put("")
        log_queue.put("testing is completed")
        time.sleep(2)
        #########################################################################################################

    except Exception as e:
        log_queue.put(f"Exception occurred in instance {udid}: {str(e)}")
    


if __name__ == "__main__":

    # Create a queue for logging
    log_queue = multiprocessing.Queue()
    
    # Start logging thread /* main program thread */
    logging_thread = threading.Thread(target=logging_thread, args=(log_queue,))
    logging_thread.start()

    udids_file = "devices.txt"  # Path to the file containing UDIDs
    udids = read_udids_from_file(udids_file)
    processes = []
    # Create and start multi process
    for i, udid in enumerate(udids):
        instance_port = 4723 + i   # every instance should connect to different appium server port
        
        process = multiprocessing.Process(target=login_and_download, args=(instance_port, udid))
        processes.append(process)
        process.start()

    # Wait for all threads to complete
    for process in processes:
        process.join()

    # Log final completion message with timestamp
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"{timestamp} - Automation complete.")