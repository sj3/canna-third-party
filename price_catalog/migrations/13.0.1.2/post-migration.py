# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade



def fill_product_catalog_prices(env):
#     openupgrade.logged_query(
#         env.cr, """
#         INSERT INTO price_catalog (name, currency_id,catalog_type,active) 
#         SELECT pp.name, pp.currency_id,'sale',pp.active 
#         FROM product_pricelist pp;
#         """,
#     )
    pricelists = env['product.pricelist'].search(['|', ('active','=', False),
                                                  ('active','=',True)])
    print ("======pricelists========", pricelists)
    for pricelist in pricelists:
        catalog = env['price.catalog'].create({'active':pricelist.active,
                                               'name':pricelist.name,
                                               'currency_id':pricelist.currency_id.id,
                                               'catalog_type':'sale',
                                               'company_id':pricelist.company_id.id
                                               })
        print ("==========catalog========", catalog)
        for line in pricelist.item_ids:
            subcatalog = env['price.subcatalog'].create({'name':catalog.name,
                                            'start_date':line.date_start,
                                            'end_date':line.date_end,
                                            'catalog_id':catalog.id})
            print ("=======subcatalog=========", subcatalog, line.product_id)
            if line.product_id:
                price = pricelist.get_product_price(line.product_id, 1.0, False)
                items = env['price.catalog.item'].create({'product_id':line.product_id.id,
                                                          'subcatalog_id':subcatalog.id,
                                                          'price':price})
                print ("=====items======", items)

@openupgrade.migrate()
def migrate(env, version):
    print ("==============in migrate===========\n\n=====================\n\n")
    fill_product_catalog_prices(env)

