import sql_utils as su
import utils as u
import mysql.connector

DB = mysql.connector.connect(
  host="localhost",
  user="prestashop",
  password="batmankill2404",
  database="prestashop"
)
CURSOR = DB.cursor()
su.modify_tables(CURSOR)


"""
1. Get unprocessed products
2. For each product in unprocessed:
    a. 
2. Find all similar products in unprocessed products
3. Check if there is mother? If not create one
4. Move all unprocessed products to combinations and mark them inactive in main

"""

records_to_process = su.get_products_to_process(CURSOR)
for r in records_to_process:
    if (r.id_product not in [2, 21]): continue
    print(r)
    mother = su.find_mother_for_product(CURSOR, r)
    if mother is None:
        siblings = su.find_siblings_for_product(CURSOR, r)
        print(f'    Siblings found: {siblings}')
        if len(siblings) == 0:
            #su.set_product_proc_status(CURSOR, r.id_product, su.ProcStatus.UNIQUE)
            pass
        else:
            grouped_attribute_refs, _ = u.group_refs_by_order(siblings)
            head_ref = u.get_head_ref_from_grouped_refs(grouped_attribute_refs)
            head_name = u.find_most_common_name_part(siblings)
            #TODO - Create mother and merge them
    else:
        print(f'    Mother found: {mother}')
        #su.merge_product_to_mother(CURSOR, r, mother)
        #su.mark_product_as_inactive(CURSOR, r.id_product)
        #su.set_product_proc_status(CURSOR, r.id_product, su.ProcStatus.PROCESSED)
