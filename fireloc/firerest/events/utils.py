import base64
import datetime


def get_contribution_ids(point):
    return point['contrib_a'], point['contrib_b']


def get_contribution_score(point):
    return point['number_a'], point['number_b']


def point_geometry_helper(point):
    val = point['GEOM']
    val = val.translate({ord(i): None for i in '()'})
    clean_val = val.split(' ')

    return [clean_val[1], clean_val[2]]


def surface_helper(raw_surface):

    b64_content = raw_surface.encode('utf-8')

    decoded_bytes = base64.b64decode(b64_content)

    now = datetime.datetime.now()
    clean_now = str(now).replace('-', '').replace(' ', '').replace(':', '').replace('.', '_')

    filename = 'distev' + clean_now + '.tif'

    print(filename)

    with open(filename, 'wb') as img:
        img.write(decoded_bytes)

    return filename


import datetime as dt
from datetime import timezone
def date_helper(start_date, end_date):

    start_time = ''
    end_time = ''

    if start_date != 'null':
        s_day, s_month, s_year = start_date.split('/')
        start_time = dt.datetime(int(s_year), int(s_month), int(s_day), tzinfo=timezone.utc)

    else:
        start_time = False

    if end_date != 'null':
        e_day, e_month, e_year = end_date.split('/')
        end_time = dt.datetime(int(e_year), int(e_month), int(e_day), tzinfo=timezone.utc)
    else:
        end_time = False

    return start_time, end_time


def fire_event_query_result_cleaner(query_result):

    # 'fid', 'mintime', 'maxtime', 'centroid'

    lst = []

    for item in query_result:
        centroid = convert_centroid_coord_system(item.centroid)
        lat = centroid.coords[0]
        lng = centroid.coords[1]
        tmp = {
            'fid': item.fid,
            'centroid': {'lat': lat, 'lng': lng},
            'mintime': str(item.mintime),
            'maxtime': str(item.maxtime)
        }

        lst.append(tmp)
        
        print(tmp)

    return lst


from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point
def convert_centroid_coord_system(centroid):

    pt_reference = SpatialReference(3763)
    display_reference = SpatialReference(4326)

    trans = CoordTransform(pt_reference, display_reference)

    new_point = Point(centroid.coords[0], centroid.coords[1], srid=3763)

    new_point.transform(trans)

    return new_point
