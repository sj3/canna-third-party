# Copyright 2020 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging
import urllib.parse

from odoo import api, exceptions, fields, models
from odoo.tools.translate import _

try:
    import requests
    from requests.exceptions import Timeout, ConnectionError, HTTPError
    from requests.adapters import HTTPAdapter
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("requests is not available in the sys path")

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    _inherit = "res.partner"

    date_localization = fields.Datetime(string="Geolocation Date")
    partner_latitude = fields.Float(tracking=True)
    partner_longitude = fields.Float(tracking=True)
    mapbox_error = fields.Text()

    def send_mapbox_fail_mail(self, error):
        template = self.env.ref("geoengine_mapbox.email_template_mapbox_call_fail")
        feedback_email = (
            self.env["ir.config_parameter"].sudo().get_param("mapbox.feedback_email")
        )
        for partner in self:
            partner.write({"mapbox_error": error})
            template.write({"email_to": feedback_email})
            template.send_mail(partner.id, force_send=True)

    @api.model
    def get_mapbox_client_id(self):
        return self.env["ir.config_parameter"].sudo().get_param(
            "mapbox.client_id")

    @api.model
    def get_geo_vals_osm(self):
        """Get the latitude and longitude from nominatim.
        """
        result = {
            "partner_latitude": 0,
            "partner_longitude": 0,
            "date_localization": fields.Date.today(),
        }

        territory_to_country_code = {
            "PF": "FR",
        }

        def get_state():
            if not partner.state_id:
                return ""
            return partner.state_id.name

        def get_countrycodes():
            if not self.country_id:
                return ""

            code = self.country_id.code

            return territory_to_country_code.get(
                code, code)

        url = "https://nominatim.openstreetmap.org/search"
        pay_loads = [
            {
                "street": self.street or "",
                "postalcode": self.zip or "",
                "city": self.city or "",
                "state": self.state_id and self.state_id.name or "",
                "countrycodes": get_countrycodes(),
            },
            {
                "city": self.city or "",
                "state": self.state_id and self.state_id.name or "",
                "countrycodes": get_countrycodes(),
            },
            {
                "city": self.city or "",
                "countrycodes": get_countrycodes(),
            },
        ]
        vals = []
        headers = requests.utils.default_headers()
        headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) snap "
                "Chromium/80.0.3987.100 Chrome/80.0.3987.100 Safari/537.36"
            }
        )
        for pay_load in pay_loads:
            try:
                session = requests.Session()
                adapter = HTTPAdapter(max_retries=0)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                pay_load.update(
                    {"limit": 1, "format": "json", "addressdetails": 1}
                )
                request_result = session.get(
                    url, params=pay_load, timeout=5.0, headers=headers
                )
                request_result.raise_for_status()
                vals = request_result.json()
                if len(vals):
                    result.update({
                        "partner_latitude":
                        vals[0].get("lat") or 0,
                        "partner_longitude":
                        vals[0].get("lon") or 0,
                    })

            except Timeout:
                continue
            except ConnectionError as e:
                _logger.exception("Geocoding error: %s" % e)
                raise exceptions.UserError(_("Please check your internet connection!"))
                #                raise exceptions.Warning(_(
                #                    "Geocoding error.\n"
                #                    "Try pressing save again.\n\n"
                #                    "If it still doesn't work open a ticket "
                #                    "with the following information. \n"
                #                    "%s") % e.message)
                continue
            except HTTPError:
                continue

            if result['partner_latitude'] != 0:
                break
        self.write(result)

    def get_mapbox_location(self):
        def get_state():
            if not partner.state_id:
                return ""
            return partner.state_id.name

        result = {
            "partner_latitude": 0,
            "partner_longitude": 0,
            "date_localization": fields.Date.today(),
        }

        mapbox_client_id = self.get_mapbox_client_id()


        pay_loads = [
            [",".join(filter(None, [
                self.street or "",
                self.street2 or "",
                self.city or "",
                self.zip or "",
                self.state_id and self.state_id.name or "",
            ]))],
            [",".join(filter(None, [
                self.city or "",
                self.state_id and self.state_id.name or "",
            ]))],
            [",".join(filter(None, [
                self.state_id and self.state_id.name or "",
            ]))],
        ]

        result_vals = []
        headers = requests.utils.default_headers()
        headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) snap "
                "Chromium/80.0.3987.100 Chrome/80.0.3987.100 Safari/537.36"
            }
        )

        for pay_load in pay_loads:
            session = requests.Session()
            adapter = HTTPAdapter(max_retries=0)
            session.mount("http://", adapter)
            session.mount("https://", adapter)

            url = "https://api.mapbox.com/geocoding/v5/mapbox.places/"
            url += pay_load[0] + ".json"
            lang_code = self.lang or "en_US"
            mb_params = {
                "country": self.country_id.code
                if self.country_id else "",
                "autocomplete": False,
                "access_token": mapbox_client_id,
                "limit": 1,
                "language": lang_code.split('_')[0],
            }

            try:
                request_result = session.get(
                    url, params=mb_params,
                    timeout=5.0, headers=headers
                )

                if request_result.status_code == 401:
                    _logger.exception("Geocoding error: Wrong Mapbox key")
                    self.send_mapbox_fail_mail("Wrong Mapbox key")
                    self.get_geo_vals_osm()
                    break

                result_vals = request_result.json()
                if len(result_vals.get('features', [])):
                    feature = result_vals['features'][0]
                    result.update({
                        "partner_latitude":
                        feature.get("center", [0, 0])[1],
                        "partner_longitude":
                        feature.get("center", [0, 0])[0],
                    })
            except Exception as e:
                # Fallback to nominatim and mail the error
                _logger.exception("Geocoding error", str(e))
                self.send_mapbox_fail_mail(str(e))
                self.get_geo_vals_osm()
            if result['partner_latitude'] != 0:
                break

        self.write(result)
