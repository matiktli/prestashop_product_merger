from recordtype import recordtype
from enum import Enum

"""
------------------------- FIELDS SEPARATE -------------------------
"""

PRODUCT_FIELDS = ['id_product', 'proc_status', 'id_supplier', 'id_manufacturer', 'id_category_default', 'id_shop_default', 'id_tax_rules_group', 'on_sale', 'online_only', 'ean13', 'isbn', 'upc',
    'ecotax', 'quantity', 'minimal_quantity', 'low_stock_threshold', 'low_stock_alert', 'price', 'wholesale_price', 'unity', 'unit_price_ratio',
    'additional_shipping_cost', 'reference', 'supplier_reference', 'location', 'width', 'height', 'depth', 'weight', 'out_of_stock', 'additional_delivery_times',
    'quantity_discount', 'customizable', 'uploadable_files', 'text_fields', 'active', 'redirect_type', 'id_type_redirected', 'available_for_order',
    'available_date', 'show_condition', 'condition', 'show_price', 'indexed', 'visibility', 'cache_is_pack', 'cache_has_attachments', 'is_virtual',
    'cache_default_attribute', 'date_add', 'date_upd', 'advanced_stock_management', 'pack_stock_type', 'state']

PRODUCT_LANG_FIELDS = ['name', 'description', 'id_shop', 'description_short', 'link_rewrite', 'meta_description', 'meta_keywords', 'meta_title', 'available_now', 'available_later',
    'delivery_in_stock', 'delivery_out_stock', 'id_lang']

PRODUCT_SHOP_FIELDS = ['id_product', 'id_shop', 'id_category_default', 'id_tax_rules_group', 'on_sale', 'online_only', 'ecotax', 'minimal_quantity', 'low_stock_threshold', 'low_stock_alert', 'price', 'wholesale_price', 'unity', 'unit_price_ratio', 'additional_shipping_cost', 'customizable', 'uploadable_files', 'text_fields', 'active', 'redirect_type', 'id_type_redirected', 'available_for_order', 'available_date', 'show_condition', 'condition', 'show_price', 'indexed', 'visibility', 'cache_default_attribute', 'advanced_stock_management', 'date_add', 'date_upd', 'pack_stock_type']

PRODUCT_ATTRIBUTE_FIELDS = ['id_product', 'reference', 'supplier_reference', 'location', 'ean13', 'isbn', 'upc', 'wholesale_price', 'price', 'ecotax', 'quantity', 'weight', 'unit_price_impact', 'default_on', 'minimal_quantity', 'low_stock_threshold', 'low_stock_alert', 'available_date']

PRODUCT_ATTRIBUTE_SHOP_FIELDS = ['id_product', 'id_product_attribute', 'id_shop', 'wholesale_price', 'price', 'ecotax', 'weight', 'unit_price_impact', 'default_on', 'minimal_quantity', 'low_stock_threshold', 'low_stock_alert', 'available_date']

STOCK_AVAILABLE_FIELDS = ['id_stock_available', 'id_product', 'id_product_attribute', 'id_shop', 'id_shop_group', 'quantity', 'physical_quantity', 'reserved_quantity', 'depends_on_stock', 'out_of_stock', 'location']


PRODUCT_CUSTOM_DEFINED_FIELDS = ['references']


"""
------------------------- FIELDS COMBINED -------------------------
"""

PRODUCT_COMBINED_FIELDS = PRODUCT_FIELDS + PRODUCT_LANG_FIELDS + PRODUCT_CUSTOM_DEFINED_FIELDS


"""
------------------------- MODELS -------------------------
"""

"""
Product represents join of `product` & `product_lang`
"""
PRODUCT = recordtype('PRODUCT',
    field_names = PRODUCT_COMBINED_FIELDS,
    default=(None,)*len(PRODUCT_COMBINED_FIELDS))

class Product(PRODUCT):
        __slots__ = ()
        def __str__(self):
            return str(f'\nProduct(id: {self.id_product}, name: {self.name}, references: {self.references}, proc_status: {self.proc_status})')
        
        def __repr__(self):
            return self.__str__()


"""
Mother represents join of `product` & `product_lang`
"""
MOTHER = recordtype('MOTHER',
    field_names = PRODUCT_COMBINED_FIELDS,
    default=(None,)*len(PRODUCT_COMBINED_FIELDS))

class Mother(MOTHER):
        __slots__ = ()
        def __str__(self):
            return str(f'Mother(id: {self.id_product}, name: {self.name}, references: {self.references}, proc_status: {self.proc_status})')
        
        def __repr__(self):
            return self.__str__()
"""
------------------------- ENUMS -------------------------
"""

"""
Representing: `product.proc_status`
"""
class ProcStatus(Enum):
    PROCESSED = 0
    UNIQUE = 1
    MOTHER = 2
    POTENTIAL_SIBLING = 3
    NOT_PROCESSED = -1
