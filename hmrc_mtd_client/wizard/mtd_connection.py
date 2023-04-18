# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import odoolib
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, RedirectWarning

_logger = logging.getLogger(__name__)


class MtdConnection(models.TransientModel):
    _name = 'mtd.connection'
    _description = "MTD connection control"

    def open_connection_odoogap(self):
        """opens the connection to the mtd server
        Returns:
            [odoorpc] -- odoorpc object
        """
        try:
            params = self.env['ir.config_parameter'].sudo()
            login = params.get_param('mtd.login', default=False)
            password = params.get_param('mtd.password', default=False)
            server = params.get_param('mtd.server.api', default=False)
            db = params.get_param('mtd.db', default=False)
            port = params.get_param('mtd.port', default=False)

            odoo_instance = odoolib.get_connection(hostname=server, protocol='jsonrpcs', port=int(port),
                                                    database=db, login=login, password=password)
            # odoo_instance = odoorpc.ODOO(server, protocol='jsonrpc', port=int(port))
            # odoo_instance.login(db, login, password)
            operations = odoo_instance.get_model('mtd.operations')
            return operations
        except Exception as e:
            logging.error('Invalid connection %s' % str(e))
            raise UserError('Invalid user.')

    def get_authorization(self):
        """starts HMRC authorization flow
        Returns:
            [dict] -- [redirect url action]
        """
        conn = self.open_connection_odoogap()
        mtd_sandbox = self.env['ir.config_parameter'].sudo().get_param('mtd.sandbox', default=False)
        response = conn.authorize(mtd_sandbox)

        if response.get('status') == 200:
            self.env['ir.config_parameter'].sudo().set_param('mtd.hmrc.url', response.get('mtd_url'))
            client_action = {
                'type': 'ir.actions.act_url',
                'name': "HMRC authentication",
                'target': 'new',
                'url': response.get('message')
            }

            return client_action

        raise UserError('An error has occurred : \n status: %s \n message: %s ' % (
            str(response.get('status')),
            response.get('message')
        ))

    def refresh_token(self):
        """refreshs HMRC token
        Returns:
            [type] -- [HMRC token]
        """
        conn = self.open_connection_odoogap()
        mtd_sandbox = self.env['ir.config_parameter'].sudo().get_param('mtd.sandbox', default=False)
        response = conn.refresh_token(mtd_sandbox)

        channel_id = self.env.ref('hmrc_mtd_client.channel_mtd_token')

        if response.get('status') == 200:
            set_param = self.env['ir.config_parameter'].sudo().set_param
            set_param('mtd.token', response.get('message').get('token'))
            set_param('mtd.token_expire_date', response.get('message').get('exp_date'))
            channel_id.message_post(body='Token refreshed successfully', message_type="notification",
                                    subtype="mail.mt_comment")
            return response.get('message').get('token')

        else:
            message_body = 'An error has occurred : <b>status:</b> %s - <b>message:</b> %s' % (
                str(response.get('status')), response.get('message'))
            channel_id.message_post(body=message_body, message_type="notification",
                                    subtype="mail.mt_comment")

    def get_token(self):
        """stores the HMRC token in the system
        """
        conn = self.open_connection_odoogap()
        print('calling get token')
        response = conn.get_token()
        print(response)
        if response.get('status') == 200:
            set_param = self.env['ir.config_parameter'].sudo().set_param
            set_param('mtd.token', response.get('message').get('token'))
            set_param('mtd.token_expire_date', response.get('message').get('exp_date'))

        else:
            raise UserError(
                'An error has occurred : \n status: %s\n message: %s' % (
                    str(response.get('status')),
                    response.get('message')
                ))
