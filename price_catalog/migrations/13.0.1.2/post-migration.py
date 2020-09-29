from openupgradelib import openupgrade


def fill_product_catalog_prices(env):
    pricelists = env['product.pricelist'].search(['|', ('active', '=', False),
                                                  ('active', '=', True)])
    for pricelist in pricelists:
        catalog = env['price.catalog'].create({
            'active': pricelist.active,
            'name': pricelist.name,
            'currency_id': pricelist.currency_id.id,
            'catalog_type': 'sale',
            'company_id': pricelist.company_id.id
        })
        subcatalog = env['price.subcatalog'].create({
            'name': catalog.name + str(catalog.id),
            'catalog_id': catalog.id
        })
        for line in pricelist.item_ids:
            product_id = False
            if line.applied_on == '0_product_variant' and line.product_id:
                product_id = line.product_id
            if line.applied_on == '1_product' and line.product_tmpl_id:
                product_id = env['product.product'].search([
                    ('product_tmpl_id', '=', line.product_tmpl_id.id)])
            if product_id:
                item = env['price.catalog.item'].search([
                    ('product_id', '=', product_id.id), 
                    ('subcatalog_id', '=', subcatalog.id)])
                if not item:
                    price = pricelist.get_product_price(product_id, 1.0, False)
                    env['price.catalog.item'].create({
                        'product_id': product_id.id,
                        'subcatalog_id': subcatalog.id,
                        'price': price
                    })


@openupgrade.migrate()
def migrate(env, version):
    fill_product_catalog_prices(env)
