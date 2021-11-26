# Copyright 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
from urllib.parse import quote_plus

from odoo import fields, models

try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Requests is not available in the sys path")

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def geo_localize(self):
        mapbox_client_id = (
            self.env["ir.config_parameter"].sudo().get_param("mapbox.client_id")
        )
        if not mapbox_client_id:
            return super().geo_localize()

        for partner in self:
            partner.write(partner.get_mapbox_location())

        return True

    def get_mapbox_location(self):
        self.ensure_one()

        result = {
            "partner_latitude": 0,
            "partner_longitude": 0,
            "date_localization": fields.Date.today(),
        }

        mapbox_client_id = self.env["res.company"].get_mapbox_api_key()

        if not mapbox_client_id:
            return result

        # For info about geocodeing format, see:
        # https://docs.mapbox.com/help/troubleshooting/address-geocoding-format-guide/
        # #addresses-in-multiple-countries
        pay_loads = [
            [
                ",".join(
                    map(
                        quote_plus,
                        filter(
                            None,
                            [
                                self.street or "",
                                self.zip or "",
                                self.city or "",
                                self.state_id and self.state_id.name or "",
                                self.street2,
                            ],
                        ),
                    )
                )
            ],
            [
                ",".join(
                    map(
                        quote_plus,
                        filter(
                            None,
                            [
                                self.zip or "",
                                self.city or "",
                                self.state_id and self.state_id.name or "",
                            ],
                        ),
                    )
                )
            ],
            [
                ",".join(
                    map(
                        quote_plus,
                        filter(None, [self.state_id and self.state_id.name or ""]),
                    )
                )
            ],
        ]

        headers = requests.utils.default_headers()
        headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) snap "
                "Chromium/80.0.3987.100 Chrome/80.0.3987.100 Safari/537.36"
            }
        )

        for pay_load in pay_loads:
            if not pay_load[0]:
                continue

            session = requests.Session()
            adapter = HTTPAdapter(max_retries=0)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
            url += pay_load[0] + ".json"
            lang_code = self.lang or "en_US"
            mb_params = {
                "country": self.country_id.code if self.country_id else "",
                "autocomplete": False,
                "access_token": mapbox_client_id,
                "limit": 1,
                "language": lang_code.split("_")[0],
            }

            try:
                request_result = session.get(
                    url, params=mb_params, timeout=5.0, headers=headers
                )
                request_result.raise_for_status()
                result_vals = request_result.json()

                if len(result_vals.get("features", [])):
                    feature = result_vals["features"][0]
                    result.update(
                        {
                            "partner_latitude": feature.get("center", [0, 0])[1],
                            "partner_longitude": feature.get("center", [0, 0])[0],
                        }
                    )
                    break
                else:
                    _logger.debug(
                        "No Mapbox geocoding result for partner %s: %s",
                        self.id,
                        pay_load,
                    )

            except Exception as e:
                _logger.exception("Mapbox geocoding error: %s", str(e))
        else:
            _logger.warning(
                "No Mapbox geocoding result for partner %s: %s", self.id, pay_loads[0]
            )

        return result
