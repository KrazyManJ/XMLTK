set /p token=<token.txt
cd ..
twine upload dist/* -u __token__ -p %token%