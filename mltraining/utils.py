import os, tarfile, shutil, pathlib

def prepare_bash_script(input_file, output_file, find_string, replacement_string):
    """
    Prepare a well-formatted Bash script from an input file, with a specified string replacement.

    :param input_file: Path to the input file
    :param output_file: Path to the output file
    :param replacement_string: The string to replace find_string with
    """
    # Read the input file content
    with open(input_file, 'r') as f:
        text = f.read()

    # Replace occurrences of "mlwb-scripts" with the replacement string
    text = text.replace(find_string, replacement_string)

    # Define the Bash script content
    bash_script = text

    # Replace any Windows-style line endings (CRLF) with Unix-style line endings (LF)
    bash_script = bash_script.replace('\r\n', '\n')

    # Write the script to the output file
    with open(output_file, 'w') as f:
        f.write(bash_script)

    print(f"Bash script saved to {output_file}.")

def create_lc_scripts_for_user(username):
    user_dir = os.path.join(os.getcwd()+"/mltraining/", username)
    
    #check if path exists
    #if it doesn’t exist we create one    
    if not os.path.exists(user_dir):        
        os.makedirs(user_dir)

    # create bash script 1
    input_file = os.path.join(os.getcwd()+"/mltraining/", "generic_lifecycle_config.txt")
    output_file = user_dir + "/generic_lifecycle_config.sh" 
    print(user_dir)
    find_string = "username"
    replacement_string = username
    prepare_bash_script(input_file, output_file, find_string, replacement_string)

    # create bash script 2
    input_file = os.path.join(os.getcwd()+"/mltraining/", "sagemaker_inst_bootstrap.txt")
    output_file = user_dir + "/sagemaker_inst_bootstrap.sh"
    find_string = "mlwb-nbks"
    replacement_string = "mlwb-nbks/"+username
    prepare_bash_script(input_file, output_file, find_string, replacement_string)
    input_file = os.path.join(user_dir, "sagemaker_inst_bootstrap.sh")
    find_string = "mlwb-scripts"
    replacement_string = "mlwb-scripts/"+username
    prepare_bash_script(input_file, output_file, find_string, replacement_string)

    # create bash script 3
    input_file = os.path.join(os.getcwd()+"/mltraining/", "sync_sm_notebooks.txt")
    output_file = user_dir + "/sync_sm_notebooks.sh"
    find_string = "mlwb-nbks"
    replacement_string = "mlwb-nbks/"+username
    prepare_bash_script(input_file, output_file, find_string, replacement_string)

    # create bash script 4
    input_file = os.path.join(os.getcwd()+"/mltraining/", "notebook-sync-cron")
    output_file = user_dir + "/notebook-sync-cron"
    find_string = "user"
    replacement_string = "user"
    prepare_bash_script(input_file, output_file, find_string, replacement_string)



def extract_metadata(file):
    """
    Extracts metadata from a tar.gz file.

    Returns a list of tuples containing label name and number of images.
    """
    label_counts = {}
    with tarfile.open(fileobj=file, mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                path_parts = member.name.split('/')
                # Find the last subdirectory that contains files
                label = None
                for i in range(len(path_parts)-1, 0, -1):
                    if tar.getmember('/'.join(path_parts[:i])).isdir():
                        label = path_parts[i-1]
                        break
                # Only count the label if it contains files
                if label and member.name.endswith('.jpg'):
                    if label in label_counts:
                        label_counts[label] += 1
                    else:
                        label_counts[label] = 1

    return [(k, v) for k, v in label_counts.items()]


def extract_dataset(dataset_dir, label_dir, label):
    # Extract the contents of the .tar.gz file
    with tarfile.open(f"{dataset_dir}/data.tar.gz", "r:gz") as tar:
        tar.extractall(path=label_dir)

    print("Dataset extracted to:", label_dir)

    data_dir = pathlib.Path(label_dir)

    # Find the folder containing class subdirectories
    for sub_dir in data_dir.glob('*'):
        if sub_dir.is_dir():
            sub_sub_dirs = list(sub_dir.glob('*'))
            if sub_sub_dirs and any([sub_sub_dir.name == label for sub_sub_dir in sub_sub_dirs]):
                label_dir = [sub_sub_dir for sub_sub_dir in sub_sub_dirs if sub_sub_dir.name == label][0]
                for img_file in label_dir.glob('*'):
                    shutil.move(str(img_file), str(data_dir / img_file.name))
                shutil.rmtree(str(sub_dir))
                break

    return data_dir