# Copyright 2024 Canna
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
from collections import defaultdict
from datetime import datetime, timedelta
from urllib.request import urlopen

from odoo import fields, models


class ResCurrencyRateProviderCNB(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(selection_add=[("CNB", "Czech National Bank")])

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "CNB":
            return super()._get_supported_currencies()  # pragma: no cover

        return [
            "AUD",
            "BRL",
            "BGN",
            "CNY",
            "DKK",
            "EUR",
            "PHP",
            "HKD",
            "INR",
            "IDR",
            "ISK",
            "ILS",
            "JPY",
            "ZAR",
            "CAD",
            "KRW",
            "HUF",
            "MYR",
            "MXN",
            "XDR",
            "NOK",
            "NZD",
            "PLN",
            "RON",
            "SGD",
            "SEK",
            "CHF",
            "THB",
            "TRY",
            "USD",
            "GBP",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "CNB":
            return super()._obtain_rates(base_currency, currencies, date_from, date_to)
        content = defaultdict(dict)
        while date_from <= date_to:
            date = date_from.strftime("%d.%m.%Y")
            url = (
                f"https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/"
                f"kurzy-devizoveho-trhu/denni_kurz.txt?date={date}"
            )
            with urlopen(url) as response:
                response = response.read().decode("utf-8").splitlines()
                date = datetime.strptime(response[0].split(" ")[0], "%d.%m.%Y").date()
                reader = csv.DictReader(response[1:], delimiter="|")
                for row in reader:
                    if row["kód"] in currencies:
                        content[date][row["kód"]] = str(
                            1.0
                            / (
                                float(row["kurz"].replace(",", "."))
                                / float(row["množství"])
                            )
                        )
            date_from += timedelta(days=1)
        return content
