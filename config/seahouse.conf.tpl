[keys]
googlemaps_key =

[directories]
ahn.units_dir = data/ahn/units/
json.data_dir = data/json/

[postgres]
host = localhost
port = 5432
user =
password =
name = seahouse

# This will be automatically filed with the values above
sqlalchemy.url = postgres://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s
