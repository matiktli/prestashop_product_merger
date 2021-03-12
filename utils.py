from collections import namedtuple
import difflib as df

PRODUCT = namedtuple('PRODUCT', ['id_product', 'name', 'references', 'proc_status'])


"""
Transform from db row to Product
"""
def to_product(db_row):
    refs_by_flor = db_row[2].split('_')
    refs_by_dash = db_row[2].split('-')
    refs = refs_by_flor if len(refs_by_flor) >= len(refs_by_dash) else refs_by_dash
    if len(refs) == 1 and refs[0] == '':
        refs.clear()
    return PRODUCT(id_product=db_row[0], name=db_row[1], references=refs, proc_status=db_row[3])

"""
Obtain the mother product name from grouped list of products
"""
def obtain_mother_product_name_from_grouped_products(grouped_products):
    # For now we assuming that the first three parts out of product name are mother name
    return __obtain_mother_name_from_product_tmp(grouped_products[0], n=3)

"""
Helping function
This function might need to be refactored if we face more live scenarios of products
"""
def __obtain_mother_name_from_product_tmp(product, n=3):
    full_name_split = product.name.split(' ')
    if len(full_name_split) >= n:
        return ' '.join(full_name_split[:n])
    return product.name

"""
Obtain siblings from products similar to given product via `Product.reference` distance calculation
"""
def get_siblings_products_for_product(product, products):
    available_refs = set([to_ref_string(p.references) for p in products if to_ref_string(p.references) != to_ref_string(product.references)])
    main_ref = to_ref_string(product.references)
    found_similar_refs = set(df.get_close_matches(main_ref, available_refs, n=len(available_refs) - 1))
    siblings = []
    for p in products:
        ref_string = to_ref_string(p.references)
        if ref_string in found_similar_refs:
            siblings.append(p)
    return siblings

"""
Obtain head ref that will be used as reference inside newly created mother.
It is hard assumtion that we have already siblings in here.
"""
def get_head_ref_from_grouped_refs(grouped_refs):
    if len(grouped_refs[0]) == 0:
        raise Exception('Could not find head ref')
    elif len(grouped_refs[0]) > 1:
        raise Exception('Could not find head ref. Two or more head refs present')
    return next(iter(grouped_refs[0]))

"""
Group the references of provided siblings by their order. (sort of like the json structure)
"""
def group_refs_by_order(products):
    grouped_refs = []
    for p in products:
        refs = p.references
        for i, r in enumerate(refs):
            if len(grouped_refs) <= i:
                grouped_refs.append(set())
            if r not in grouped_refs[i]:
                grouped_refs[i].add(r)
    return grouped_refs

"""
Very trivial function implementation to do not produce boiler-plate code
"""
def contains(l, filter):
    for x in l:
        if filter(x):
            return True
    return False

"""
Convert reference table to reference string
"""
def to_ref_string(refs: []):
    return '_'.join(refs)