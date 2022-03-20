import pandas as pd
import os
import random
import string


names = pd.read_csv("./names.csv")
# names["email"] = names["first"].apply(lambda x: x[0]).str.lower() + names["last"].str.lower() + "@notarealcompany.org"
# names.to_csv("names.csv", index=False)
# names["git"] = names["first"] + " " + names["last"] + " <" + names["email"] + ">"


def random_string(length = None, l=5, u=30):
    if length is None:
        length = random.randint(l, u)
    letters = string.ascii_lowercase
    out = ''.join(random.choice(letters) for i in range(length))
    return out


def commit(author=None, m=None):
    if m is None:
        m = random_string()
    if author is not None:
        os.system("git add .")
        cmd_commit = "git commit -m \"" + m + "\" --author \"" + author + "\""
        os.system(cmd_commit)


def random_authors(names, num = 10):
    return [a for a in random.sample(list(names["git"]), num)]


def random_content(numlines=None, l=5, u=100):
    if numlines is None:
        numlines = random.randint(l, u)
    new_content = [random_string() for i in range(numlines)]
    # new_content = '\n'.join(new_content)
    return new_content


def modify_contents(old_contents, num=10):
    new_contents = old_contents.copy()
    N = len(old_contents)
    ind = [i for i in range(N)]
    ind = random.sample(ind, min(num, N))
    for i in ind:
        new_contents[i] = random_string() + "\n"
    return new_contents


def new_file(fn = None):
    if fn is None:
        fn = random_string() + "." + random_string(l=2, u=3)
    if not os.path.exists(fn):
        new_content = random_content()
        with open(fn, 'w') as f:
            f.writelines(new_content)
    else:
        modify_file(fn=fn)
    return None


def modify_file(fn = None, append = None):
    if append is None:
        append = random.choice([True, False])
    if fn is not None:
        if append:
            new_content = random_content(l=2, u=7)
            with open(fn, 'a') as f:
                f.writelines(new_content)
        else:
            with open('stats.txt', 'r') as file:
                old_content = file.readlines()
            new_content = modify_contents(old_content)
            with open(fn, 'w') as f:
                f.writelines(new_content)
        return None


def random_existing_file():
    prohibited = ['.gitattributes', '.gitignore', '.idea', 'names.csv', 'random-git-log.py']
    file_list = os.listdir()
    file_list = [f for f in file_list if f not in prohibited]
    return random.sample(file_list)


def random_git_log():
    return None

