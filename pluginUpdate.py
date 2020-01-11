import git #pip install GitPython


def update():
#  #  empty_repo = git.Repo.init(".")
#  #  empty_repo.
#  #  origin = empty_repo.create_remote('origin', "https://github.com/haribertlondon/service.butler")
#  #  assert origin.exists()
#  #  assert origin == empty_repo.remotes.origin == empty_repo.remotes['origin']
#  #  origin.fetch()                  # assure we actually have data. fetch() returns useful information
#  #  # Setup a local tracking branch of a remote branch
#  #  empty_repo.create_head('master', origin.refs.master)  # create local branch "master" from remote "master"
#  #  empty_repo.heads.master.set_tracking_branch(origin.refs.master)  # set local "master" to track remote "master
#  #  empty_repo.heads.master.checkout()  # checkout local "master" to working tree
#  #  # Three above commands in one:
#  #  empty_repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master).checkout()
#  #  # rename remotes
#  #  origin.rename('new_origin')
#  #  # push and pull behaves similarly to `git push|pull`
#  #  origin.pull()
#  #  origin.push()
    # assert not empty_repo.delete_remote(origin).exists()     # create and delete remotes
    print("Start update")
#    repo = git.Repo('.')
#    print(repo)
#    o = repo.remotes.master    
#    print(o)
#    o.pull()
    repo = git.Git('.')
    # blast any current changes
    msg1 = repo.git.reset('--hard')
    # ensure master is checked out
    msg2 = repo.heads.master.checkout()
    # blast any changes there (only if it wasn't checked out)
    msg3= repo.git.reset('--hard')
    # remove any extra non-tracked files (.pyc, etc)
    msg4 = repo.git.clean('-xdf')
    # pull in the changes from from the remote
    msg5 = repo.remotes.origin.pull()
    #b = g.
    print(msg1)
    print(msg2)
    print(msg3)
    print(msg4)
    print(msg5) 
    
    print("Updated")
    
if __name__ == "__main__":
    update()