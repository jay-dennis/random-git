import pandas as pd
import os
import random
import string
import subprocess
from time import sleep
import urllib.request


sleep_time = 2  # give the file system time to catch up with git during commits and merges


def get_word_list():
    word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = urllib.request.urlopen(word_site)
    txt = response.read()
    words = txt.splitlines()
    return words


def loadnames(fn=None, process=False, save=False):
    if fn is None:
        fn = "./names.csv"
    names = pd.read_csv(fn)
    if process:
        names["email"] = names["first"].apply(lambda x: x[0]).str.lower() + names["last"].str.lower() + "@notarealcompany.org"
        names["git"] = names["first"] + " " + names["last"] + " <" + names["email"] + ">"
        if save:
            names.to_csv(fn, index=False)
    return names


def random_string(length=None, l=5, u=30):
    if length is None:
        length = random.randint(l, u)
    letters = string.ascii_lowercase
    out = ''.join(random.choice(letters) for i in range(length))
    return out


def random_words(num=None, l=1, u=7):
    if num is None:
        num = random.randint(l, u)
    words = get_word_list()
    words = random.sample(words, num)
    words = " ".join([i.decode("utf-8") for i in words])
    return words


def commit(author=None, authorlist=None, m=None, system_call=True, verbose=False):
    sleep(sleep_time)
    if m is None:
        m = random_words()
    if author is None:
        if authorlist is None:
            names = loadnames()
            authorlist = random_authors(names, num=1)
        author = random.choice(authorlist)
    cmd_commit = "git commit -m \"" + m + "\" --author \"" + author + "\""
    if verbose:
        print(cmd_commit)
    if system_call:
        os.system("git add .")
        sleep(sleep_time)
        os.system(cmd_commit)
        # info = subprocess.run(['git', 'add', "."], shell=True, capture_output=True)
        # info = subprocess.run(cmd_commit.split(" "), shell=True, capture_output=True)
        # info.stderr.decode('utf-8')
        sleep(sleep_time)
    return None


def random_authors(names, num=10):
    return [a for a in random.sample(list(names["git"]), num)]


def random_content(numlines=None, l=5, u=100):
    if numlines is None:
        numlines = random.randint(l, u)
    new_content = [random_words() + "\n" for i in range(numlines)]
    return new_content


def modify_contents(old_contents, num=10):
    new_contents = old_contents.copy()
    N = len(old_contents)
    ind = [i for i in range(N)]
    ind = random.sample(ind, min(num, N))
    for i in ind:
        new_contents[i] = random_words() + "\n"
    return new_contents


def new_file(fn=None, new_content=None, verbose=False):
    if fn is None:
        fn = random_words(l=1, u=3).replace(" ", "_") + "." + random_string(l=2, u=3)
    if not os.path.exists(fn):
        if new_content is None:
            new_content = random_content()
        with open(fn, 'w') as f:
            f.writelines(new_content)
    else:
        modify_file(fn=fn)
    if verbose:
        print(fn)
    return fn


def modify_file(fn=None, append=None):
    if append is None:
        append = random.choice([True, False])
    if fn is not None:
        prohibited = ["random-git.py", "names.csv", ".gitignore", ".gitattributes"]
        if fn not in prohibited:
            if append:
                new_content = random_content(l=2, u=7)
                with open(fn, 'a') as f:
                    f.writelines(new_content)
            else:
                with open(fn, 'r') as file:
                    old_content = file.readlines()
                new_content = modify_contents(old_content)
                with open(fn, 'w') as f:
                    f.writelines(new_content)
    return None


def random_existing_file(num=1):
    prohibited = ['.git', '.gitattributes', '.gitignore', '.idea', 'names.csv', 'random-git.py']
    file_list = os.listdir()
    file_list = [f for f in file_list if f not in prohibited]
    if len(file_list) > 0:
        out = random.sample(file_list, min(len(file_list), num))
    else:
        out = []
    return out


def git_cleanup():
    info = subprocess.run(['git', 'gc'], shell=True, capture_output=True)
    return info


def new_branch(name=None):
    # cmdnew = "git branch " + name
    # os.system(cmdnew)
    if name is not None:
        newbranch = subprocess.run(['git', 'branch', name], shell=True, capture_output=True)
    else:
        newbranch = None
    sleep(sleep_time)
    return newbranch


def checkout_branch(name=None):
    # cmdcheckout = "git checkout " + name
    # os.system(cmdcheckout)
    if name is not None:
        checkoutbranch = subprocess.run(['git', 'checkout', name], shell=True, capture_output=True)
    else:
        checkoutbranch = None
    sleep(sleep_time)
    return checkoutbranch


def merge(authorlist=None, receiving=None, transmitting=None, checkout=False, author=None):
    sleep(sleep_time)
    if author is None:
        if authorlist is None:
            names = loadnames()
            authorlist = random_authors(names, num=1)
        author = random.choice(authorlist)
    if (receiving is not None) & (transmitting is not None):
        # merge deconflict
        ## parse output from merge
        ## look for "CONFLICT (content): Merge conflict in <file name>"
        ## deconflict each conflicted file
        ## then commit
        #
        commit(author=author, m="clean up", system_call=True)
        sleep(sleep_time)
        if checkout:
            info = checkout_branch(receiving)
        # result = subprocess.run(["git", "merge", "--no-ff", transmitting], shell=True, capture_output=True)
        result = subprocess.run(["git", "merge", "--no-commit", transmitting], shell=True, capture_output=True)
        sleep(sleep_time)
        output = result.stdout.decode('utf-8')
        # output = result.stderr.decode('utf-8')
        output = output.split("\n")
        conflicted_files = [o.split("Merge conflict in ")[1] for o in output if "CONFLICT" in o]
        if len(conflicted_files) > 0:
            for cf in conflicted_files:
                deconflict(fn=cf, resolve="Head", transmitting=None)
        commit(author=author, m="Merging branch " + transmitting, system_call=True)
    sleep(sleep_time)
    return None


def deconflict(fn, resolve="Head", transmitting=None):
    # place holder
    # current branch begins "<<<<<<< HEAD"
    # sep and transmitting branch begins "======="
    # conflict ends with ">>>>>>> <transmitting branch name>
    # allow randomly choosing which to accept
    # then run commit() again with m = "Merging brach <branch name>" after resolving all conflicts in all files (outside this function)
    with open(fn, 'r') as f:
        content = f.readlines()
    conflicts = {}
    linenum = 0
    for line in content:
        if "<<<<<<< HEAD" in line:
            ind = len(conflicts) + 1
            conflicts[ind] = {"start": None, "mid": None, "end": None}
            conflicts[ind]["start"] = linenum
        elif "=======" in line:
            if conflicts[ind]["start"] is not None:
                conflicts[ind]["mid"] = linenum
        elif ">>>>>>> " in line:
            if conflicts[ind]["start"] is not None:
                conflicts[ind]["end"] = linenum
        linenum = linenum + 1
    for i in reversed(list(conflicts.keys())):  # start with the last conflict and work backwards
        head = [c for c in range(conflicts[i]["start"], conflicts[i]["mid"]+1)] + [conflicts[i]["end"]]
        tran = [conflicts[i]["start"]] + [c for c in range(conflicts[i]["mid"], conflicts[i]["end"]+1)]
        if resolve == "random":
            resolve = random.choice(["Head", "transmitting"])
        if resolve == "Head":
            for j in tran[::-1]:
                content.pop(j)
        elif resolve == "transmitting":
            for j in head[::-1]:  # remove lines starting with the last one and working backwards
                content.pop(j)
    with open(fn, 'w') as f:
        f.writelines(content)
    return None


def git_init(main=None):
    if not os.path.exists(".git"):
        result = subprocess.run(["git", "init"], shell=True, capture_output=True)
    # TODO: check main branch name
    if main is None:
        main = "main"
    result = subprocess.run(["git", "branch", "-m", main], shell=True, capture_output=True)
    return None


def make_gitignore():
    gitignore = ["/**/.idea\n", "/**/*.csv\n", "/**/*.py\n"]
    if os.path.exists(".gitignore"):
        mode = 'a'
    else:
        mode = 'w'
    with open(".gitignore", mode) as f:
        f.writelines(gitignore)
    return None


def random_git_log(names=None, numauthors=5, numfiles=5, numbranches=3, numcommits=10, mergefrequency=5):
    if names is None:
        names = loadnames()
    make_gitignore()
    git_init()
    authorlist = random_authors(names, num=numauthors)  # get some random authors
    branches = [random_words(l=1, u=2).replace(" ", "-") for b in range(numbranches)]  # create branch list
    for i in range(numfiles):
        sleep(sleep_time)
        if i > 0:  # first commit to main branch
            current_branch = random.choice(branches)  # randomly choose which branch will be edited
            info = new_branch(name=current_branch)
            info = checkout_branch(name=current_branch)
        newfn = new_file()  # make and modify files randomly
        commit(authorlist=authorlist, system_call=True)  # randomly choose an author to commit the changes
    for i in range(numcommits):
        sleep(sleep_time)
        current_branch = random.choice(branches)
        checkout_branch(current_branch)
        files = random_existing_file(num=5)
        for f in files:
                modify_file(fn=f)
        commit(authorlist=authorlist, system_call=True)
        if i % mergefrequency == 0:
            sleep(sleep_time)
            ## every mergefrequency, merge the current branch into main and deconflict
            merge(authorlist=authorlist, receiving="main", transmitting=current_branch, checkout=True)
    checkout_branch("main")
    for current_branch in branches:  # clean up by merging everything to main
        sleep(sleep_time)
        merge(authorlist=authorlist, receiving="main", transmitting=current_branch, checkout=False)
    git_cleanup()
    return None


if __name__ == "__debug__":
    names = loadnames()
    random_string()
    random_authors(names, num=10)
    a = random_content()
    modify_contents(a, num=10)
    a = new_file()
    modify_file(a)
    random_existing_file()
    commit(verbose=True, system_call=True)
    deconflict("temp.txt", resolve="Head", transmitting=None)


if __name__ == "__main__":
    random_git_log(names=None, numauthors=5, numfiles=5, numbranches=3, numcommits=20, mergefrequency=5)
