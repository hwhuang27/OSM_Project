# Extract Spark-style JSON from planet.osm data.
# Typical invocation:
# spark-submit osm-amenities.py /courses/datasets/openstreetmaps amenities

import sys
assert sys.version_info >= (3, 5) # make sure we have Python 3.5+

from pyspark.sql import SparkSession, functions, types, Row
spark = SparkSession.builder.appName('OSM point of interest extracter').getOrCreate()
assert spark.version >= '2.4' # make sure we have Spark 2.4+
spark.sparkContext.setLogLevel('WARN')
sc = spark.sparkContext
spark.conf.set("spark.sql.session.timeZone", "UTC")

from lxml import etree
import dateutil.parser
#import datetime


amenity_schema = types.StructType([
    types.StructField('lat', types.DoubleType(), nullable=False),
    types.StructField('lon', types.DoubleType(), nullable=False),
    types.StructField('unix_time', types.DoubleType(), nullable=False),
    #types.StructField('timestamp', types.TimestampType(), nullable=False),
    types.StructField('amenity', types.StringType(), nullable=False),
    types.StructField('name', types.StringType(), nullable=True),
    types.StructField('tags', types.MapType(types.StringType(), types.StringType()), nullable=False),
])


def get_amenities(line):
    root = etree.fromstring(line)
    if root.tag != 'node':
        return

    tags = {tag.get('k'): tag.get('v') for tag in root.iter('tag')}
    if 'amenity' not in tags:
        return

    lat = float(root.get('lat'))
    lon = float(root.get('lon'))
    # https://stackoverflow.com/q/969285/6871666
    unix_time = dateutil.parser.parse(root.get('timestamp')).timestamp()
    #unix_time = datetime.datetime.strptime(root.get('timestamp'), "%Y-%m-%dT%H:%M:%S%z").timestamp()
    amenity = tags['amenity']
    del tags['amenity']
    if 'name' in tags:
        name = tags['name']
        del tags['name']
    else:
        name = None
    yield Row(lat=lat, lon=lon, unix_time=unix_time, amenity=amenity, name=name, tags=tags)


def main(inputs, output):
    lines = sc.textFile(inputs)
    nodes = lines.flatMap(get_amenities)
    amenities = spark.createDataFrame(nodes, schema=amenity_schema)
    # work around Python to Spark datetime conversion problems
    amenities = amenities.select(
        'lat', 'lon',
        functions.from_unixtime(amenities['unix_time']).alias('timestamp'),
        'amenity', 'name', 'tags'
    )
    amenities = amenities.cache()
    amenities.write.json(output, mode='overwrite', compression='gzip')
    amenities.write.parquet(output + '-parquet', mode='overwrite', compression='lz4')


if __name__ == '__main__':
    inputs = sys.argv[1]
    output = sys.argv[2]
    main(inputs, output)
