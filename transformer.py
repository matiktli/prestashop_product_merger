import model as m
import random
import string
import datetime

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
    #ref = ref + '-(' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)) + ')'
    result = m.Mother(*list(source))
    result.id_product = None
    result.reference = ref
    result.name = name
    result.references = [ref]
    result.proc_status = m.ProcStatus.MOTHER.value
    result.link_rewrite = name.lower().strip().replace(' ', '-')
    return result

def to_db_values(source, fields_to_take, defaults={}):
    result_values = []
    source_fields = source._fields
    for i, field_name in enumerate(fields_to_take):
        if field_name in source_fields:
            val = getattr(source, field_name)
            if isinstance(val, datetime.datetime):
                if field_name in ('available_date'):
                    val = val.strftime('%Y-%m-%d')
                else:
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
            result_values.append(val)
        else:
            if field_name in defaults:
                val = defaults[field_name]
                result_values.append(val)
            else:
                print('---Could not find: ', field_name)
    result = ['NULL' if i in [None, 'None'] else ('\'' + str(i) + '\'') for i in result_values]
    return ', '.join(result)