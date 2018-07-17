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


@task
def release_github(ctx):
    with open("CHANGES.md") as f:
        contents = f.read()
    toks = re.split("##", contents)
    desc = toks[1].strip()
    toks = desc.split("\n")
    desc = "\n".join(toks[1:]).strip()
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
