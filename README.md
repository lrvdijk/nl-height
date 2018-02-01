Visualising the height of the Netherlands
=========================================

This project generates "evelation profiles" through horizontal cuts of the 
Netherlands. The visualisation can be found here:

https://lucasvandijk.nl/2018/01/visualising-the-height-of-the-netherlands/

Authors
-------

* Lucas van Dijk
* Dorus Leliveld (@Tclv)

This project was created as part of the course Data Visualisation at Delft 
University of Technology.

Requirements
-------------

### Visualisation itself

* Node.JS
* CoffeeScript
* Gulp + several plugins

### Data preprocessing

* Python >= 3.4
* PostgreSQL >= 9.3
* PostGIS >= 2.1

**Python Packages:**

* geopy
* psycopg2
* SQLAlchemy
* Geoalchemy2
* Shapely
* requests
* clint
* python-slugify


Installation
------------

### Getting the code

1. Create a virtual environment

        $ pyvenv nl-height
        $ cd nl-height

2. Activate the environment

        $ source bin/activate

3. Clone the repository

        $ git clone https://github.com/lrvdijk/nl-height

4. Install Python requirements

        $ cd nl-height
        $ pip install -r requirements.txt

5. Install Node.JS requirements

        $ npm install

*NB*: Most of the code has been written about two years ago, I did not update 
to the latest and shiniest method for keeping track of NPM packages, JS build 
systems, etc.

### Data preprocessing

1. Create a new PostgreSQL database, with PostGIS extension

        $ createdb nlheight
        $ psql -d nlheight
        psql> CREATE EXTENSION postgis;

2. Enter your database configuration

        $ cp config/seahouse.conf.tpl config/seahouse.conf
        $ vim config/seahouse.conf

2. Load AHN units shapefile into the database

        $ cd data/ahn/
        $ psql -d nlheight -f ahn_units.sql

3. Convert lo_x en lo_y columns to integer

        $ psql -d seahouse
        psql> ALTER TABLE ahn_units ALTER COLUMN lo_x TYPE integer USING
        lo_x::integer;
        psql> ALTER TABLE ahn_units ALTER COLUMN lo_y TYPE integer USING
        lo_y::integer;

4. Download all AHN datasets

        $ cd ../../
        $ python python/ahn-downloader.py

5. Extract all AHN zipfiles

        $ python python/ahn-extractor.py

6. Load AHN raster data into the database

        $ cd data/ahn/units/
        $ raster2pgsql -s 28992 -I -M -F -C -t 50x50 ahn2_5_*.tif ahn_raster > raster_data.sql
        $ psql -d nlheight -f raster_data.sql

7. Generate elevation profiles for a given location. Repeat this step for 
   multiple locations.

        $ cd ../../../
        $ python python/dataset-gen.py Delft


Development Server
------------------

1. Run gulp, includes a file watcher with automatic reload

        $ gulp
