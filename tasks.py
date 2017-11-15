# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

"""
Deployment file to facilitate releases.
Note that this file is meant to be run from the root directory.
"""
import glob
import os
import json
import webbrowser
import requests
import re
import subprocess
from invoke import task

from monty.os import cd
from flamyngo import __version__ as ver


# @task
# def make_doc(ctx):
#     with open("CHANGES.rst") as f:
#         contents = f.read()
#
#     toks = re.split("\-{3,}", contents)
#     n = len(toks[0].split()[-1])
#     changes = [toks[0]]
#     changes.append("\n" + "\n".join(toks[1].strip().split("\n")[0:-1]))
#     changes = ("-" * n).join(changes)
#
#     with open("docs/latest_changes.rst", "w") as f:
#         f.write(changes)
#
#     with cd("examples"):
#         ctx.run("jupyter nbconvert --to html *.ipynb")
#         ctx.run("mv *.html ../docs/_static")
#     with cd("docs"):
#         ctx.run("cp ../CHANGES.rst change_log.rst")
#         ctx.run("sphinx-apidoc -d 6 -o . -f ../pymatgen")
#         ctx.run("rm pymatgen.*.tests.rst")
#         for f in glob.glob("docs/*.rst"):
#             if f.startswith('docs/pymatgen') and f.endswith('rst'):
#                 newoutput = []
#                 suboutput = []
#                 subpackage = False
#                 with open(f, 'r') as fid:
#                     for line in fid:
#                         clean = line.strip()
#                         if clean == "Subpackages":
#                             subpackage = True
#                         if not subpackage and not clean.endswith("tests"):
#                             newoutput.append(line)
#                         else:
#                             if not clean.endswith("tests"):
#                                 suboutput.append(line)
#                             if clean.startswith("pymatgen") and not clean.endswith("tests"):
#                                 newoutput.extend(suboutput)
#                                 subpackage = False
#                                 suboutput = []
#
#                 with open(f, 'w') as fid:
#                     fid.write("".join(newoutput))
#         ctx.run("make html")
#         ctx.run("cp _static/* _build/html/_static")
#
#         #This makes sure pymatgen.org works to redirect to the Gihub page
#         ctx.run("echo \"pymatgen.org\" > _build/html/CNAME")
#         #Avoid ths use of jekyll so that _dir works as intended.
#         ctx.run("touch _build/html/.nojekyll")


@task
def publish(ctx):
    ctx.run("rm dist/*.*", warn=True)
    ctx.run("python setup.py register sdist bdist_wheel")
    ctx.run("twine upload dist/*")


@task
def setver(ctx):
    ctx.run("sed s/version=.*,/version=\\\"{}\\\",/ setup.py > newsetup"
          .format(ver))
    ctx.run("mv newsetup setup.py")


@task
def merge_stable(ctx):
    ctx.run("git add .")
    ctx.run("git commit -a -m \"v%s release\"" % ver)
    ctx.run("git push")
    # ctx.run("git checkout stable")
    # ctx.run("git pull")
    # ctx.run("git merge master")
    # ctx.run("git push")
    # ctx.run("git checkout master")


@task
def release_github(ctx):
    with open("CHANGES.rst") as f:
        contents = f.read()
    toks = re.split("\-+", contents)
    desc = toks[1].strip()
    toks = desc.split("\n")
    desc = "\n".join(toks[:-1]).strip()
    payload = {
        "tag_name": "v" + ver,
        "target_commitish": "master",
        "name": "v" + ver,
        "body": desc,
        "draft": False,
        "prerelease": False
    }
    response = requests.post(
        "https://api.github.com/repos/materialsvirtuallab/flamyngo/releases",
        data=json.dumps(payload),
        headers={"Authorization": "token " + os.environ["GITHUB_RELEASES_TOKEN"]})
    print(response.text)


@task
def release(ctx, notest=False):
    setver(ctx)
    if not notest:
        ctx.run("nosetests")
    publish(ctx)
    merge_stable(ctx)
    # update_doc(ctx)
    release_github(ctx)
