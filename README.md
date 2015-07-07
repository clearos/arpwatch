# arpwatch

Forked version of arpwatch with ClearOS changes applied

## Update usage
  Add __#kojibuild__ to commit message to automatically build

* git clone git://github.com/clearos/arpwatch.git
* cd gconsole
* git checkout c7
* git remote add upstream git://git.centos.org/rpms/arpwatch.git
* git pull upstream c7
* git checkout clear7
* git merge --no-commit c7
* git commit
