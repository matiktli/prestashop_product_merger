import sql_utils as su
import utils as u
import mysql.connector
import model as m
import csv
from datetime import datetime
import time

DB = mysql.connector.connect(
  host="localhost",
  user="prestashop",
  password="batmankill2404",
  database="prestashop"
)
DB.autocommit = False
CURSOR = DB.cursor()
su.db_init(CURSOR, db=DB)

"""
1. Get unprocessed products
2. For each product in unprocessed:
    a. 
2. Find all similar products in unprocessed products
3. Check if there is mother? If not create one
4. Move all unprocessed products to combinations and mark them inactive in main

"""

START = datetime.now()

def log(product_id, message, depth=0, depth_marker='--'):
    msg_values = (product_id, message, depth)
    with open(f'logs_{str(START.timestamp())}.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([*msg_values])
        msg_str = f'[{msg_values[0]}]'+(''.join([depth_marker for _ in range(0, depth)]))+f'{msg_values[1]}'
        print(msg_str)

LIMIT=100

records_to_process = su.get_products_to_process(CURSOR, limit=None, ids=[1000])
seen = set() # tmp, idk why doubles the records
for r in records_to_process:
    if len(seen) == LIMIT: break
    try:
        if r.id_product in seen: continue
        seen.add(r.id_product)
        log(r.id_product, f'Processing: {r}', depth=0)
        mother = su.find_mother_for_product(CURSOR, r)
        if mother is None:
            siblings = su.find_siblings_for_product(CURSOR, r)
            log(r.id_product, f'Mother NOT found. Will try to find siblings', depth=1)
            if len(siblings) == 0:
                su.set_products_proc_status(CURSOR, [r.id_product], m.ProcStatus.UNIQUE)
                log(r.id_product, f'Siblings NOT found. Marking as UNIQUE.', depth=2)
                pass
            else:
                log(r.id_product, f'Siblings found: {len(siblings)}. {[p.id_product for p in siblings]}', depth=2)
                grouped_attribute_refs = u.group_refs_by_order(siblings+ [r])
                grouped_attribute_names = u.group_names_by_order(siblings + [r])

                head_ref = u.get_head_ref_from_grouped_refs(grouped_attribute_refs)
                head_name = u.get_head_name_from_grouped_names(grouped_attribute_names)

                mapped_refs_and_names = u.map_attribute_refs_to_names(grouped_attribute_refs, grouped_attribute_names)

                mother_product = u.prepare_mother_object(r, head_name, head_ref, mapped_refs_and_names, siblings=siblings)
                mother_id = su.save_mother(CURSOR, mother_product)
                mother_product.id_product = mother_id
                log(r.id_product, f'Mother created with id: {mother_product.id_product}', depth=3)

                su.save_combinations(CURSOR, mother_product, source=r, siblings=siblings, mappings=mapped_refs_and_names)
                su.save_price_data(CURSOR, mother_product, r)
                for pp in siblings + [r]:
                    su.mark_products_as_inactive(CURSOR, [pp.id_product])
                    su.set_products_proc_status(CURSOR, [pp.id_product], m.ProcStatus.PROCESSED)
                log(r.id_product, f'Combinations created, children marked as inactive len: {len(siblings + [r])}', depth=3)
        else:
            log(r.id_product, f'--Mother found with id: {mother.id_product} :WIP: [here will merge with mother]', depth=1)
            continue #raise Exception("IN IMPLEMENTATION --Mother found, merge now")
            su.merge_product_to_mother(CURSOR, r, mother)
            su.mark_products_as_inactive(CURSOR, [r.id_product])
            su.set_products_proc_status(CURSOR, [r.id_product], m.ProcStatus.PROCESSED)
    except Exception as ex:
        DB.rollback()
        raise ex #tmp
        log(r.id_product, f'\n[Error while processing record with id: {r.id_product}]. {ex}', depth=0)

STOP = datetime.now()
print(f'Time taken for {LIMIT} records: {str(STOP-START)}.')
revert = input('Do you want to commit[Yes/No]: ')
DB.commit() if revert in ['Yes', 'True'] else DB.rollback()