import asyncio
import shlex
from typing import Tuple
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
import config
from ..logging import LOGGER

# --- Loop Error Fix ---
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
    # हमने अपडेट वाले फंक्शन को आसान बना दिया है ताकि बोट क्रैश न हो
    try:
        repo = Repo()
        LOGGER(__name__).info(f"Git Client Found. Skipping auto-update to avoid errors.")
    except Exception:
        repo = Repo.init()
        LOGGER(__name__).info(f"Git Initialized.")
    
    # आवश्यकताओं (requirements) को इंस्टॉल करना जारी रखें
    try:
        install_req("pip3 install --no-cache-dir -r requirements.txt")
        LOGGER(__name__).info(f"Requirements checked and installed.")
    except Exception as e:
        LOGGER(__name__).error(f"Requirement installation failed: {str(e)}")
