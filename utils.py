import model as m
import copy
import transformer as t
import os
from itertools import takewhile

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

def generate_name_like_search(p: m.Product):
    l = len(p.name)
    q = '%'+str(p.name)[2:int(l/3)]+'%'
    return q

def generate_reference_like_search(p: m.Product):
    q = '%'
    return q

def generate_category_ids_search(p: m.Product):
    ids = []
    ids.append(str(p.id_category_default))
    return ids

def generate_manufacturer_ids_search(p: m.Product):
    ids = []
    ids.append(str(p.id_manufacturer))
    return ids

"""
Obtains a common prefix of len `n` from list of strings else None
"""
def get_common_prefix(ref_group: []):
    return os.path.commonprefix(ref_group)

"""
Obtains head ref that will be used as reference inside newly created mother.
It is hard assumtion that we have already siblings in here.
"""
def get_head_ref_from_grouped_refs(grouped_refs):
    if len(grouped_refs[0]) == 0:
        raise Exception('Could not find `head ref`')
    elif len(grouped_refs[0]) > 1:
        prefix = get_common_prefix(grouped_refs[0])
        if prefix is None or len(prefix) == 0:
            raise Exception(f'Could not find `head ref` nor `common prefix` in multiple head refs: {grouped_refs[0]}')
        else:
            return str(prefix)
        raise Exception(f'Could not find `head ref`. Two or more `head refs` present: {grouped_refs[0]}')
    return str(next(iter(grouped_refs[0])))

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
def group_names_by_order(products, override_common_name=None):
    grouped_names = []
    head_name = override_common_name if override_common_name is not None else find_most_common_name_part(products)
    if not head_name:
        head_name = str(products[0].id_product)
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
    print('......')
    product_names = [p.name.split(' ') for p in products]
    return most_repeating_prefix_in_list(product_names)
    result = None
    for p in products:
        if result == None:
            result = p.name
        else:
            result = longest_substring(result.split(' '), p.name.split(' '))
    # lets remove any 'non-word' from the end of string just in case
    splited = result.split(' ')
    last_suffix = splited[len(splited) - 1]
    if len(last_suffix) <= n:
        result = ' '.join(splited[:-1])
    return result


class MappingException(Exception):
    def __init__(self, message):
        self.message=message
        super().__init__(self.message) 

def can_map_attribute_refs_to_names(grouped_attr_refs, grouped_attr_names):
    try:
        map_attribute_refs_to_names(grouped_attr_refs, grouped_attr_names)
        return True
    except MappingException:
        return False


def super_duper_smart_function(grouped_attr_refs, grouped_attr_names):
    if len(grouped_attr_refs) == len(grouped_attr_names):
        return grouped_attr_refs, grouped_attr_names
    else:
        if len(grouped_attr_refs) > len(grouped_attr_names):
            last_head_name_sub_part = grouped_attr_names[0][0].split(' ')[-1].strip()
            grouped_attr_names[0] = [grouped_attr_names[0][0].replace(' ' + last_head_name_sub_part, '')]
            grouped_attr_names.insert(1, [last_head_name_sub_part])
            print(grouped_attr_names)
            return grouped_attr_refs, grouped_attr_names
        else:
            return grouped_attr_refs, grouped_attr_names

"""
Create mapping for refs into names if possible
"""
def map_attribute_refs_to_names(grouped_attr_refs, grouped_attr_names):
    result = []
    print('Refs--> ', grouped_attr_refs)
    print('Names--> ', grouped_attr_names)
    if len(grouped_attr_refs) != len(grouped_attr_names):
        grouped_attr_refs, grouped_attr_names = super_duper_smart_function(grouped_attr_refs, grouped_attr_names)
        if len(grouped_attr_refs) != len(grouped_attr_names):
            raise MappingException("Could not match refs to names. Wrong initial sizes")
    for i in range(0, len(grouped_attr_refs)):
        inside_grouped_attr_refs = grouped_attr_refs[i]
        inside_grouped_attr_names = grouped_attr_names[i]
        if len(inside_grouped_attr_refs) != len(inside_grouped_attr_names):
            raise MappingException("Could not match refs to names. Wrong inside sizes")
        inside_mapping = {}
        for j in range(0, len(inside_grouped_attr_refs)):
            inside_mapping[inside_grouped_attr_names[j]] = inside_grouped_attr_refs[j]
        result.append(inside_mapping)
    print('Mappings--> ', result)
    return result, grouped_attr_refs, grouped_attr_names

"""
Build mother product from source product
"""
def prepare_mother_object(source_product, name, ref, attribute_mapping, siblings=[]):
    mother = t.product_to_mother(name, ref, source=source_product)
    return mother

def get_first_part_of_name_that_is_not_prefix(name, prefix):
    prefix = prefix.strip()
    r = name.replace(prefix, '').strip().split(' ')[0]
    r = r.strip().replace('\n', '')
    return r
"""
------------------------- SUPER DUMY UTILS -------------------------
"""

def strip(string1):
    return string1.replace(' ','')

"""
Utlility function for finding longest repeating substring in two strings
"""
def longest_substring(s1, s2):
    print(s1)
    print(s2)
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

def min_arr(l):
    m = l[0]
    for e in l:
        if len(e) <= len(m):
            m = e
    return m

def max_arr(l):
    m = l[0]
    for e in l:
        if len(e) >= len(m):
            m = e
    return m

def most_repeating_prefix(l):
    if not l: return ''
    s1 = min_arr(l) if isinstance(l, list) else min(l)
    s2 = max_arr(l) if isinstance(l, list) else max(l)
    result = s1
    for i, c in enumerate(s1):
        if c != s2[i]:
            result = s1[:i]
            break
    if isinstance(result, list):
        return ' '.join(result)
    else:
        return result.strip()

def most_repeating_prefix_in_list(l):
    return ' '.join(os.path.commonprefix(l))

"""
Very trivial function implementation to do not produce boiler-plate code
"""
def contains(l, filter):
    for x in l:
        if filter(x):
            return True
    return False