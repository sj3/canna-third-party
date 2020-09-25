# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

import requests
from openerp import api, fields, models

URL_TOKEN = "https://login.bol.com/token"


class BolcomAuthentication(models.Model):
    _name = "bolcom.authentication"

    access_token = fields.Char(string="Access Token")
    token_type = fields.Char(string="Token Type")
    expiration = fields.Datetime(string="Expiration Time in seconds")
    scope = fields.Char()
    name = fields.Char()

    @api.model
    def get_token(self, existing_token=False):
        """
        Fetch a new access token
        """
        res = False
        is_exist_not_expired = True
        if existing_token:
            now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            is_exist_not_expired = len(
                self.search(
                    [("access_token", "=", existing_token), ("expiration", ">", now_s)]
                )
            )
            res = existing_token
        if not existing_token or not is_exist_not_expired:
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }
            data = {
                "client_id": self.env.user.company_id.bolcom_client_id,
                "client_secret": self.env.user.company_id.bolcom_secret,
                "grant_type": "client_credentials",
            }
            now = datetime.now()
            resp = requests.post(URL_TOKEN, headers=headers, data=data)
            resp.raise_for_status()
            if resp.status_code == 200:
                vals = resp.json()
                vals["expiration"] = now + timedelta(seconds=vals.pop("expires_in"))
                if self.create(vals):
                    res = vals["token_type"] + " " + vals["access_token"]
                    res = res.encode("ascii")
        return res

    def check_token(self):
        """
        Checks if the token is still valid
        """
        if not self.expiration:
            return False
        now = datetime.now()
        if self.expiration < now:  # refresh token
            self.get_token()
        return True

    @api.model
    def request_resource(
        self,
        token,
        resource,
        id=False,
        data=False,
        demo=False,
        media="application/vnd.retailer.v3+json",
        query=False,
        method="get",
    ):
        data = data or {}
        headers = {
            "Content-Type": media,
            "Accept": media,
            "Authorization": token,
        }
        url = self.env.user.company_id.bolcom_url
        if demo:
            url += "-demo"
        url += "/" + resource
        if id:
            url += "/" + str(id)
        if query:
            url += "?" + query
        if method == "post":
            resp = requests.post(url, headers=headers, data=data)
        elif method == "get":
            resp = requests.get(url, headers=headers, data=data)
        else:
            resp = requests.get(url, headers=headers, data=data)
        resp.raise_for_status()
        if resp.status_code == 200:
            vals = resp.json()
            return vals
        return {}
