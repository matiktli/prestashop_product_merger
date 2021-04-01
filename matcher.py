import utils as u
import sql_utils as su
import model as m
import difflib as df

class SiblingsMatcher():

    def __init__(self, cursor, limit=100):
        self.cursor = cursor
        self.limit = limit

    def find_siblings(self, product):
        potential_siblings = self.__get_potential_siblings(product, limit=self.limit)
        print(f'Potentials: {len(potential_siblings)}')
        found_siblings = self.__filter_siblings_by_reference(product, potential_siblings)
        print(f'Potentials after ref filter: {len(found_siblings)}')
        override_common_name = None
        found_siblings, override_common_name = self.__filter_siblings_by_name(product, found_siblings)
        print(f'Potentials after name filter: {len(found_siblings)}')
        return found_siblings, override_common_name

    def __get_potential_siblings(self, product, limit=None, offset=None):
        name_like_str = u.generate_name_like_search(product)
        reference_like_str = u.generate_reference_like_search(product)
        category_ids_str = su.list_to_sql(u.generate_category_ids_search(product))
        manufacturer_ids_str = su.list_to_sql(u.generate_manufacturer_ids_search(product))
        siblings_query = 'AND (p_lang.name LIKE \'{}\' OR p.reference LIKE \'{}\') AND p.id_category_default IN {} AND p.id_manufacturer IN {}'.format(name_like_str, reference_like_str, category_ids_str, manufacturer_ids_str)
        return su.get_products(self.cursor, [m.ProcStatus.UNIQUE, m.ProcStatus.NOT_PROCESSED], additional_query = siblings_query, limit=limit)

    """
    Obtain siblings from products similar to given product via `Product.reference` distance calculation
    """
    def __filter_siblings_by_reference(self, product, potential_siblings):
        available_refs = set([u.to_ref_string(p.references) for p in potential_siblings if u.to_ref_string(p.references) != u.to_ref_string(product.references)])
        main_ref = u.to_ref_string(product.references)
        found_similar_refs = set(df.get_close_matches(main_ref, available_refs, n=len(available_refs)))
        siblings = []
        for p in potential_siblings:
            ref_string = u.to_ref_string(p.references)
            if ref_string in found_similar_refs:
                if product.references[0] == p.references[0]:
                    siblings.append(p)
        return siblings

    def __filter_siblings_by_name(self, product, potential_siblings, search_for_name_part=None):
        print('----')
        available_names = [p.name.split(' ') for p in potential_siblings if p.name != product.name]
        
        if search_for_name_part is None:
            most_common_prefix = u.most_repeating_prefix(available_names).strip()
            print('kuhwa: ', most_common_prefix)
            first_non_prefix_part = u.get_first_part_of_name_that_is_not_prefix(product.name, most_common_prefix).strip()
            search_for_name_part = most_common_prefix + ' ' + first_non_prefix_part
        potential_siblings = [s for s in potential_siblings if search_for_name_part in s.name]
        print(f'--Searching for part: \'{str(search_for_name_part)}\' found: {len(potential_siblings)}.')
        grouped_attribute_refs = u.group_refs_by_order(potential_siblings)
        grouped_attribute_names = u.group_names_by_order(potential_siblings, override_common_name=search_for_name_part)
        print('kuhwa2: ', search_for_name_part)
        if u.can_map_attribute_refs_to_names(grouped_attribute_refs, grouped_attribute_names):
            return potential_siblings, search_for_name_part
        else:
            first_non_prefix_part = u.get_first_part_of_name_that_is_not_prefix(product.name, search_for_name_part).strip()
            search_for_name_part = (search_for_name_part.strip() + ' ' + first_non_prefix_part.strip()).strip()
            return self.__filter_siblings_by_name(product, potential_siblings, search_for_name_part=search_for_name_part)
                

    def __longest_substring_finder(self, string1, string2):
        answer = ""
        len1, len2 = len(string1), len(string2)
        for i in range(len1):
            match = []
            for j in range(len2):
                if (i + j < len1 and string1[i + j] == string2[j]):
                    match.append(string2[j])
                else:
                    if (len(match) > len(answer)): answer = match
                    match = []
        return answer

    