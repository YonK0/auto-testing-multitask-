# Auto testing mobile apps (multitasking) Description : 
this script uses multithread and multiprocess makes more easier to run auto testing for mobile apps with logging .
this is the workflow of the script : 

![image](https://github.com/user-attachments/assets/79c2e1c9-82c1-4de5-8ef3-7042e1d4693c)

PS : this project can run on Windows and Linux.

# Detailed installation and setting Up
You can find detailed installation of all used tools in my old repo :
https://github.com/YonK0/appium-multithread

# Appium 

![image](https://github.com/user-attachments/assets/15b84812-a6bf-41a6-8b81-f437a720812a)

Appium is a mobile automation testing tool which is used to automate mobile applications on different mobile operating systems such as Android and iOS.


# Emulator used : Any Android emulator can be used here
personally i tried with nox , bluestacks and genymotion (best one for me ).


# Adb 
![image](https://github.com/user-attachments/assets/8c3171f0-450f-4f3c-9f6f-53f7ae1bc81b)

Android Debug Bridge ( adb ) is a versatile command-line tool that lets you communicate with a device.

1.adb address and port you can find in parameters on the emulator for example : 

![image](https://github.com/user-attachments/assets/b550cfa9-e22c-4ec5-b03f-45216f709014)

2.after you got the address and port copy them to devices.txt if you want that devices included.


# Running multitask script : 

now have adb and appium installed and setted up , let's run our script !!!  

![image](https://github.com/user-attachments/assets/bfcfbdfa-52d0-44f8-a89d-57ddaecc36b1)

as the image show , we are ready to run the script : 
` python multitask.py `

Now you can see all instances are running the auto testing at the same time , meanwhile the logging is running too (automation.log).

![image](https://github.com/user-attachments/assets/3cbe6723-7716-4786-8b85-427365111d12)

Check log while the multitasking in running   : ` tail -f  automation.log ` || or notepad++ in windows  

PS: you can open whatever number of instances you want , just make sure you have enough resources to run it ! 


Also i updoaded a simple video , showing how it works with 2 bluestacks instances (windows) : 
https://www.youtube.com/watch?v=DzMka7yeTKo

Im willing to upload another video showing more complex steps with more instances , on a Linux machine in the future.
