#!/bin/bash
repositories="adm bi cesaf common core corregedoria edocs esocial judicial planejamento raf rh web"
core_dirs="app auditoria auth contrib default engine ged standard static urls workflow"

files=(settings.py tester.py install.py syncdb.py install-with-venvwrapper.py sysinfo.json celeryconf.py)

core_excludes=()
for file in "${files[@]}"
do
    core_excludes+=(--exclude "$file")
done

for repo in $repositories
do
    rm -fr tmp
    git clone ssh://git@gitlab.mpto.mp.br:3022/mpto/$repo.git tmp -b port-py37
    mkdir tmp
    rm -fr tmp/.git
    rm tmp/.gitignore
    if [ $repo == "core" ]; then
        for dir in $core_dirs
        do
            rsync -av "${core_excludes[@]}" tmp/$dir/ $dir/
        done
    else
        rsync -av tmp/ $repo
    fi

done
rm -fr tmp
rm -fr core