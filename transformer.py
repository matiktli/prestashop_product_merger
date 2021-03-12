import model as m


"""
From: `product` & `product_lang`
To: `model.PRODUCT`
"""
def to_product(db_row):
    refs_index = __find_index(m.PRODUCT_COMBINED_FIELDS, 'reference')
    refs_by_flor = db_row[refs_index].split('_')
    refs_by_dash = db_row[refs_index].split('-')
    refs = refs_by_flor if len(refs_by_flor) >= len(refs_by_dash) else refs_by_dash
    if len(refs) == 1 and refs[0] == '':
        refs.clear()
    return m.Product(*db_row, references=refs)

def __find_index(list_of_fields, name):
    return list_of_fields.index(name)