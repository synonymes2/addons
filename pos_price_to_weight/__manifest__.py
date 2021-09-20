# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale - Price to Weight',
    'version': '12.0.2.0.0',
    'category': 'Point Of Sale',
    'summary': 'Compute weight based on barcodes with prices',
    'author': 'Mohamed Sadiq',
    'website': 'http://www.lalouve.net/',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'data/barcode_rule.xml',
        'views/assets.xml',
        'views/view_pos_config.xml',
    ],
    'demo': [
        'demo/product_product.xml',
    ],
    'installable': True,
}
