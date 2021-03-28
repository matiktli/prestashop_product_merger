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
        found_siblings = self.__filter_siblings_by_name(product, found_siblings)
        print(f'Potentials after name filter: {len(found_siblings)}')
        return found_siblings

    def __get_potential_siblings(self, product, limit=None, offset=None):
        name_like_str = u.generate_name_like_search(product)
        reference_like_str = u.generate_reference_like_search(product)
        category_ids_str = su.list_to_sql(u.generate_category_ids_search(product))
        manufacturer_ids_str = su.list_to_sql(u.generate_manufacturer_ids_search(product))
        siblings_query = 'AND (p_lang.name LIKE \'{}\' OR p.reference LIKE \'{}\') AND p.id_category_default IN {} AND p.id_manufacturer IN {}'.format(name_like_str, reference_like_str, category_ids_str, manufacturer_ids_str)
        print(f'\n\n{siblings_query}\n\n')
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
                siblings.append(p)
        print(f'----> [REF] Ref-{len(siblings)}: {main_ref}\n----> Search in: {available_refs}\n----> Found: {found_similar_refs}')
        return siblings

    def __filter_siblings_by_name(self, product, potential_siblings):
        available_names = set([p.name for p in potential_siblings if p.name != product.name])
        main_name = product.name.split(' ')
        # TODO-important find common name and narrow results
                

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