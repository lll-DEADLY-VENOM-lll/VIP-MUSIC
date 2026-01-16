#
# Copyright (C) 2024 by THE-VIP-BOY-OP@Github, < https://github.com/THE-VIP-BOY-OP >.
#
# This file is part of < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/THE-VIP-BOY-OP/VIP-MUSIC/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import shlex
from typing import Tuple
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
import config
from ..logging import LOGGER

# --- Loop Error Fix (Python 3.10+) ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return loop.run_until_complete(install_requirements())


def git():
    REPO_LINK = config.UPSTREAM_REPO
    # अगर config में ब्रांच नहीं है तो 'main' को डिफॉल्ट मानें
    BRANCH = config.UPSTREAM_BRANCH if config.UPSTREAM_BRANCH else "main"
    
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO

    try:
        repo = Repo()
        LOGGER(__name__).info(f"Git Client Found [VPS DEPLOYER]")
    except GitCommandError:
        LOGGER(__name__).info(f"Invalid Git Command")
        return
    except InvalidGitRepositoryError:
        repo = Repo.init()
        if "origin" in repo.remotes:
            origin = repo.remote("origin")
        else:
            origin = repo.create_remote("origin", UPSTREAM_REPO)
        
        # यहाँ चेक किया जा रहा है कि कौन सी ब्रांच मौजूद है
        origin.fetch()
        try:
            repo.create_head(BRANCH, origin.refs[BRANCH])
        except Exception:
            BRANCH = "main" # अगर master फेल हुआ तो main ट्राई करें
            repo.create_head(BRANCH, origin.refs[BRANCH])
            
        repo.heads[BRANCH].set_tracking_branch(origin.refs[BRANCH])
        repo.heads[BRANCH].checkout(True)

    try:
        nrs = repo.remote("origin")
    except Exception:
        nrs = repo.create_remote("origin", UPSTREAM_REPO)

    # --- यहाँ मुख्य सुधार है (Branch Fetch Fix) ---
    try:
        nrs.fetch(BRANCH)
    except Exception as e:
        LOGGER(__name__).error(f"Fetch failed for {BRANCH}. Trying 'main' branch...")
        BRANCH = "main"
        try:
            nrs.fetch(BRANCH)
        except Exception as final_err:
            LOGGER(__name__).error(f"Update failed: {final_err}. Starting bot without update.")
            return

    try:
        nrs.pull(BRANCH)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    
    install_req("pip3 install --no-cache-dir -r requirements.txt")
    LOGGER(__name__).info(f"Fetched Updates from: {REPO_LINK}")
