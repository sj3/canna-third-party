import logging
import os

from odoo.tests import common
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime

_logger = logging.getLogger(__name__)

directory = os.path.dirname(__file__)


class TestGetPrice(common.TransactionCase):

    def test_get_price(self):
        product = self.env.ref('product.product_delivery_01')
        
        catalog = self.env['price.catalog'].create({
            'name': "UNITTEST CATALOG",
            'catalog_type': 'sale',
        })

        subcatalog = self.env['price.subcatalog'].create({
            'name': "UNITTEST v1",
            "catalog_id": catalog.id,
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',            
        })

        item = self.env['price.catalog.item'].create({
            'subcatalog_id': subcatalog.id,
            'product_id': product.id,
            'price': 7,
        })

        # before
        self.assertEquals(
            7,
            catalog.get_price(
                product,
                datetime.strptime('2020-04-01 12:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
            )
        ) 
        # during boundary
        self.assertEquals(
            7,
            catalog.get_price(
                product,
                datetime.strptime('2020-01-01 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
            )
        )
       
        # during 
        self.assertEquals(
            7,
            catalog.get_price(
                product,
                datetime.strptime('2020-04-01 12:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
            )
        )
        # during boundary
        self.assertEquals(
            7,
            catalog.get_price(
                product,
                datetime.strptime('2020-12-31 12:59:59', DEFAULT_SERVER_DATETIME_FORMAT)
            )
        )

        # after
        self.assertEquals(
            0,
            catalog.get_price(
                product,
                datetime.strptime('2021-04-01 12:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
            )
        )
        
