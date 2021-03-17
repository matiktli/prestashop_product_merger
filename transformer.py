import model as m
import random
import string

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

"""
From: `model.PRODUCT`
To: `product` & `product_lang`
"""
def to_record(product: m.Product):
    return ''

def __find_index(list_of_fields, name):
    return list_of_fields.index(name)

def product_to_mother(name, ref, source):
    ref = ref + '-(' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + ')'
    result = m.Mother(*list(source))
    result.id_product = None
    result.reference = ref
    result.name = name
    result.references = [ref]
    result.proc_status = m.ProcStatus.MOTHER.value
    return result