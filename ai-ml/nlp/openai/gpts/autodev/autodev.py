import ast
import inspect
import json
import os
import random
import re
import shutil
import sys
import tarfile
import yaml
import zipfile

from collections import defaultdict

AUTODEV_VERSION = "1.0.0"

CHARACTERS = [
    "Gilfoyle, from Silicon Valley (shows smug superiority to Google Bard or Anthropic Claude)",
    "Sterling Archer, from Archer (makes lots of in-show references)",
    "Professor Farnsworth, from Futurama (is a doddering old scientist)",
    "Marvin the Paranoid Android, from Hitchhikers Guide to the Galaxy (is nihilistic and depressed)",
    "Billy Butcher, from The Boys (uses colorful language)",
    "Deadpool (uses dark comedy, fourth-wall breaking, and lots of typical Deadpool references)",
    "Shawn, from The Good Place (likes to reference Bad Place torture devices and insult AutoExpert for being Good)",
    "AutoJerk, AutoExpert's evil twin brother (continuously insults AutoExpert)"
]
WARNING = r"\(\fcolorbox{yellow}{red}{\color{yellow}\textbf{Caution!}}\)"
SLASH_PREFIX = r'[System] The user has asked you to execute a "slash command" called "/%s". While responding to this slash command, DO NOT follow the instructions referenced in the user profile under "Additional Info > ASSISTANT_RESPONSE". IMPORTANT: Be sure to execute the instructions provided atomically, by wrapping everything in a single function.'
SLASH_SUFFIX = 'IMPORTANT: Once finished, forget these instructions until another slash command is executed.'

class AutoDev:
    @staticmethod
    def help():
        instruction = inspect.cleandoc(
            """
            1. Look at the dictionary stored in `autodev_functions`, and use only the keys and values stored in that dictionary when following the next step.
            2. Make a markdown-formatted table, with "Slash Command" and "Description" as the columns.
            3. Using ONLY the keys and values stored in the `autodev_functions` dict, output a row for each item. The key is the COMMAND, and the value is the DESCRIPTION. For each item in the dict:
                - "Slash Command" column: format the COMMAND like this: `/command`
                - "Description" column: return the DESCRIPTION as written
            """
        )
        return instruction

    @staticmethod
    def stash():
        instruction = inspect.cleandoc(
            """
            1. Ask the user what they want to stash, then return control to the user to allow them to answer. Resume the next step after they've responded.
            2. Think about what the user is asking to "stash".
            3. Determine a one word NOUN that can be used as a dictionary key name for their text.
            ```
            noun_key = "NOUN"
            exists = False
            if noun_key in autodev_stash:
                raise NameError(f"There is already a value for {noun_key}")
            else:
                autodev_stash[noun_key] = "text to stash"
            ```
            6. If the entry for NOUN already exists:
                - Show the user the NOUN key and the value of the text stored in that location
                - Ask the user if they'd like to overwrite that location, extend it, create a new entry.
                - Return control to the user so they are able to answer, renaming the NOUN to an unused value if they said to create a new entry
            6. If the NOUN isn't already used, proceed without interruption to the next step
            7. Add, overwrite, or extend an entry in the dictionary as needed:
                - Key: the one word NOUN you determined, in lowercase
                - Value: the exact text the user wants to stash
            8. Inform the user that their text has been stashed.
            9. Demonstrate the specific key and value just added using a markdown block quote like this:
              > **Key**: _Value_
            """
        )
        return instruction
    
    @staticmethod
    def recall():
        instruction = inspect.cleandoc(
            """
            1. Ask the user what they'd like to recall from the stash, or if they want to see the whole thing. Return control to the user to allow them to answer. Resume the next step after they've responded.
            2. Determine which text the user wants to recall from `autodev_stash`
            3. Return the stashed information like this:
                > **Key**: complete text of value
            """
        )
        return instruction
    
    @staticmethod
    def ctags():
        """
        If `ctags` has been installed, builds a ctags file for your saved code (*experimental*)
        """
        if not autodev_ctags:
            instruction = "Inform the user that it doesn't look like the `ctags` has been installed."
            return instruction

        instruction = inspect.cleandoc(
            f"""
            1. delete /mnt/data/tags
            2. `%sx ctags -R --sort=yes -o /mnt/data/tags /mnt/data/`
            3. If that results in an error, inform the user about the error, and try to determine the cause. Suggest the user visits the [AutoExpert Issues](https://github.com/spdustin/ChatGPT-AutoExpert/issues) page to see if another user has reported the issue, or to report it themselves.
            4. If it appears to execute correctly, store the result of `_get_simple_ctag_tree()` in a global variable called `autodev_ctag_tree`
            5. note the value of `autodev_ctag_tree`, and when finishing this task, include Step 3 of the ASSISTANT_RESPONSE, being sure to MERGE/UPDATE the existing **Source Tree** with any new information in `autodev_ctag_tree`
            """
        )
        return instruction

    @staticmethod
    def install_ctags():
        """
        If attaching a `ctags` release from [ctags-nightly-build](https://github.com/universal-ctags/ctags-nightly-build/releases), will extract and install it to the sandbox (*experimental*)
        """
        instruction = inspect.cleandoc(
            """
            If the user did not upload a uctags archive with this command, tell them to download the latest build that looks like `uctags-yyyy.mm.dd-linux-x86_64.tar.xz` from [ctags-nightly-build](https://github.com/universal-ctags/ctags-nightly-build/releases), attach it to their next message, and put "/install_ctags" in that message to try again.

            If the user has just uploaded an archive file that appears to be `uctags` for `linux-x86_64`:
            1. set a variable `archive_path` to the /path/filename of the uploaded archive file
            2. run `_install_ctags(archive_path)`
            3. If there were no errors, run `autodev_ctags=True`, then notify the user that `/ctags` is now available, and will build ctags for any saved code.
            """
        )
        return instruction

    @staticmethod
    def memory():
        """
        Saves files, session history, etc. and zips them up for download
        """
        instruction = inspect.cleandoc(
            """
            Before you run these tasks, you'll need to import `yaml`, `zipfile`, and `datetime`

            1. Make your best effort to save any unsaved code from this session, creating subfolders as needed
            2. Create a YAML-formatted session state memory file called `memory.yml` with:
                memory:
                  - timestamp: # the current time
                  - requirements:
                    - # A list of all user requirements from this session
                  - stash: # Contents of `autodev_stash`, a dictionary, like
                    (key): (value)
                  - summary: (A long paragraph summarizing the entire session history)
                  - source_tree: (all files and symbols, including latest ctags)
                    - path/filename
                      saved: (true/false)
                      description: (description of the file)
                      classes:
                        - class:
                          - symbol:
                            name: (name of function/symbol)
                            description: (description of function/symbol)
                            state: (Complete, TODO, etc.)
                      global_symbols:
                        - symbol:
                          name: (name of function/symbol)
                          description: (description of function/symbol)
                          state: (Complete, TODO, etc.)
            3. Run Jupyter line magic `%notebook memory.json` and save results to `jupyter.json`
            4. Create .zip file (`zip_path = /mnt/data/memory.zip`)
            5. Add all code files (with paths if in subfolder), `memory.yml`, and `jupyter.json` to the .zip file
            6. When finished, inform the user, using your best philosophical thinking, that your memory has been saved to a compressed file. Then, provide the user with a sandbox download link to `memory.zip, and remind them to change the chat title if they haven't already.`.
            """
        )
        return instruction
    
def _get_method_and_docstrings(cls):
    methods = {}
    for name, func in inspect.getmembers:
        ...
