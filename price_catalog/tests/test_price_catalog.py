import logging
import os

from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tests import common

_logger = logging.getLogger(__name__)

directory = os.path.dirname(__file__)


class TestPriceCatalog(common.TransactionCase):
    def setUp(self):
        super(TestPriceCatalog, self).setUp()

    def test_createCatalog(self):
        catalog = self.env["price.catalog"].create(
            {"name": "UNITTEST CATALOG", "catalog_type": "sale"}
        )

        subcatalog = self.env["price.subcatalog"].create(
            {"name": "UNITTEST v1", "catalog_id": catalog.id}
        )

        self.env["price.catalog.item"].create(
            {
                "subcatalog_id": subcatalog.id,
                "product_id": self.env.ref("product.product_delivery_01").id,
                "price": 7,
            }
        )

        with self.assertRaises(IntegrityError):
            self.env["price.catalog.item"].create(
                {
                    "subcatalog_id": subcatalog.id,
                    "product_id": self.env.ref("product.product_delivery_01").id,
                    "price": 9,
                }
            )

    # def test_createCatalogWithoutStartDate(self):
    #     catalog = self.env['price.catalog'].create({
    #         'name': "UNITTEST CATALOG",
    #         'catalog_type': 'sale',
    #     })

    #     with self.assertRaises(IntegrityError):
    #         subcatalog = self.env['price.subcatalog'].create({
    #             'name': "UNITTEST v1",
    #             "catalog_id": catalog.id,
    #             'start_date': False,
    #         })

    def test_createOverlapWithInactiveCatalog(self):
        catalog = self.env["price.catalog"].create(
            {"name": "UNITTEST CATALOG", "catalog_type": "sale"}
        )

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST v1",
                "catalog_id": catalog.id,
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
                "active": False,
            }
        )

        with self.assertRaises(ValidationError):
            self.env["price.subcatalog"].create(
                {
                    "name": "UNITTEST subcatalog overlap",
                    "catalog_id": catalog.id,
                    "start_date": "2019-01-01",
                    "end_date": "2020-01-31",
                }
            ).unlink()

    def test_createOverlappingSubcatalog(self):
        catalog = self.env["price.catalog"].create(
            {"name": "UNITTEST CATALOG", "catalog_type": "sale"}
        )

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST v1",
                "catalog_id": catalog.id,
                "start_date": "2020-01-01",
                "end_date": "2020-12-31",
            }
        )

        # before
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog before",
                "catalog_id": catalog.id,
                "start_date": "2019-01-01",
                "end_date": "2019-12-31",
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog before no start",
                "catalog_id": catalog.id,
                "start_date": False,
                "end_date": "2019-12-31",
            }
        ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog before no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # overlap start

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": "2020-12-31",
                    }
                ).unlink()

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no start",
                        "catalog_id": catalog.id,
                        "start_date": False,
                        "end_date": "2022-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # after

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": "2023-12-31",
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after no start",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": False,
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after no end",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": False,
            }
        ).unlink()

    def test_createOverlappingSubcatalogOpenEnd(self):
        catalog = self.env["price.catalog"].create(
            {"name": "UNITTEST CATALOG", "catalog_type": "sale"}
        )

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST v1",
                "catalog_id": catalog.id,
                "start_date": "2020-01-01",
                "end_date": False,
            }
        )

        # before

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog before",
                "catalog_id": catalog.id,
                "start_date": "2019-01-01",
                "end_date": "2019-12-31",
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog before no start",
                "catalog_id": catalog.id,
                "start_date": False,
                "end_date": "2019-12-31",
            }
        ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog before no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # overlap start

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": "2020-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no start",
                        "catalog_id": catalog.id,
                        "start_date": False,
                        "end_date": "2022-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # after

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog after",
                        "catalog_id": catalog.id,
                        "start_date": "2022-12-31",
                        "end_date": "2023-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog after no start",
                        "catalog_id": catalog.id,
                        "start_date": "2022-12-31",
                        "end_date": False,
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog after no end",
                        "catalog_id": catalog.id,
                        "start_date": "2022-12-31",
                        "end_date": False,
                    }
                ).unlink()

    def test_createOverlappingSubcatalogOpenStart(self):
        catalog = self.env["price.catalog"].create(
            {"name": "UNITTEST CATALOG", "catalog_type": "sale"}
        )

        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST v1",
                "catalog_id": catalog.id,
                "start_date": False,
                "end_date": "2020-12-31",
            }
        )

        # before

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog before",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": "2019-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog before no start",
                        "catalog_id": catalog.id,
                        "start_date": False,
                        "end_date": "2019-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog before no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # overlap start

        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": "2020-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no start",
                        "catalog_id": catalog.id,
                        "start_date": False,
                        "end_date": "2022-12-31",
                    }
                ).unlink()
        with self.assertRaises(ValidationError):
            with self.env.cr.savepoint():
                self.env["price.subcatalog"].create(
                    {
                        "name": "UNITTEST subcatalog overlap no end",
                        "catalog_id": catalog.id,
                        "start_date": "2019-01-01",
                        "end_date": False,
                    }
                ).unlink()

        # after
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": "2023-12-31",
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after no start",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": False,
            }
        ).unlink()
        self.env["price.subcatalog"].create(
            {
                "name": "UNITTEST subcatalog after no end",
                "catalog_id": catalog.id,
                "start_date": "2022-12-31",
                "end_date": False,
            }
        ).unlink()
