#!/bin/bash

cd /home/ed/Projects/linkypedia/linkypedia
source /etc/apache2/virtualenv/bin/activate
./manage.py stats
