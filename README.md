# arpwatch

Forked version of arpwatch with ClearOS changes applied

* git clone git+ssh://git@github.com/clearos/arpwatch.git
* cd arpwatch
* git checkout c7
* git remote add upstream git://git.centos.org/rpms/arpwatch.git
* git pull upstream c7
* git checkout clear7
* git merge --no-commit c7
* git commit
