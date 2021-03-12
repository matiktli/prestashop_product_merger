import model as m


"""
------------------------- HELPER FUNCTIONS -------------------------
"""
def add_prefix(arr, prefix):
    return [prefix + x for x in arr]

def turn_into_string(arr):
    return ', '.join(arr)

"""
------------------------- FIELDS TO SELECT -------------------------
"""
PRODUCT_FIELDS_SQL = turn_into_string(add_prefix(m.PRODUCT_FIELDS, 'p.')) + ', ' + turn_into_string(add_prefix(m.PRODUCT_LANG_FIELDS, 'p_lang.'))


"""
------------------------- QUERIES -------------------------
"""
GET_PRODUCTS_QUERY = 'SELECT {} FROM `prstshp_product` p INNER JOIN `prstshp_product_lang` p_lang ON p_lang.id_product = p.id_product WHERE p_lang.id_lang = 1'

CREATE_NEW_PRODUCT_QUERY_PART = 'INSERT INTO `prstshp_product` ({}) VALUES ({})'
