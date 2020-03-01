import os
import glob
from pymongo import MongoClient
import ipaddress
from bson.int64 import Int64

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://root:root@localhost:27017/blocked?authMechanism=DEFAULT&authSource=admin')
MONGODB_IMPORT_COLLECTION = os.getenv('MONGODB_IMPORT_COLLECTION', 'blocked_new')
MONGODB_PROD_COLLECTION = os.getenv('MONGODB_PROD_COLLECTION', 'blocked')
IMPORT_DIR = os.getenv('IMPORT_DIR', '../data/archive/utf8')


def import_file(filename):
    mongodb_client = MongoClient(MONGODB_URI)
    db = mongodb_client.get_database()
    blocked = db.get_collection(MONGODB_IMPORT_COLLECTION)
    with open(filename, 'r') as csv_file:
        lines = csv_file.readlines()
        inserts = []
        inserted = 0
        for line in lines:
            components = line.strip().split(';')
            if len(components) < 6:
                continue

            ips = components[0].split(' | ')
            domain = components[1]
            url = components[2].strip('"')
            decision_org = components[3]
            decision_num = components[4]
            decision_date = components[5]

            if domain.strip() == '':
                domain = None

            if url.strip() == '' or url == 'http://' or url == 'https://':
                url = None

            for ip in ips:
                if ip.strip() == '':
                    if domain is not None and len(domain.split('.')) == 4:
                        ip = domain
                    else:
                        ip = None

                ip_first = None
                ip_last = None
                length = None
                if ip is not None:
                    pair = ip.split('/')
                    ip_first = ipaddress.ip_address(pair[0])
                    # Skip ipv6.
                    if ip_first.version == 6:
                        continue
                    ip_first = Int64(ip_first)
                    if len(pair) > 1:
                        length = int(pair[1])
                        ip_last = ip_first | (1 << (32 - length)) - 1
                    else:
                        length = 32
                        ip_last = ip_first

                inserts.append({
                    'ip': ip,
                    'ip_first': ip_first,
                    'ip_last': ip_last,
                    'length': length,
                    'decision_date': decision_date,
                    'decision_org': decision_org,
                    'decision_num': decision_num,
                    'domain': domain,
                    'url': url,
                })
                if len(inserts) == 10000:
                    result = blocked.insert_many(inserts)
                    result.inserted_ids
                    inserted += len(inserts)
                    inserts = []
                    pass

        if len(inserts) > 0:
            result = blocked.insert_many(inserts)
            result.inserted_ids
            inserted += len(inserts)
            pass


if __name__ == '__main__':
    files = [f for f in glob.glob(IMPORT_DIR + "/*.csv")]
    for f in files:
        basename = os.path.basename(f)
        print(f'Importing {basename} file...')
        import_file(f)

    # @todo Run health check somewhere...?
    mongodb_client = MongoClient(MONGODB_URI)
    db = mongodb_client.get_database()
    try:
        # Try to drop temporary collection.
        blocked_tmp = db.get_collection(f'~{MONGODB_PROD_COLLECTION}')
        blocked_tmp.drop()
    except Exception as err:
        print(err)
    try:
        # Try to rename current collection.
        blocked = db.get_collection(MONGODB_PROD_COLLECTION)
        blocked.rename(f'~{MONGODB_PROD_COLLECTION}')
    except Exception as err:
        print(err)
    blocked_new = db.get_collection(MONGODB_IMPORT_COLLECTION)
    blocked_new.create_index('domain')
    blocked_new.create_index('ip')
    blocked_new.create_index('url')
    blocked_new.rename(MONGODB_PROD_COLLECTION)
