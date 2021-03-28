import utils as u
import transformer as t
import model as m
import queries as queries

def db_init(c, db=None):
    try:
        q = 'ALTER TABLE `' + queries.TABLE_PREFIX + 'product` ADD COLUMN `proc_status` INT(1) DEFAULT -1'
        c.execute(q)
        if db != None:
            db.commit()
    except Exception:
        return
def list_to_sql(l):
    return '({})'.format(','.join(['\'' + str(x) + '\'' for x in l]))
    
def get_products(c, proc_statuses: [m.ProcStatus] = None, additional_query = '', limit=None):
    q = queries.GET_PRODUCTS_QUERY.format(queries.PRODUCT_FIELDS_SQL + ', ' + queries.PRODUCT_LANG_FIELDS_SQL)
    if proc_statuses != None:
        statuses_string = ', '.join(['\"' + str(s.value) + '\"' for s in proc_statuses])
        q += f' AND p.proc_status in ({statuses_string})'
    else:
        q += f' AND p.proc_status is null'

    q += ' ' + additional_query
    q += ' ORDER BY p.date_add desc'
    if limit is not None:
        q += f' LIMIT {limit}'
    c.execute(q)
    return list([t.to_product(row) for row in c.fetchall()])

def get_mother_products(c, additional_query = ''):
    return get_products(c, [m.ProcStatus.MOTHER], additional_query = additional_query)

def get_unique_products(c, additional_query = ''):
    return get_products(c, [m.ProcStatus.UNIQUE], additional_query = additional_query)

def get_products_to_process(c, ids=None, limit=None, offset=None):
    if ids is not None:
        additional_query = f'AND p.id_product IN {list_to_sql(ids)}'
    return get_products(c, [m.ProcStatus.UNIQUE, m.ProcStatus.NOT_PROCESSED], additional_query = additional_query, limit=limit)

def mark_products_as_inactive(c, product_ids: []):
    q = 'UPDATE `' + queries.TABLE_PREFIX + 'product` SET `active`=0, `state`=0 WHERE `id_product` IN ' + list_to_sql(product_ids)
    c.execute(q)

def set_products_proc_status(c, product_ids: [], status: m.ProcStatus):
    q = f'UPDATE `' + queries.TABLE_PREFIX + f'product` SET `proc_status`={status.value} WHERE `id_product` IN ' + list_to_sql(product_ids)
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

def find_attribute_id_by_name(c, name):
    names = [name.lower(), name.upper(), name.capitalize()]
    names = ','.join(['\'' + n + '\'' for n in names])
    q = f'SELECT a_lang.id_attribute, a.id_attribute_group FROM `' + queries.TABLE_PREFIX + f'attribute_lang` a_lang INNER JOIN `{queries.TABLE_PREFIX}attribute` a ON a.id_attribute = a_lang.id_attribute WHERE a_lang.name IN ({names})'
    c.execute(q)
    r = c.fetchall()
    r = r[0] if len(r) == 1 else (None, None)
    return r

def merge_product_to_mother(c, product, mother):
    #TODO-hard-p2- move data from product to combinations
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
    seen_attr_to_group = set()
    for i, p in enumerate(([source] + siblings)):
        product_attribute_id = insert_product_attribute(c, p, db=db, default_on_value=(1 if i == 0 else None), mom_id = mother_product.id_product)
        insert_product_attribute_shop(c, p, db=db, product_attribute_id=product_attribute_id, default_on_value=(1 if i == 0 else None), mom_id = mother_product.id_product)
        insert_stock_available(c, mother_id=mother_product.id_product, product_attribute_id=product_attribute_id, product_id=p.id_product)
        move_images_from_product_to_other(c, source_product_id=p.id_product, target_product_id=mother_product.id_product, cover='NULL', product_attribute_id=product_attribute_id)
        for j, ref in enumerate(p.references[1:]):
            found_mapping = None
            for k, v in mappings[j+1].items():
                if v == ref:
                   found_mapping = k
            if found_mapping == None:
                raise Exception(f'Could not find attribute mapping for ref: {ref}')
            attribute_id, attribute_group_id = find_attribute_id_by_name(c, found_mapping)
            if attribute_id == None:
                raise Exception(f'Could not find attribute id for mapping: {found_mapping}')
            insert_product_attribute_combination(c, db=db, attribute_id=attribute_id, product_attribute_id=product_attribute_id)
            if '{}-{}'.format(attribute_id, attribute_group_id) not in seen_attr_to_group:
                seen_attr_to_group.add('{}-{}'.format(attribute_id, attribute_group_id))
                insert_layered_product_attribute(c, product=mother_product, attribute_id=attribute_id, attribute_group_id=attribute_group_id)
    set_only_one_img_as_cover(c, mother_product.id_product)
    insert_summed_stock(c, mother_id=mother_product.id_product, siblings = [source] + siblings)

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
    q = f'INSERT INTO `' + queries.TABLE_PREFIX + f'product_attribute_combination` (`id_attribute`, `id_product_attribute`) VALUES (\'{attribute_id}\', \'{product_attribute_id}\')'
    c.execute(q)
    if db != None:
        db.commit()
    return c.lastrowid

def insert_layered_product_attribute(c, product, attribute_id, attribute_group_id):
    q = f'INSERT INTO `' + queries.TABLE_PREFIX + f'layered_product_attribute` (`id_attribute`, `id_product`, `id_attribute_group`, `id_shop`) VALUES (\'{attribute_id}\', \'{product.id_product}\', \'{attribute_group_id}\', 1)'
    c.execute(q)

def insert_stock_available(c, product_id=None, product_attribute_id=None, mother_id=None, quantity=None):
    if quantity == None:
        quantity = count_quantity_for_products(c, [product_id])
    q = f'INSERT INTO `' + queries.TABLE_PREFIX + f'stock_available` (`id_product`, `id_product_attribute`, `quantity`, `id_shop`, `id_shop_group`) VALUES (\'{mother_id}\', \'{product_attribute_id}\', \'{quantity}\', 1, 0)'
    c.execute(q)
    
def insert_summed_stock(c, siblings, mother_id):
    summed_q = count_quantity_for_products(c, [s.id_product for s in siblings])
    print('-> ', summed_q)
    insert_stock_available(c, quantity=summed_q, product_attribute_id=0, mother_id=mother_id)

def count_quantity_for_products(c, product_ids: []):
    q = f'SELECT quantity FROM `' + queries.TABLE_PREFIX + f'stock_available` WHERE id_product in ({queries.turn_into_string(product_ids)}) AND id_product_attribute=0'
    c.execute(q)
    q_result = c.fetchall()
    s = 0
    if len(q_result) == 0: return None
    for quant in q_result:
        s += int(quant[0])
    return s

def insert_category_product(c, mother, db=None):
    q = f'SELECT COUNT(*) FROM `' + queries.TABLE_PREFIX + f'category_product` WHERE id_category={mother.id_category_default}'
    c.execute(q)
    count = c.fetchall()
    count = count[0][0] if len(count) == 1 else None
    q = f'INSERT INTO `' + queries.TABLE_PREFIX + f'category_product` (id_category, id_product, position) VALUES (\'{mother.id_category_default}\', \'{mother.id_product}\', \'{count + 1}\')'
    c.execute(q)

def move_images_from_product_to_other(c, source_product_id, target_product_id, product_attribute_id, cover='NULL'):
    sq = f'SELECT id_image FROM `{queries.TABLE_PREFIX}image` WHERE id_product={source_product_id}'
    c.execute(sq)
    sq_results = c.fetchall()
    for i, img_id in enumerate(sq_results):
        uq_image = f'UPDATE `{queries.TABLE_PREFIX}image` SET id_product={target_product_id}, cover={cover}, position={i} WHERE id_product={source_product_id} AND id_image={img_id[0]}'
        c.execute(uq_image)
        uq_image_shop = f'UPDATE `{queries.TABLE_PREFIX}image_shop` SET id_product={target_product_id}, cover={cover} WHERE id_product={source_product_id} AND id_image={img_id[0]}'
        c.execute(uq_image_shop)
        iq_image_attr = f'INSERT INTO `{queries.TABLE_PREFIX}product_attribute_image` (id_product_attribute, id_image) VALUES ({product_attribute_id},{img_id[0]})'
        c.execute(iq_image_attr)

def set_only_one_img_as_cover(c, product_id):
    sq = f'SELECT id_image FROM `{queries.TABLE_PREFIX}image` WHERE id_product={product_id} LIMIT 1'
    c.execute(sq)
    id_image = c.fetchall()[0][0]
    uq_image = f'UPDATE `{queries.TABLE_PREFIX}image` SET cover=1 WHERE id_product={product_id} AND id_image={id_image}'
    c.execute(uq_image)
    uq_image_shop = f'UPDATE `{queries.TABLE_PREFIX}image_shop` SET cover=1 WHERE id_product={product_id} AND id_image={id_image}'
    c.execute(uq_image_shop)

def save_price_data(c, mother_product, source_product):
    sq = f'SELECT id_currency, id_shop, price_min, price_max, id_country FROM `{queries.TABLE_PREFIX}layered_price_index` WHERE id_product={source_product.id_product} AND id_shop=1 AND id_country=14 LIMIT 1'
    c.execute(sq)
    results = c.fetchall()[0]
    iq_image = 'INSERT INTO `{}layered_price_index` (id_product, id_currency, id_shop, price_min, price_max, id_country) VALUES ({}, {}, {}, {}, {}, {})'.format(queries.TABLE_PREFIX, mother_product.id_product, *results)
    c.execute(iq_image)
