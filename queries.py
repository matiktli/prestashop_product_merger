import model as m


"""
------------------------- HELPER FUNCTIONS -------------------------
"""
def add_prefix(arr, prefix):
    return [prefix + x for x in arr]

def turn_into_string(arr):
    return ', '.join(arr)

def add_this_special_char_to_column_names(arr):
    return [('`' + str(x) + '`') for x in arr]

"""
------------------------- FIELDS TO SELECT -------------------------
"""
PRODUCT_FIELDS_SQL = turn_into_string(add_prefix(m.PRODUCT_FIELDS, 'p.'))
PRODUCT_LANG_FIELDS_SQL = turn_into_string(add_prefix(m.PRODUCT_LANG_FIELDS, 'p_lang.'))

PRODUCT_FIELDS_SQL_INSERT = turn_into_string(add_this_special_char_to_column_names(add_prefix(m.PRODUCT_FIELDS, 'p.')))

tmp = m.PRODUCT_LANG_FIELDS.copy()
tmp.append('id_product')
PRODUCT_LANG_FIELDS_SQL_INSERT = turn_into_string(add_this_special_char_to_column_names(add_prefix(tmp, 'p_lang.')))

PRODUCT_SHOP_FIELDS_SQL_INSERT = turn_into_string(add_this_special_char_to_column_names(add_prefix(m.PRODUCT_SHOP_FIELDS, 'p_shop.')))

PRODUCT_ATTRIBUTE_FIELDS_SQL_INSERT = turn_into_string(add_this_special_char_to_column_names(add_prefix(m.PRODUCT_ATTRIBUTE_FIELDS, 'p_atr.')))

PRODUCT_ATTRIBUTE_SHOP_FIELDS_SQL_INSERT = turn_into_string(add_this_special_char_to_column_names(add_prefix(m.PRODUCT_ATTRIBUTE_SHOP_FIELDS, 'p_atr_shop.')))

"""
------------------------- QUERIES -------------------------
"""
GET_PRODUCTS_QUERY = 'SELECT {} FROM `prstshp_product` p LEFT OUTER JOIN `prstshp_product_lang` p_lang ON p_lang.id_product = p.id_product WHERE p.id_product is not null '

INSERT_PRODUCT_QUERY = 'INSERT INTO `prstshp_product` ({}) VALUES ({})'
INSERT_PRODUCT_LANG_QUERY = 'INSERT INTO `prstshp_product_lang` ({}) VALUES ({})'
INSERT_PRODUCT_SHOP_QUERY = 'INSERT INTO `prstshp_product_shop` ({}) VALUES ({})'
INSERT_PRODUCT_ATTRIBUTE_QUERY = 'INSERT INTO `prstshp_product_attribute` ({}) VALUES ({})'
INSERT_PRODUCT_ATTRIBUTE_SHOP_QUERY = 'INSERT INTO `prstshp_product_attribute_shop` ({}) VALUES ({})'