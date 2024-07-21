import multiprocessing
import subprocess
import time
import json
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


def interact_with_element(wait, by_type, identifier, action="click", keys=None, print=None, udid=None):
    try:
        element = wait.until(EC.element_to_be_clickable((by_type, identifier)))
        if action == "click":
            element.click()
        elif action == "send_keys":
            element.clear()
            element.send_keys(keys)
        print(f"{udid}: {identifier} - successfully interacted.")
    except Exception as e:
        print(f"{udid}: Failed to interact with {identifier} - {str(e)}")



def session_manager(instance_port, udid):


    try:
        appium_service = AppiumService()
        appium_service.start(args=['--address', '127.0.0.1', '--port', str(instance_port), '-pa', '/wd/hub'])

        #load app data from config file // Example : spotify apk
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)

        desired_caps = {
            'platformName': 'Android',
            'automationName': 'UiAutomator2',
            'udid': str(udid),
            "appPackage": config["appPackage"],
            "appActivity": config["appActivity"],
            "noReset": config["noReset"],  # Preserve app data & state
        }
        option = AppiumOptions().load_capabilities(desired_caps)
        driver = webdriver.Remote(f'http://127.0.0.1:{instance_port}/wd/hub', options=option)

        #run auto testing
        Auto_test_steps()

        print("testing is completed")

    except Exception as e:
        print(f"Exception occurred in instance {udid}: {str(e)}")

        appium_service.stop()  # Ensure Appium service is stopped

if __name__ == "__main__":
    udids = "127.0.0.1:6562"
    port = 4724
    session_manager(port,udids)

    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Automation complete.")
