#!/bin/bash

cd /home/ed/Projects/linkypedia/linkypedia
source /etc/apache2/virtualenv2/bin/activate
./manage.py stats
touch stats-last
