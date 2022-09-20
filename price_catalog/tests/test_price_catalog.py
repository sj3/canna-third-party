import logging
import os

from odoo.tests import common
from psycopg2 import IntegrityError

_logger = logging.getLogger(__name__)

directory = os.path.dirname(__file__)


class TestPriceCatalog(common.TransactionCase):
    
    def setUp(self):
        super(TestPriceCatalog, self).setUp()

    def test_createCatalog(self):
        catalog = self.env['price.catalog'].create({
            'name': "UNITTEST CATALOG",
            'catalog_type': 'sale',
        })

        subcatalog = self.env['price.subcatalog'].create({
            'name': "UNITTEST v1",
            "catalog_id": catalog.id,
        })

        item = self.env['price.catalog.item'].create({
            'subcatalog_id': subcatalog.id,
            'product_id': self.env.ref('product.product_delivery_01').id,
            'price': 7,
        })

        with self.assertRaises(IntegrityError):
            item = self.env['price.catalog.item'].create({
                'subcatalog_id': subcatalog.id,
                'product_id': self.env.ref('product.product_delivery_01').id,
                'price': 9,
            })


    def test_createCatalogWithoutStartDate(self):
        catalog = self.env['price.catalog'].create({
            'name': "UNITTEST CATALOG",
            'catalog_type': 'sale',
        })
        
        with self.assertRaises(IntegrityError):                
            subcatalog = self.env['price.subcatalog'].create({
                'name': "UNITTEST v1",
                "catalog_id": catalog.id,
                'start_date': False,
            })
