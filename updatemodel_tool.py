# readme 
# python -m PyInstaller --onefile .\updatemodel_tool.py 
# python3 -m PyInstaller --onefile .\updatemodel_tool.py 
# -w: no terminal required 
# Run: updatemodel_tool.exe 2 DYV4 
#      updatemodel_tool.exe 1 CYV4

import os
import sys
import shutil
import json
import re
from datetime import datetime, timezone
from sys import platform

DEBUG= True

def debug_print(message):
    if DEBUG:
        print(message)

# declear common file paths
usrmodel_path = os.path.abspath(os.path.dirname(sys.argv[0]))
for file_user_model in os.listdir(usrmodel_path):
    if file_user_model.endswith(".nb"):
        debug_print(os.path.join(usrmodel_path, file_user_model))
        # Get the file name without the file type extension recursively
        file_user_model_no_ext = os.path.splitext(os.path.basename(file_user_model))[0]
        debug_print(file_user_model_no_ext)

if platform == "win32":
    # Windows...
    arduino15_path = os.path.expanduser("~\AppData\Local\Arduino15")
    ambpro2_path = arduino15_path + "\packages\\realtek\hardware\AmebaPro2"
    sdk_version = os.listdir(ambpro2_path)[0]
    dest_path = ambpro2_path + "\\" + sdk_version + "\\variants\common_nn_models"
elif platform == "linux" or platform == "linux2":
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

model_mapping = {
    "CYV3": "yolov3_tiny",
    "CYV4": "yolov4_tiny",
    "CYV7": "yolov7_tiny",
    "CM": "mobilefacenet_i8",
    "CS": "scrfd320p",
    "DYV3": "yolov3_tiny",
    "DYV4": "yolov4_tiny",
    "DYV7": "yolov7_tiny",
    "DM": "mobilefacenet_i8",
    "DS": "scrfd320p"
}

allowed_values = ["CYV3", "CYV4", "CYV7", "CM", "CS", "DYV3", "DYV4", "DYV7", "DM", "DS"]

def dspFileProp(filename):
    file_model_stats = os.stat(filename)
    file_model_datetime = datetime.fromtimestamp(file_model_stats.st_mtime, tz = timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    file_model_date = datetime.fromtimestamp(file_model_stats.st_mtime, tz = timezone.utc).strftime('%Y-%m-%d')
    file_model_mode = oct(file_model_stats.st_mode)
    debug_print("              FILE INFO")
    debug_print("------------------------------------------")
    debug_print(f"Size:          {file_model_stats.st_size}")
    debug_print(f"Last modified: {file_model_datetime}")
    debug_print(f"Mode:          {file_model_mode}")
    debug_print("------------------------------------------")
    return file_model_date

def renameFile(filename, type):
    if type == 1:
        # Backup Dmodel
        filename_modified = "Dbackup_" + dspFileProp(filename) + "_" + filename
        if os.path.isfile(os.path.join(dest_path, filename_modified)) == False:
            os.rename(os.path.join(dest_path, filename), os.path.join(dest_path, filename_modified))
        debug_print("[INFO] Dmodel Backup done.")
    else:
        # Backup Cmodel
        filename_modified = "Cbackup_" + dspFileProp(filename) + "_" + filename
        if os.path.isfile(os.path.join(dest_path, filename_modified)) == False:
            os.rename(os.path.join(dest_path, filename), os.path.join(dest_path, filename_modified))
        debug_print("[INFO] Cmodel Backup done.")

def backupModel(user_model):
    """
    Backup user model whether exists.

    Returns:
    None
    """
    debug_print("[INFO] Backup Default Model: " + input2model(user_model))
    for dest_file in os.listdir(dest_path):
        if "Dbackup" in dest_file:
            debug_print(f"[INFO] Backup Default Model {user_model} found !!!")
        elif input2model(user_model) in dest_file:
            # backup default model
            renameFile(input2model(user_model) + ".nb", 1)
    
    # backup Cmodel
    if platform == "linux" or platform == "linux2" or platform == "darwin" : 
            # linux & OS X
        shutil.copy(usrmodel_path + "/" + file_user_model, dest_path)
    #                     # elif platform == "darwin":
    #                     #     # OS X
    elif platform == "win32":
    #                         # Windows...
        shutil.copy(usrmodel_path + "\\" + input2model(user_model) + ".nb", dest_path)
    debug_print(input2model(user_model) + ".nb")
    renameFile(input2model(user_model) + ".nb", 0)

    # copy Cmodel
    if platform == "linux" or platform == "linux2" or platform == "darwin" : 
            # linux & OS X
        shutil.copy(usrmodel_path + "/" + file_user_model, dest_path)
    #                     # elif platform == "darwin":
    #                     #     # OS X
    elif platform == "win32":
    #                         # Windows...
        shutil.copy(usrmodel_path + "\\" + input2model(user_model) + ".nb", dest_path)
    debug_print("[INFO] User model copied.")

        
                # # Revert backup model
                # file_model_reverted = file_model.split("_", 2)[2]
                # debug_print(file_model_reverted)
                # # TODO delete copied user file
                # if os.path.exists(dest_path + "/" + file_model_reverted):
                #     if platform == "linux" or platform == "linux2" or platform == "darwin" : 
                #         # linux & OS X
                #         os.remove(dest_path + "/" + file_model_reverted)
                #     elif platform == "win32":
                #         # Windows...
                #         os.remove(dest_path + "\\" + file_model_reverted)
                # else:
                #     debug_print("[Error] Cannot find model file")
    #             debug_print("[INFO] User model deleted.")
    #             # TODO rename backuped model back to normal
    #             os.rename(os.path.join(dest_path, file_model), os.path.join(dest_path, file_model_reverted))
    #             debug_print("[INFO] Revert done.")
    #             break
            # else:
            #     if file_user_model_no_ext in file_model:
            #         # TODO file size !=0
            #         file_user_model = file_model
            #         debug_print(f"Model {file_model} contains the keyword {file_user_model} has found !!!")
    #                 # Get file properties
    #                 if os.path.exists(file_user_model_no_ext + ".nb"):
    #                     debug_print("[INFO] Backup starts ....")
    #                     # Backup Dmodel
    #                     file_model_modified = "Dbackup_" + dspFileProp(file_user_model) + "_" + file_model
    #                     os.rename(os.path.join(dest_path, file_model), os.path.join(dest_path, file_model_modified))
    #                     debug_print("[INFO] Dmodel Backup done.")
                        
    #                     # Copy Cmodel
    #                     if platform == "linux" or platform == "linux2" or platform == "darwin" : 
    #                         # linux & OS X
    #                         shutil.copy(usrmodel_path + "/" + file_user_model, dest_path)
    #                     # elif platform == "darwin":
    #                     #     # OS X
    #                     elif platform == "win32":
    #                         # Windows...
    #                         shutil.copy(usrmodel_path + "\\" + file_user_model, dest_path)
    #                     debug_print("[INFO] User model copied.")
    #                     # Backup Cmodel
    #                     debug_print(file_user_model)
                        
    #                     file_model_modified = "Cbackup_" + dspFileProp(file_user_model) + "_" + file_model
    #                     # debug_print(file_model_modified)
    #                     os.rename(os.path.join(dest_path, file_model), os.path.join(dest_path, file_model_modified))
    #                     debug_print("[INFO] Cmodel Backup done.")
    #                     shutil.copy(usrmodel_path + "\\" + file_user_model, dest_path)
    #                 else:
    #                     debug_print(f"The file {file_user_model_no_ext}.nb does not exist.")
    #             else:  
    #                 continue
    # debug_print("==================================")

def revertModel(user_model):
    for dest_file in os.listdir(dest_path):
        if "Dbackup" in dest_file:
            debug_print(f"[INFO] Defaut backup model {dest_file} found")
            file_model_reverted = dest_file.split("_", 2)[2]
            if os.path.exists(dest_path + "/" + file_model_reverted):
                if platform == "linux" or platform == "linux2" or platform == "darwin" : 
                    # linux & OS X
                    os.remove(dest_path + "/" + file_model_reverted)
                elif platform == "win32":
                    # Windows...
                    os.remove(dest_path + "\\" + file_model_reverted)
                debug_print(f"[INFO] User Model {file_model_reverted} has been removed")
            # revert Dbackup
            os.rename(os.path.join(dest_path, dest_file), os.path.join(dest_path, file_model_reverted))
            debug_print("[INFO] Revert done.")

def updateJSON(option, input):
    """
    Updates a JSON file based on the input parameters.

    Args:
    option (int): 0 for default settings, 1 for user settings.
    user_model (str, optional): The user model to use (required if option is 1).

    Returns:
    None
    """
    debug_print(input2model(input))
    for file_json in os.listdir(dest_path):
        if file_json.endswith(".json"):
            debug_print(file_json)
            # Read the existing data from the file

                
            with open(os.path.join(dest_path, file_json), "r+") as file:
                print(os.path.join(dest_path, file_json))
                data = json.load(file)
            
            
                # if option == 0:
                    # Default Settings
                    # data["FWFS"]["files"] = ['yolov4_tiny', 'scrfd320p', 'mobilefacenet_i8'] 
                # elif option == 1:
                #     # Update the "files" list in the "FWFS" dictionary based on user model name
                #     if file_user_model:
                #         data["FWFS"]["files"] = [file_user_model_no_ext]
                #     else:
                #         debug_print('Error: user_model parameter is required when option is 1')
                #         return
                # else:
                #     debug_print('Error: Invalid option')
                #     return
            
            # # Write the updated data back to the file
            # with open(os.path.join(dest_path, file_json), "w") as file:
            #     json.dump(data, file, indent=4)
            # if option == 0:
            #     debug_print('[INFO] JSON file reverted to default successfully.')
            # else:
            #     debug_print('[INFO] JSON file updated successfully.')

def getUserInput_origin():
    """
    Displays a menu and prompts the user to select an option.

    Options:
    1. Input user model
    2. Use default settings

    If the user selects option 1, the function prompts the user to enter a user model.
    If the user selects option 2, the function uses default settings.
    """
    user_input_flag = 0
    while user_input_flag == 0:
        debug_print("--------------------------")
        debug_print("Please select an option:")
        debug_print("1. Input user model")
        debug_print("2. Use default settings")
        debug_print("--------------------------")

        if len(sys.argv) > 1:
            # User has provided input, so we can access it
            user_input = sys.argv[1]
            debug_print(f"User input: {user_input}")
        else:
            # User has not provided input, so we prompt them to do so
            debug_print("Error: Please provide input.")
            user_input = input("> ")
            debug_print(f"User input: {user_input}")
        
        if user_input == "1" and user_input_flag == 0:
            while True:
                # Use user model
                debug_print("--------------------------")
                debug_print("Input user model:")
                debug_print("CYV3: Customize Yolov3")
                debug_print("CYV4: Customize Yolov4")
                debug_print("CYV7: Customize Yolov7")
                debug_print("CM: Customize MobileFaceNet")
                debug_print("CS: Customize SCRFD")
                debug_print("--------------------------")
                debug_print("Enter your option: ")
                if len(sys.argv) > 1:
                    # User has provided input, so we can access it
                    user_input_sub1 = sys.argv[2]
                    debug_print(f"User input: {user_input_sub1}")
                else:
                    # User has not provided input, so we prompt them to do so
                    user_input_sub1 = input("> ")
                    debug_print(f"User input: {user_input_sub1}")
                user_input_flag = True
                if user_input_sub1 in allowed_Cvalues:
                    backupModel(user_input_sub1)
                    updateJSON(1, user_input_sub1) 
                    break
                else:
                    debug_print("Invalid choice. Please enter valid user model.")
                    break
                
        elif user_input == "2" and user_input_flag == 0:
            while True:
                # Use default settings
                debug_print("--------------------------")
                debug_print("Input default model:")
                debug_print("DYV3: Default Yolov3")
                debug_print("DYV4: Default Yolov4")
                debug_print("DYV7: Default Yolov7")
                debug_print("DM: Default MobileFaceNet")
                debug_print("DS: Default SCRFD")
                debug_print("--------------------------")
                debug_print("Enter your option: ")
                if len(sys.argv) > 1:
                    # User has provided input, so we can access it
                    user_input_sub1 = sys.argv[2]
                    debug_print(f"User input: {user_input_sub1}")
                else:
                    # User has not provided input, so we prompt them to do so
                    user_input_sub1 = input("> ")
                    debug_print(f"User input: {user_input_sub1}")
                user_input_flag = True
                if user_input_sub1 in allowed_Dvalues:
                    updateJSON(1, user_input_sub1) 
                    break
                else:
                    debug_print("Invalid choice. Please enter valid user model.")
                    break
        else:
            debug_print("Invalid choice. Please enter 1 or 2.")
            break

def dsp_user_menu():
    """
    Displays a menu and prompts the user to select an option.
    """
    options = [
        ("CYV3", "Customize Yolov3"),
        ("CYV4", "Customize Yolov4"),
        ("CYV7", "Customize Yolov7"),
        ("CM", "Customize MobileFaceNet"),
        ("CS", "Customize SCRFD"),
        ("DYV3", "Default Yolov3"),
        ("DYV4", "Default Yolov4"),
        ("DYV7", "Default Yolov7"),
        ("DM", "Default MobileFaceNet"),
        ("DS", "Default SCRFD")
    ]
    debug_print("--------------------------")
    debug_print("Input user model:")
    for option in options[:5]:
        debug_print(f"{option[0]}: {option[1]}")
    debug_print("--------------------------")
    debug_print("Input default model:")
    for option in options[5:]:
        debug_print(f"{option[0]}: {option[1]}")
    debug_print("--------------------------")

def input2model(input):
    # convert user parameter into model name
    model_mapping = {
        "CYV3": "yolov3_tiny",
        "CYV4": "yolov4_tiny",
        "CYV7": "yolov7_tiny",
        "CM": "mobilefacenet_i8",
        "CS": "scrfd320p",
        "DYV3": "yolov3_tiny",
        "DYV4": "yolov4_tiny",
        "DYV7": "yolov7_tiny",
        "DM": "mobilefacenet_i8",
        "DS": "scrfd320p"
    }
    model = model_mapping.get(input)
    return model

def validationCheck(input):
    if input in allowed_values:
        if input[0] == 'C':
            # convert input to model
            input = input2model(input) + ".nb"
            if os.path.isfile(input):
                debug_print(f"[INFO] Customized Model {input} Found!")
                return 1
            else:
                debug_print(f"[Error] Model {input} NOT Found! Please check your input again.")
        if input[0] == 'D':
            return 0
    else:
        debug_print("[Error] Please enter valid input.")
        
def getUserInput():
    user_input_flag = False
    while user_input_flag == False:
        dsp_user_menu()
        if len(sys.argv) > 1:
            # User has provided input, so we can access it
            user_input_sub1 = sys.argv[1]
            debug_print(f"User input: {user_input_sub1}")
        else:
            # User has not provided input, so we prompt them to do so
            user_input_sub1 = input("Please provide a valid input > ")
            debug_print(f"User input: {user_input_sub1}")
        user_input_flag = True
        if validationCheck(user_input_sub1) == 1:
            backupModel(user_input_sub1)
        else:
            revertModel(user_input_sub1)


    updateJSON(1, user_input_sub1) 

#####################################################################################
# Main Function
# Default script location: tools/
#####################################################################################
if __name__ == '__main__':
    # TODO: customized folder validation
    getUserInput()
    
    # input("Press Enter to leave the terminal")

#################################################################
# TODO: multi model support []
# TODO: model size check []
# TODO: arduino.ino YOLOMODEL []
