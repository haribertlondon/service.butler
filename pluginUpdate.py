import git #pip install GitPython
import pluginKodi
import os
import time


def gitupdate():
    repo = git.Repo('.')
    msg1 = repo.git.reset('--hard','origin/master')
    # blast any current changes
    msg2 = repo.git.reset('--hard')
    # ensure master is checked out
    msg3 = repo.heads.master.checkout()
    # blast any changes there (only if it wasn't checked out)
    msg4 = repo.git.reset('--hard')
    # remove any extra non-tracked files (.pyc, etc)
    msg5 = repo.git.clean('-xdf')
    # pull in the changes from from the remote
    msg6 = repo.remotes.origin.pull()
    #b = g.
    print(msg1)
    print(msg2)
    print(msg3)
    print(msg4)
    print(msg5) 
    print(msg6)
    
    print("Updated")
    
def performUpdate():
    a = pluginKodi.kodiShowMessage("Starting Update from server...")
    print(a)
    gitupdate()
    time.sleep(2)
    a = pluginKodi.kodiShowMessage("Rebooting system in 10 sec")
    print(a)
    time.sleep(10)
    print("Rebooting system")
    os.system('systemctl reboot -i')
    
if __name__ == "__main__":
    performUpdate()