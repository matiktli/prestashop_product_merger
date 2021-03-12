import difflib as df
import model as m

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
        raise Exception(f'Could not find head ref. Two or more head refs present: {grouped_refs[0]}')
    return next(iter(grouped_refs[0]))

"""
Obtain head name that will be used as reference inside newly created mother.
It is hard assumtion that we have already siblings in here.
"""
def get_head_name_from_grouped_names(grouped_names):
    if len(grouped_names[0]) == 0:
        raise Exception('Could not find head name')
    elif len(grouped_names[0]) > 1:
        raise Exception(f'Could not find head name. Two or more head names present: {grouped_names[0]}')
    return next(iter(grouped_names[0]))

"""
Group the references of provided siblings by their order. (sort of like the json structure)
"""
def group_refs_by_order(products):
    grouped_refs = []
    for p in products:
        refs = p.references
        for i, r in enumerate(refs):
            if len(grouped_refs) <= i:
                grouped_refs.append([])
            if r not in grouped_refs[i]:
                grouped_refs[i].append(r)
    return grouped_refs

"""
Group the names of provided siblings by their order. (sort of like the json structure)
"""
def group_names_by_order(products):
    grouped_names = []
    head_name = find_most_common_name_part(products)
    if not head_name:
        raise Exception("Could not find head_name")
    grouped_names.append([head_name])
    for p in products:
        name_suffix = p.name.replace(head_name + ' ', '')
        for i, name_part in enumerate(name_suffix.split(' ')):
            if len(grouped_names) <= i+1:
                grouped_names.append([])
            if name_part not in grouped_names[i+1]:
                grouped_names[i+1].append(name_part)
    return grouped_names

"""
Convert reference table to reference string
"""
def to_ref_string(refs: []):
    return '_'.join(refs)

"""
Find most repeating name in siblings products
"""
def find_most_common_name_part(products, n=2):
    result = None
    for p in products:
        if result == None:
            result = p.name
        else:
            result = longest_substring(result, p.name)
    # lets remove any 'non-word' from the end of string just in case
    splited = result.split(' ')
    last_suffix = splited[len(splited) - 1]
    if len(last_suffix) <= n:
        result = ' '.join(splited[:-1])
    return result


"""
Create mapping for refs into names if possible
"""
def map_attribute_refs_to_names(grouped_attr_refs, grouped_attr_names):
    result = []
    if len(grouped_attr_refs) != len(grouped_attr_names):
        raise Exception("Could not match refs to names. Wrong initial sizes")
    for i in range(0, len(grouped_attr_refs)):
        inside_grouped_attr_refs = grouped_attr_refs[i]
        inside_grouped_attr_names = grouped_attr_names[i]
        if len(inside_grouped_attr_refs) != len(inside_grouped_attr_names):
            raise Exception("Could not match refs to names. Wrong inside sizes")
        inside_mapping = {}
        for j in range(0, len(inside_grouped_attr_refs)):
            inside_mapping[inside_grouped_attr_names[j]] = inside_grouped_attr_refs[j]
        result.append(inside_mapping)
    return result

"""
Build mother product from source product
"""
def prepare_mother_object(source_product, name, ref, attribute_mapping, siblings=[]):
    return None

"""
------------------------- SUPER DUMY UTILS -------------------------
"""

"""
Utlility function for finding longest repeating substring in two strings
"""
def longest_substring(s1, s2):
    answer = ""
    len1, len2 = len(s1), len(s2)
    for i in range(len1):
        match = ""
        for j in range(len2):
            if (i + j < len1 and s1[i + j] == s2[j]):
                match += s2[j]
            else:
                if (len(match) > len(answer)):
                    answer = match
                match = ""
    return answer

"""
Very trivial function implementation to do not produce boiler-plate code
"""
def contains(l, filter):
    for x in l:
        if filter(x):
            return True
    return False