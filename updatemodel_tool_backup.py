# readme 
# python -m PyInstaller --onefile .\updatemodel_tool.py 
# python3 -m PyInstaller --onefile .\updatemodel_tool.py 
# -w: no terminal required

import os
import sys
import shutil
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from sys import platform

# declear common file paths
usrmodel_path = os.path.abspath(os.path.dirname(sys.argv[0]))
for file_user_model in os.listdir(usrmodel_path):
    if file_user_model.endswith(".nb"):
        # print(os.path.join(usrmodel_path, file_user_model))
        # Get the file name without the file type extension recursively
        file_user_model_no_ext = os.path.splitext(os.path.basename(file_user_model))[0]
        #  print(file_user_model_no_ext)

if platform == "linux" or platform == "linux2":
    # linux
    arduino15_path = os.path.expanduser("/home/" + os.getlogin() + "/.arduino15")
    ambpro2_path = arduino15_path + "/packages/realtek/hardware/AmebaPro2/"
    sdk_version = os.listdir(ambpro2_path)[0]
    dest_path = ambpro2_path + "/" + sdk_version + "/variants/common_nn_models"
elif platform == "darwin":
    # OS X
    arduino15_path = os.path.expanduser("/Users/" + os.getlogin() + "/Library/Arduino15")
    ambpro2_path = arduino15_path + "/packages/realtek/hardware/AmebaPro2/"
    sdk_version = os.listdir(ambpro2_path)[1]
    dest_path = ambpro2_path + "/" + sdk_version + "/variants/common_nn_models"
elif platform == "win32":
    # Windows...
    arduino15_path = os.path.expanduser("~\AppData\Local\Arduino15")
    ambpro2_path = arduino15_path + "\packages\\realtek\hardware\AmebaPro2\\"
    sdk_version = os.listdir(ambpro2_path)[0]
    dest_path = ambpro2_path + "\\" + sdk_version + "\\variants\common_nn_models"
#print(sdk_version)
#print(dest_path)

def backupModel(user_model):
    """
    Check user model whether exists.

    Returns:
    None
    """
    for file_model in os.listdir(dest_path):
        if file_model.endswith(".nb"):
            if "backup" in file_model:
                print(f"INFO: Backuped Model {file_model} has found !!!")
                break
            else:
                if file_user_model in file_model:
                    # TODO file size !=0
                    print(f"Model {file_model} contains the keyword {file_user_model} has found !!!")
                    # Get file properties
                    file_model_stats = os.stat(user_model)
                    print("--------------------------")
                    print("Size:          ", file_model_stats.st_size)
                    print("Last modified: ", datetime.fromtimestamp(file_model_stats.st_mtime, tz = timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
                    print("Mode:          ", oct(file_model_stats.st_mode))
                    print("--------------------------")
                    print("INFO: Backup starts....")
                    # Backup model
                    file_model_modified = "backup_" + datetime.fromtimestamp(file_model_stats.st_mtime, tz = timezone.utc).strftime('%Y-%m-%d') + "_" + file_model
                    os.rename(os.path.join(dest_path, file_model), os.path.join(dest_path, file_model_modified))
                    print("INFO: Backup done.")
                    shutil.copy(usrmodel_path + "\\" + file_user_model, dest_path)
                    print("INFO: User model copied.")
                else:  
                    continue

# # updateJSON() 
# for file_json in os.listdir(dest_path):
#     if file_json.endswith(".json"):
#         # print(os.path.join(dest_path, file_json))
#         # print(file_json)
#         # Read the existing data from the file
#         with open(os.path.join(dest_path, file_json), "r+") as file:
#             data = json.load(file)
#         # Update the "files" list in the "FWFS" dictionary
#         data["FWFS"]["files"] = [file_user_model_no_ext]
#         # Default Settings
#         # data["FWFS"]["files"] = ['yolov4_tiny', 'scrfd320p', 'mobilefacenet_i8'] 
#         # Write the updated data back to the file
#         with open(os.path.join(dest_path, file_json), "w") as file:
#             json.dump(data, file, indent=4)
#         #################################################################

def updateJSON(option, user_model):
    """
    Updates a JSON file based on the input parameters.

    Args:
    option (int): 0 for default settings, 1 for user settings.
    user_model (str, optional): The user model to use (required if option is 1).

    Returns:
    None
    """
    print(user_model)
    for file_json in os.listdir(dest_path):
        if file_json.endswith(".json"):
            # print(os.path.join(dest_path, file_json))
            # print(file_json)
            # Read the existing data from the file
            with open(os.path.join(dest_path, file_json), "r+") as file:
                data = json.load(file)
            
            if "YV3" in user_model[1:]:
                print("yolov3_tiny")
            
            if user_model == "CYV3" or user_model == "DYV3":
                file_user_model_no_ext = "yolov3_tiny"
            elif user_model == "CYV4" or user_model == "DYV4":
                file_user_model_no_ext = "yolov4_tiny"
            elif user_model == "CYV7"or user_model == "DYV7":
                file_user_model_no_ext = "yolov7_tiny"
            elif user_model == "CM" or user_model == "DM" :
                file_user_model_no_ext = "mobilefacenet_i8"
            elif user_model == "CS" or user_model == "DS":
                file_user_model_no_ext = "scrfd320p"
            print(file_user_model_no_ext)
            
            if option == 0:
                # Default Settings
                data["FWFS"]["files"] = ['yolov4_tiny', 'scrfd320p', 'mobilefacenet_i8'] 
            elif option == 1:
                # Update the "files" list in the "FWFS" dictionary based on user model name
                if file_user_model:
                    data["FWFS"]["files"] = [file_user_model_no_ext]
                else:
                    print('Error: user_model parameter is required when option is 1')
                    return
            else:
                print('Error: Invalid option')
                return
            
            # Write the updated data back to the file
            with open(os.path.join(dest_path, file_json), "w") as file:
                json.dump(data, file, indent=4)
            if option == 0:
                print('INFO: JSON file reverted to default successfully.')
            else:
                print('INFO: JSON file updated successfully.')

def get_user_input():
    """
    Displays a menu and prompts the user to select an option.

    Options:
    1. Input user model
    2. Use default settings

    If the user selects option 1, the function prompts the user to enter a user model.
    If the user selects option 2, the function uses default settings.
    """
    user_input_flag = False
    while user_input_flag == False:
        print("--------------------------")
        print("Please select an option:")
        print("1. Input user model")
        print("2. Use default settings")
        print("--------------------------")

        if len(sys.argv) > 1:
            # User has provided input, so we can access it
            user_input = sys.argv[1]
            print(f"User input: {user_input}")
        else:
            # User has not provided input, so we prompt them to do so
            print("Error: Please provide input.")
            user_input = input("> ")
            print(f"User input: {user_input}")
        
        if user_input == "1" and user_input_flag == 0:
            while True:
                # Use user model
                print("--------------------------")
                print("Input user model:")
                print("CYV3: Customize Yolov3")
                print("CYV4: Customize Yolov4")
                print("CYV7: Customize Yolov7")
                print("CM: Customize MobileFaceNet")
                print("CS: Customize SCRFD")
                print("--------------------------")
                print("Enter your option: ")
                
                if len(sys.argv) > 1:
                    # User has provided input, so we can access it
                    user_input_sub1 = sys.argv[2]
                    print(f"User input: {user_input_sub1}")
                else:
                    # User has not provided input, so we prompt them to do so
                    user_input_sub1 = input("> ")
                    print(f"User input: {user_input_sub1}")
                user_input_flag = True
                print(user_input_sub1)
                updateJSON(1, user_input_sub1) # TODO: change to updateJSON(1, user_input_sub1)
                # TODO: check invalid input
                break
        elif user_input == "2" and user_input_flag == False:
            # Use default settings
            print("--------------------------")
            print("Input default model:")
            print("DYV3: Default Yolov3")
            print("DYV4: Default Yolov4")
            print("DYV7: Default Yolov7")
            print("DM: Default MobileFaceNet")
            print("DS: Default SCRFD")
            print("--------------------------")
            # updateJSON(0)
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

#####################################################################################
# Main Function
# Default script location: tools/
#####################################################################################
if __name__ == '__main__':
    get_user_input()                            # display menu
    input("Press Enter to leave the terminal")

#################################################################
# TODO: support 3 OS [DONE]
# TODO: multi model support []
# TODO: model size check []
# TODO: arduino.ino YOLOMODEL []
