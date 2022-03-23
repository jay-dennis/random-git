import pandas as pd
import os
import random
import string
import subprocess


def loadnames():
    names = pd.read_csv("./names.csv")
    # names["email"] = names["first"].apply(lambda x: x[0]).str.lower() + names["last"].str.lower() + "@notarealcompany.org"
    # names.to_csv("names.csv", index=False)
    # names["git"] = names["first"] + " " + names["last"] + " <" + names["email"] + ">"
    return names


def random_string(length=None, l=5, u=30):
    if length is None:
        length = random.randint(l, u)
    letters = string.ascii_lowercase
    out = ''.join(random.choice(letters) for i in range(length))
    return out


def commit(author=None, authorlist=None, m=None, system_call=False, verbose=False):
    if m is None:
        m = random_string()
    if authorlist is None:
        names = loadnames()
        authorlist = random_authors(names, num=1)
    if author is None:
        author = random.choice(authorlist)
    cmd_commit = "git commit -m \"" + m + "\" --author \"" + author + "\""
    if verbose:
        print(cmd_commit)
    if system_call:
        os.system("git add .")
        os.system(cmd_commit)
    return None


def random_authors(names, num=10):
    return [a for a in random.sample(list(names["git"]), num)]


def random_content(numlines=None, l=5, u=100):
    if numlines is None:
        numlines = random.randint(l, u)
    new_content = [random_string() + "\n" for i in range(numlines)]
    return new_content


def modify_contents(old_contents, num=10):
    new_contents = old_contents.copy()
    N = len(old_contents)
    ind = [i for i in range(N)]
    ind = random.sample(ind, min(num, N))
    for i in ind:
        new_contents[i] = random_string()
        new_contents[i] = random_string() + "\n"
    return new_contents


def new_file(fn=None, new_content=None, verbose=False):
    if fn is None:
        fn = random_string() + "." + random_string(l=2, u=3)
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
        prohibited = ["random-git-log.py", "names.csv", ".gitignore", ".gitattributes"]
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
    prohibited = ['.git', '.gitattributes', '.gitignore', '.idea', 'names.csv', 'random-git-log.py']
    file_list = os.listdir()
    file_list = [f for f in file_list if f not in prohibited]
    if len(file_list) > 0:
        out = random.sample(file_list, min(len(file_list),num))
    else:
        out = []
    return out


def new_branch(name=None):
    # cmdnew = "git branch " + name
    # os.system(cmdnew)
    newbranch = subprocess.run(['git', 'branch', name], shell=True, capture_output=True)
    return newbranch


def checkout_branch(name=None):
    # cmdcheckout = "git checkout " + name
    # os.system(cmdcheckout)
    checkoutbranch = subprocess.run(['git', 'checkout', name], shell=True, capture_output=True)
    return checkoutbranch


def merge(receiving=None, transmitting=None):
    if (receiving is not None) & (transmitting is not None):
        os.system("git checkout " + receiving)
        os.system("git merge --no-ff " + transmitting)
        result = subprocess.run(['dir', '-a'], stdout=subprocess.PIPE)
        result.stdout.decode('utf-8')
        result = subprocess.run(['ls', '-l'], shell=True, capture_output=True)
        result = subprocess.run(["git", "log"], shell=True, capture_output=True)
        result.stdout
        result.stderr.decode('utf-8')
        # merge deconflict
        ## parse output from merge
        ## look for "CONFLICT (content): Merge conflict in <file name>"
        ## deconflict each conflicted file
        ## commit(authorlist = , m="Merging brach " + transmitting)
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
        f.writelines()
    return None


def random_git_log(names=None, numauthors=10, numfiles=10, numbranches=3, numcommits=100, mergefrequency=5):
    if names is None:
        names = loadnames()
    make_gitignore()
    git_init()
    authorlist = random_authors(names, num=numauthors)  # get some random authors
    branches = [random_string(l=5, u=10) for b in range(numbranches)]  # create branch list
    files = []
    for i in range(numfiles):
        current_branch = random.choice(branches)  # randomly choose which branch will be edited
        new_branch(current_branch)
        checkout_branch(current_branch)
        newfn = new_file()  # make and modify files randomly
        files = files + [newfn]  # keep a running list of file names
        commit(authorlist=authorlist)  # randomly choose an author to commit the changes
    for i in range(numcommits):
        current_branch = random.choice(branches)
        checkout_branch(current_branch)
        for f in random.sample(files, random.randint(1,len(files))):
            modify_file(fn=f)
        commit(authorlist=authorlist)
    ## every mergefrequency, merge the current branch into main and deconflict
    return None


def git_init():
    if not os.path.exists(".git"):
        os.system("git init")
    # TODO: check main branch name
    os.system("git branch -m main")
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


if __name__ == "__main__":
    names = loadnames()
    random_string()
    random_authors(names, num=10)
    a = random_content()
    modify_contents(a, num=10)
    a = new_file()
    modify_file(a)
    random_existing_file()
    commit(verbose=True)
    deconflict("temp.txt", resolve="Head", transmitting=None)