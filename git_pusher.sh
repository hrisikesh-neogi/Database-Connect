echo [$(date)]: "git init"
git init
echo [$(date)]: "add files"
git add . 
echo [$(date)]: "git commit"
git commit -m "version 0.1.6.1"
echo [$(date)]: "git push"
git push
echo [$(date)]: "END"

