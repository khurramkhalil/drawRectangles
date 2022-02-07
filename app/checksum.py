import hashlib
import json
import os
import subprocess


def checksum(filename, parent=None):
    if not parent:

        # Open,close, read file and calculate MD5 on its contents
        with open(filename, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_parent = hashlib.md5(data).hexdigest()

        # If
        if not os.path.exists("tree.json"):
            label = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()

            if label == 'master':
                var = subprocess.run(["git", "checkout", "-b", "1"], check=True, stdout=subprocess.PIPE).stdout
                var = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()
                assert var == '1'

            names = {md5_parent: '1'}
            with open("names.json", "w") as file1, open("tree.json", "w") as file2:
                json.dump(names, file1)
                json.dump({'1': ['1']}, file2)

            return md5_parent

        else:
            with open('names.json', 'r') as f1, open('tree.json', 'r') as f2:
                record = json.load(f1)
                tree = json.load(f2)

            # Finally, compare original MD5 with freshly calculated
            if md5_parent in record:
                suggest_branch = str(record[md5_parent])
                curr_branch = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()

                if not suggest_branch == curr_branch:
                    subprocess.check_output(["git", "checkout", f"{suggest_branch}"])
                    print("MD5 verified.")
                # pass

            print(md5_parent)
            print("MD5 verification failed!.")

            return md5_parent

    else:

        pass
