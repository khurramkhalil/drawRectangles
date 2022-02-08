import hashlib
import json
import os
import shutil
import subprocess
import networkx as nx


def checksum(filename, parent=None):
    dvc_dir = os.getcwd() + '\\data\\raw'

    if not parent:

        # Open,close, read file and calculate MD5 on its contents
        with open(filename, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_parent = hashlib.md5(data).hexdigest()

        # If
        if not os.path.exists("network.gpickle"):
            net = nx.Graph()

            net.add_node('main', high_val=1)
            label = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()

            if label == 'main' or label == 'master':
                var = subprocess.run(["git", "checkout", "-b", "1"], check=True, stdout=subprocess.PIPE).stdout
                var = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()
                assert var == '1'

                net.add_node(md5_parent, parent='main', current=var)
                net.add_edge('main', md5_parent)

                # delete all contents from dvc tracked folder

                for f in os.listdir(dvc_dir):
                    if not (f.endswith(".gitignore") or f.endswith(".dvc")):
                        os.remove(os.path.join(dvc_dir, f))

                # copy file name to dvc_dir
                shutil.copy(filename, dvc_dir)

                # now add files to dvc
                dvc_add = subprocess.run(["dvc", "add", "./data/raw"], check=True, stdout=subprocess.PIPE).stdout
                git_add = subprocess.run(["git", "add", "./data/raw.dvc", "./data/.gitignore"], check=True,
                                         stdout=subprocess.PIPE).stdout
                # git_add = subprocess.run(["git", "add", "--all"], check=True, stdout=subprocess.PIPE).stdout
                git_commit = subprocess.run(["git", "commit", "-m", "1"], check=True, stdout=subprocess.PIPE).stdout
                git_push = subprocess.run(["git", "push"], check=True, stdout=subprocess.PIPE).stdout
                dvc_push = subprocess.run(["dvc", "push"], check=True, stdout=subprocess.PIPE).stdout

                nx.write_gpickle(net, "network.gpickle")

                return md5_parent

        else:

            net = nx.read_gpickle("network.gpickle")

            if md5_parent not in net:
                # come back to main
                git = subprocess.run(["git", "checkout", "main"], check=True, stdout=subprocess.PIPE).stdout
                dvc = subprocess.run(["dvc", "checkout"], check=True, stdout=subprocess.PIPE).stdout
                label = int(int(net.node['main']['high_val']) + 1)

                # make new branch
                var = subprocess.run(["git", "checkout", "-b", f"{label}"], check=True, stdout=subprocess.PIPE).stdout
                var = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()
                assert var == '1'

                # copy file name to dvc_dir
                shutil.copy(filename, dvc_dir)

                # now add files to dvc again
                dvc_add = subprocess.run(["dvc", "add", "./data/raw"], check=True, stdout=subprocess.PIPE).stdout
                git_add = subprocess.run(["git", "add", "--all"], check=True, stdout=subprocess.PIPE).stdout
                git_commit = subprocess.run(["git", "commit", "-m", f"{label}"], check=True,
                                            stdout=subprocess.PIPE).stdout
                git_push = subprocess.run(["git", "push"], check=True, stdout=subprocess.PIPE).stdout
                dvc_push = subprocess.run(["dvc", "push"], check=True, stdout=subprocess.PIPE).stdout

                # up the branch number
                net.node['main']['high_val'] = label

                net.add_node(md5_parent, parent='main', current=label)
                net.add_edge('main', md5_parent)

                nx.write_gpickle(net, "network.gpickle")

                return md5_parent

            # if already exists entry in network, checkout to that branch
            else:

                branch = net.node[md5_parent]['current']

                git = subprocess.run(["git", "checkout", f"{branch}"], check=True, stdout=subprocess.PIPE).stdout
                dvc = subprocess.run(["dvc", "checkout"], check=True, stdout=subprocess.PIPE).stdout

            return md5_parent

    else:
        md5_parent = parent
        # Open,close, read file and calculate MD5 on its contents
        with open(filename, 'rb') as file_to_check:
            # read contents of the file
            data = file_to_check.read()
            # pipe contents of the file through
            md5_child = hashlib.md5(data).hexdigest()

        net = nx.read_gpickle("network.gpickle")

        branch = net.node[md5_parent]['current']

        # come back to current branch
        git = subprocess.run(["git", "checkout", f"{branch}"], check=True, stdout=subprocess.PIPE).stdout
        dvc = subprocess.run(["dvc", "checkout"], check=True, stdout=subprocess.PIPE).stdout

        var = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()
        assert var == branch

        # Get highest value
        label = int(int(net.node['main']['high_val']) + 1)

        # make new branch
        var = subprocess.run(["git", "checkout", "-b", f"{label}"], check=True, stdout=subprocess.PIPE).stdout
        var = subprocess.check_output(["git", "branch", "--show-current"]).strip().decode()
        assert var == label

        # copy file name to dvc_dir
        shutil.copy(filename, dvc_dir)

        # now add files to dvc again
        dvc_add = subprocess.run(["dvc", "add", "./data/raw"], check=True, stdout=subprocess.PIPE).stdout
        git_add = subprocess.run(["git", "add", "--all"], check=True, stdout=subprocess.PIPE).stdout
        git_commit = subprocess.run(["git", "commit", "-m", f"{label}"], check=True, stdout=subprocess.PIPE).stdout
        git_push = subprocess.run(["git", "push"], check=True, stdout=subprocess.PIPE).stdout
        dvc_push = subprocess.run(["dvc", "push"], check=True, stdout=subprocess.PIPE).stdout

        # up the branch number
        net.node['main']['high_val'] = label

        net.add_node(md5_child, parent=branch, current=label)
        net.add_edge(md5_parent, md5_child)

        nx.write_gpickle(net, "network.gpickle")
