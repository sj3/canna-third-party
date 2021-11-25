import logging
import os

import odoo.tests.common as common

_logger = logging.getLogger(__name__)


class TestGeoenginePartner(common.TransactionCase):
    def setUp(self):
        super(TestGeoenginePartner, self).setUp()
        api_key = os.getenv("MAPBOX_API_KEY")
        _logger.info("Setting Mapbox API key to %s", api_key)
        self.env["ir.config_parameter"].set_param("mapbox.client_id", api_key)

    def test_geo_localize(self):
        test_data = [
            {
                "partner": {
                    "name": "Partner Project",
                    "street": "Rue au bois la dame",
                    "country_id": self.env.ref("base.be").id,
                    "zip": "6800",
                },
                "coordinates": {"latitude": 50.0, "longitude": 5.4},
            },
            {
                "partner": {
                    "name": "Partner Project",
                    "street": "PO 58059",
                    "country_id": self.env.ref("base.nl").id,
                    "zip": "1040HB",
                    "city": "amsterdam",
                },
                "coordinates": {"latitude": 52.4, "longitude": 4.9},
            },
            {
                "partner": {
                    "name": "Partner Project",
                    "street": "Taapuna lot 181",
                    "city": "Punaauia",
                    "zip": "98717",
                    "country_id": self.env.ref("base.pf").id,
                },
                "coordinates": {"latitude": -17.6, "longitude": -149.6},
            },
        ]

        for test_record in test_data:
            partner_id = self.env["res.partner"].create(test_record["partner"])
            partner_id.name = "Other Partner"
            vals = partner_id.get_mapbox_location()

            self.assertAlmostEqual(
                vals["partner_latitude"],
                test_record["coordinates"]["latitude"],
                1,
                "Latitude Should be equals",
            )
            self.assertAlmostEqual(
                vals["partner_longitude"],
                test_record["coordinates"]["longitude"],
                1,
                "Longitude Should be equals",
            )
