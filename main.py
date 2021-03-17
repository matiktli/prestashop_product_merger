import sql_utils as su
import utils as u
import mysql.connector
import model as m

DB = mysql.connector.connect(
  host="localhost",
  user="prestashop",
  password="batmankill2404",
  database="prestashop"
)
DB.autocommit = True
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

records_to_process = su.get_products_to_process(CURSOR)
for r in records_to_process:
    try:
        if (r.id_product not in [21]): continue
        print(f'Processing: {r}')
        mother = su.find_mother_for_product(CURSOR, r)
        if mother is None:
            siblings = su.find_siblings_for_product(CURSOR, r)
            print(f'--Siblings found: {len(siblings)}')
            if len(siblings) == 0:
                #su.set_product_proc_status(CURSOR, r.id_product, su.ProcStatus.UNIQUE)
                pass
            else:
                grouped_attribute_refs = u.group_refs_by_order(siblings+ [r])
                grouped_attribute_names = u.group_names_by_order(siblings + [r])

                head_ref = u.get_head_ref_from_grouped_refs(grouped_attribute_refs)
                head_name = u.get_head_name_from_grouped_names(grouped_attribute_names)

                mapped_refs_and_names = u.map_attribute_refs_to_names(grouped_attribute_refs, grouped_attribute_names)

                mother_product = u.prepare_mother_object(r, head_name, head_ref, mapped_refs_and_names, siblings=siblings)
                mother_id = su.save_mother(CURSOR, mother_product)
                mother_product.id_product = mother_id
                print(f'--Mother created: {mother_product}')

                su.save_combinations(CURSOR, mother_product, source=r, siblings=siblings, mappings=mapped_refs_and_names)

                for pp in siblings + [r]:
                    print(pp)
                    su.mark_product_as_inactive(CURSOR, pp.id_product)
                    su.set_product_proc_status(CURSOR, pp.id_product, m.ProcStatus.PROCESSED)

                #TODO - Create mother and merge them
        else:
            print(f'--Mother found: {mother}')
            su.merge_product_to_mother(CURSOR, r, mother)
            su.mark_product_as_inactive(CURSOR, r.id_product)
            su.set_product_proc_status(CURSOR, r.id_product, m.ProcStatus.PROCESSED)
    except Exception as ex:
        raise ex #tmp
        print(f'\n[Error while processing record with id: {r.id_product}]. {ex}\n')

input('Do flip')
#DB.rollback()