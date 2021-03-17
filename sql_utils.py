import utils as u
import transformer as t
import model as m
import queries as queries

def db_init(c, db=None):
    try:
        q = 'ALTER TABLE `prstshp_product` ADD COLUMN `proc_status` INT(1) DEFAULT -1'
        c.execute(q)
        if db != None:
            db.commit()
    except Exception:
        return

def get_products(c, proc_statuses: [m.ProcStatus] = None, additional_query = ''):
    q = queries.GET_PRODUCTS_QUERY.format(queries.PRODUCT_FIELDS_SQL + ', ' + queries.PRODUCT_LANG_FIELDS_SQL)
    if proc_statuses != None:
        statuses_string = ', '.join(['\"' + str(s.value) + '\"' for s in proc_statuses])
        q += f' AND p.proc_status in ({statuses_string})'
    else:
        q += f' AND p.proc_status is null'

    q += ' ' + additional_query
    q += ' ORDER BY p.date_add desc'
    c.execute(q)
    return list([t.to_product(row) for row in c.fetchall()])

def get_mother_products(c, additional_query = ''):
    return get_products(c, [m.ProcStatus.MOTHER], additional_query = additional_query)

def get_unique_products(c, additional_query = ''):
    return get_products(c, [m.ProcStatus.UNIQUE], additional_query = additional_query)

def get_products_to_process(c, additional_query = ''):
    return get_products(c, [m.ProcStatus.UNIQUE, m.ProcStatus.NOT_PROCESSED], additional_query = additional_query)

def mark_product_as_inactive(c, product_id):
    q = 'UPDATE `prstshp_product` SET `active`=0, `state`=0 WHERE `id_product`=' + str(product_id)
    c.execute(q)

def set_product_proc_status(c, product_id, status: m.ProcStatus):
    q = f'UPDATE `prstshp_product` SET `proc_status`={status.value} WHERE `id_product`={str(product_id)}'
    c.execute(q)

def find_mother_for_product(c, product):
    if len(product.references) == 0:
        return None # We can not find mother if there are no refs
    main_ref = product.references[0]
    q = f'AND p.reference like \"{main_ref}%\"'
    potential_mothers = get_products(c, [m.ProcStatus.MOTHER, m.ProcStatus.UNIQUE], additional_query=q)
    if len(potential_mothers) == 0:
        return None
    elif len(potential_mothers) > 1:
        raise Exception(f"Two or more mothers found for product with id: {product.id_product}")
    else:
        return potential_mothers[0]

def find_siblings_for_product(c, product):
    potential_siblings = get_products_to_process(c)
    found_siblings = u.get_siblings_products_for_product(product, potential_siblings)
    return found_siblings

def find_attribute_id_by_name(c, name):
    names = [name.lower(), name.upper(), name.capitalize()]
    names = ','.join(['\'' + n + '\'' for n in names])
    q = f'SELECT id_attribute FROM `prstshp_attribute_lang` WHERE name IN ({names})'
    c.execute(q)
    r = c.fetchall()
    r = r[0][0] if len(r) == 1 else None
    return r

def merge_product_to_mother(c, product, mother):
    #TODO - move data from product to combinations
    main_product_ref = product.references[0]
    product_options = product.references[1:]
    
def save_mother(c, mother: m.Mother, db=None):
    mother.redirect_type = '301-category'
    mother_id = insert_product(c, mother, db=db)
    mother.id_product = mother_id
    insert_product_lang(c, mother, db=db)
    insert_product_shop(c, mother, db=db)
    insert_category_product(c, mother, db=db)
    return mother_id

def save_combinations(c, mother_product, source, siblings, db=None, mappings={}):
    for i, p in enumerate(([source] + siblings)):
        product_attribute_id = insert_product_attribute(c, p, db=db, default_on_value=(1 if i == 0 else None), mom_id = mother_product.id_product)
        insert_product_attribute_shop(c, p, db=db, product_attribute_id=product_attribute_id, default_on_value=(1 if i == 0 else None), mom_id = mother_product.id_product)
        insert_stock_available(c, db=db, mother_id=mother_product.id_product, product_attribute_id=product_attribute_id, product_id=p.id_product)
        for i, ref in enumerate(p.references[1:]):
            found_mapping = None
            for k, v in mappings[i+1].items():
                if v == ref:
                   found_mapping = k
            if found_mapping == None:
                raise Exception(f'Could not find attribute mapping for ref: {ref}')
            attribute_id = find_attribute_id_by_name(c, found_mapping)
            if attribute_id == None:
                raise Exception(f'Could not find attribute id for mapping: {found_mapping}')
            insert_product_attribute_combination(c, db=db, attribute_id=attribute_id, product_attribute_id=product_attribute_id)

def insert_product(c, product, db=None):
    product_fields_without_id = m.PRODUCT_FIELDS.copy()
    product_fields_without_id.remove('id_product')
    product_sql_fields_without_id = str(queries.PRODUCT_FIELDS_SQL_INSERT).replace('`p.id_product`,', '').replace('p.', '')

    values = t.to_db_values(product, product_fields_without_id)
    q = queries.INSERT_PRODUCT_QUERY.format(product_sql_fields_without_id, values)
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_product_lang(c, product_lang, db=None):
    product_lang_fields_with_id = m.PRODUCT_LANG_FIELDS.copy()
    product_lang_fields_with_id.append('id_product')
    product_lang_sql_fields_without_id = str(queries.PRODUCT_LANG_FIELDS_SQL_INSERT).replace('p_lang.', '')
    
    values = t.to_db_values(product_lang, product_lang_fields_with_id)
    q = queries.INSERT_PRODUCT_LANG_QUERY.format(product_lang_sql_fields_without_id, values)
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_product_shop(c, product_shop, db=None):
    product_shop_fields_with_id = m.PRODUCT_SHOP_FIELDS.copy()
    product_shop_sql_fields_without_id = str(queries.PRODUCT_SHOP_FIELDS_SQL_INSERT).replace('p_shop.', '')
    
    values = t.to_db_values(product_shop, product_shop_fields_with_id)
    q = queries.INSERT_PRODUCT_SHOP_QUERY.format(product_shop_sql_fields_without_id, values)
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_product_attribute(c, product_attribute, db=None, default_on_value=None, mom_id=None):
    product_shop_fields_with_id = m.PRODUCT_ATTRIBUTE_FIELDS.copy()
    product_shop_sql_fields_without_id = str(queries.PRODUCT_ATTRIBUTE_FIELDS_SQL_INSERT).replace('p_atr.', '')
    
    values = t.to_db_values(product_attribute, product_shop_fields_with_id, defaults={'unit_price_impact': 0, 'default_on': default_on_value, 'id_product': mom_id})
    q = queries.INSERT_PRODUCT_ATTRIBUTE_QUERY.format(product_shop_sql_fields_without_id, values)
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_product_attribute_shop(c, product_attribute_shop, db=None, default_on_value=None, product_attribute_id=None, mom_id=None):
    product_shop_fields_with_id = m.PRODUCT_ATTRIBUTE_SHOP_FIELDS.copy()
    product_shop_sql_fields_without_id = str(queries.PRODUCT_ATTRIBUTE_SHOP_FIELDS_SQL_INSERT).replace('p_atr_shop.', '')
    
    values = t.to_db_values(product_attribute_shop, product_shop_fields_with_id, defaults={'unit_price_impact': 0, 'default_on': default_on_value, 'id_product_attribute': product_attribute_id, 'id_product': mom_id})
    q = queries.INSERT_PRODUCT_ATTRIBUTE_SHOP_QUERY.format(product_shop_sql_fields_without_id, values)
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_product_attribute_combination(c, attribute_id, product_attribute_id, db=None):
    q = f'INSERT INTO `prstshp_product_attribute_combination` (`id_attribute`, `id_product_attribute`) VALUES (\'{attribute_id}\', \'{product_attribute_id}\')'
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_stock_available(c, db=None, product_id=None, product_attribute_id=None, mother_id=None):
    q = f'SELECT quantity FROM `prstshp_stock_available` WHERE id_product={product_id} AND id_product_attribute=0'
    c.execute(q)
    quantity = c.fetchall()
    quantity = quantity[0][0] if len(quantity) == 1 else None
    q = f'INSERT INTO `prstshp_stock_available` (`id_product`, `id_product_attribute`, `quantity`, `id_shop`, `id_shop_group`) VALUES (\'{mother_id}\', \'{product_attribute_id}\', \'{quantity}\', 1, 0)'
    c.execute(q)
    if db != None:
        db.commit()

def insert_category_product(c, mother, db=None):
    q = f'SELECT COUNT(*) FROM `prstshp_category_product` WHERE id_category={mother.id_category_default}'
    c.execute(q)
    count = c.fetchall()
    count = count[0][0] if len(count) == 1 else None
    q = f'INSERT INTO `prstshp_category_product` (id_category, id_product, position) VALUES (\'{mother.id_category_default}\', \'{mother.id_product}\', \'{count + 1}\')'
    c.execute(q)