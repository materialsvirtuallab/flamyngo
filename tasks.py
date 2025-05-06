# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

"""
Deployment file to facilitate releases.
Note that this file is meant to be run from the root directory.
"""

from __future__ import annotations

import json
import os
import re

import requests
from invoke import task

from flamyngo import __version__ as ver


@task
def publish(ctx):
    ctx.run("rm dist/*.*", warn=True)
    ctx.run("python setup.py sdist bdist_wheel")
    ctx.run("twine upload dist/*")


@task
def setver(ctx):
    ctx.run(f'sed s/version=.*,/version=\\"{ver}\\",/ setup.py > newsetup')
    ctx.run("mv newsetup setup.py")


@task
def merge_stable(ctx):
    ctx.run("git add .")
    ctx.run(f'git commit -a -m "v{ver} release"')
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
        "tag_name": f"v{ver}",
        "target_commitish": "master",
        "name": f"v{ver}",
        "body": desc,
        "draft": False,
        "prerelease": False,
    }

    response = requests.post(
        "https://api.github.com/repos/materialsvirtuallab/flamyngo/releases",
        data=json.dumps(payload),
        headers={"Authorization": "token " + os.environ["GITHUB_RELEASES_TOKEN"]},
    )
    print(response.text)


@task
def release(ctx, notest=False):
    setver(ctx)
    publish(ctx)
    merge_stable(ctx)
    # update_doc(ctx)
    release_github(ctx)
