import pandas as pd
import os
import random
import string


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


def commit(author=None, m=None, system_call=False, verbose=False):
    if m is None:
        m = random_string()
    if author is None:
        names = loadnames()
        author = random_authors(names, num=1)
        author = author[0]
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


def branch(name=None):
    cmdnew = "git branch " + name
    cmdcheckout = "git checkout " + name
    os.system(cmdnew)
    os.system(cmdcheckout)
    return None


def merge(receiving=None, transmitting=None):
    if (receiving is not None) & (transmitting is not None):
        os.system("git checkout " + receiving)
        os.system("git merge --no-ff " + transmitting)
        # merge deconflict
        ## parse output from merge
        ## look for "CONFLICT (content): Merge conflict in <file name>"
    return None


def deconflict(fn):
    # place holder
    # current branch begins "<<<<<<< HEAD"
    # sep and transmitting branch begins "======="
    # conflict ends with ">>>>>>> <transmitting branch name>
    # allow randomly choosing which to accept
    # then run commit() again with m = "Merging brach <branch name>"
    return None


def random_git_log(names=None, numauthors=10, numbranches=3, numcommits=100, mergefrequency=5):
    if names is None:
        names = loadnames()
    # get some random authors
    # make and modify files randomly
    # randomly choose an author to commit the changes
    # randomly choose which branch will be edited
    # every mergefrequency, merge the current branch into main and deconflict
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