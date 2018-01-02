#Option to download via git is commented out. Pyinstaller is automatically installed. Distribution script is also commented out.
#You can install pip manually using the script get-pip.py or uncomment the line for setting it up in this file.

#get-pip.py
pip install stopit
pip install pyzmail
#pip install git+https://github.com/nwcell/psycopg2-windows.git@win32-py27#egg=psycopg2
pip install https://github.com/nwcell/psycopg2-windows/archive/master.zip
pip install pycrypto
pip install rpyc
pip install python-bitcoinrpc
pip install requests
#pip install -U requests[security]
pip install Pillow
pip install stepic
pip install tendo
pip install goslate
#pip install -e git+https://github.com/jgarzik/python-bitcoinrpc.git#egg=hyde
pip install https://github.com/pyinstaller/pyinstaller/archive/master.zip
pip install pypiwin32
pip install requesocks
pip install yandex.translate
pip install pympler

#Halo Distro if desired
pip install https://github.com/pyinstaller/pyinstaller/archive/develop.zip
#pyinstaller BitMHalo.py -wF --icon=BitMHalo.ico --uac-admin
#pyinstaller Halo.py --onefile --icon=BitHalo.ico --uac-admin
