echo [$(date)]: "START"
echo [$(date)]: "deleting existing dist files"
rm -r dist
echo [$(date)]: "deleting existing build files"
rm -r build 
echo [$(date)]: "activate env"
source activate ./env
echo [$(date)]: "intalling setup script"
python setup.py install
echo [$(date)]: "Pushing package to pypi..."
python setup.py sdist bdist_wheel
echo [$(date)]: "Checking dist directory"
twine check dist/*
echo [$(date)]: "Final upload to pypi..."
twine upload --repository-url https://upload.pypi.org/legacy/ dist/* -u Hrisikesh -p pypi#hrisikesh_neogi
echo [$(date)]: "END"