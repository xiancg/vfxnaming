@echo off
echo "Make sure you're running this from the project pipenv shell"
IF EXIST ".\dist\*.whl" (
    echo "Removing old wheels from dist."
    del /f /q /s ".\dist\*.whl"
)
IF EXIST ".\dist\*.tar.gz" (
    echo "Removing old source from dist."
    del /f /q /s ".\dist\*.tar.gz"
)
mkdir ".\dist"
echo "Setting up package wheel"
python -m build
echo "Uploading to PyPI"
twine upload dist/* --verbose
echo "Done!"
