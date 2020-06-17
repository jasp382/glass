Install GLASS
====================

1 - Clone GLASS repository from github.com:

	mkdir ~/code
	cd ~/code
	git clone https://github.com/jasp382/glass.git

2 - Set PGPASSWORD as environment variable:

	echo "export PGPASSWORD=yourpostgresqlpassword" | sudo tee --append ~/.bashrc
	source ~/.bashrc

4 - Edit /../../glass/glass/cons/con-postgresql.json file according your PostgreSQL configuration;

5 - Replace default osmconf.ini file in your GDAL-DATA configuration folder:

	# For Ubuntu 18.04 and Ubuntu 20
	sudo rm /usr/share/gdal/osmconf.ini
	sudo cp ~/code/glass/conf/osmconf-gdal.ini /usr/share/gdal/osmconf.ini

	# For CentOS
	sudo rm /usr/local/share/gdal/osmconf.ini
	sudo cp ~/code/gasp/conf/osmconf-gdal.ini /usr/local/share/gdal/osmconf.ini

6 - Create Python Virtual Environment for GLASS:

	sudo -H pip3 install virtualenv virtualenvwrapper

    echo "export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3" | sudo tee --append ~/.bashrc
    echo "export WORKON_HOME=~/.virtualenvs" | sudo tee --append ~/.bashrc
	echo "export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv" | sudo tee --append ~/.bashrc
    echo "source /usr/local/bin/virtualenvwrapper.sh" | sudo tee --append ~/.bashrc

    source ~/.bashrc

    mkvirtualenv glassenv

7 - Install glass in the created virtual environment:

    workon glassenv

    cd ~/code/glass && pip install -r requirements.txt

    user="$(whoami)"
    echo "/home/$user/code/glass" | sudo tee ~/.virtualenvs/glassenv/lib/python3.8/site-packages/glass.pth
