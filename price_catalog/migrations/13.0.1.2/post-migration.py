from openupgradelib import openupgrade


def fill_product_catalog_prices(env):
    pricelists = env['product.pricelist'].search(['|', ('active', '=', False),
                                                  ('active', '=', True)])
    for pricelist in pricelists:
        catalog = env['price.catalog'].create(
            {'active':pricelist.active,
            'name':pricelist.name,
            'currency_id':pricelist.currency_id.id,
            'catalog_type':'sale',
            'company_id':pricelist.company_id.id
        })
        for line in pricelist.item_ids:
            subcatalog = env['price.subcatalog'].create(
                {'name':catalog.name,
                'start_date':line.date_start,
                'end_date':line.date_end,
                'catalog_id':catalog.id
            })
            if line.product_id:
                price = pricelist.get_product_price(line.product_id, 1.0, False)
                items = env['price.catalog.item'].create(
                    {'product_id':line.product_id.id,
                    'subcatalog_id':subcatalog.id,
                    'price':price
                })


@openupgrade.migrate()
def migrate(env, version):
    fill_product_catalog_prices(env)
