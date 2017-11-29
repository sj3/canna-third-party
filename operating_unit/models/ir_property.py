# -*- coding: utf-8 -*-
# Copyright 2017 Noviat.
# Copyright 2017 Onestein BV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


class IrProperty(models.Model):
    """Override of IrProperty to enable the usage of Company Properties on
    Operating Units. Uses a lot of the standard Odoo code.
    """
    _inherit = 'ir.property'

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', select=1)

    @api.model
    def get(self, name, model, res_id=False):
        """
        Retrieve the default value for the property field.
        Overrides the original method without using super.
        :param name: Property name
        :param model: Model name
        :param res_id:
        :return: Default value of the record or False.
        """
        domain = self._get_domain(name, model)
        if domain is not None:
            domain = [('res_id', '=', res_id)] + domain
            # Perform the search with operating_unit_id asc and company_id
            # asc to ensure that properties specific to a operating unit are
            # given first.
            record = self.search(
                domain, limit=1, order='operating_unit_id asc, company_id asc')
            if not record:
                return False
            return self.get_by_record(record)
        return False

    @api.model
    def _get_domain(self, prop_name, model):
        """
        Returns a domain which can be used to check the existence of a relevant
        property record based on the user's company and operating unit.
        :param prop_name: Property field's name.
        :param model: Model name.
        :return: None or a domain.
        """
        # TODO optional: force_operating_unit.
        res = super(IrProperty, self)._get_domain(prop_name, model)
        if res:
            user = self.env['res.users'].browse(self._uid)
            ouid = user._get_operating_unit().ids
            ou_rule = ('operating_unit_id', 'in', [ouid, False])
            res.append(ou_rule)
            return res
        else:
            return None

    @api.model
    def get_multi(self, name, model, ids):
        """ Read the property field `name` for the records of model `model` with
            the given `ids`, and return a dictionary mapping `ids` to their
            corresponding value.
            Overrides the original method without using super.
            :param name: Field name.
            :param model: Model name.
            :param ids: List of relevant ids.
            :return: Dict mapping ids to corresponding value.
        """
        if not ids:
            return {}

        domain = self._get_domain(name, model)
        if domain is None:
            return dict.fromkeys(ids, False)

        # Retrieve the values for the given ids and the default value, too.
        refs = {('%s,%s' % (model, id)): id for id in ids}
        refs[False] = False
        domain += [('res_id', 'in', list(refs))]

        # Note: order by 'company_id asc' will return non-null values first.
        props = self.search(
            domain, order='operating_unit_id asc, company_id asc')
        result = {}
        for prop in props:
            # For a given res_id, take the first property only.
            id = refs.pop(prop.res_id, None)
            if id is not None:
                result[id] = self.get_by_record(prop)

        # Set the default value to the ids that are not in result.
        default_value = result.pop(False, False)
        for id in ids:
            result.setdefault(id, default_value)

        return result

    @api.model
    def set_multi(self, name, model, values):
        """ Assign the property field `name` for the records of model `model`
            with `values` (dictionary mapping record ids to their value).
            Writes changes or creates a new property record if it does not
            exist yet.
            Overrides the original method without using super.
            To use super, try to separate method into multiple methods for
            reading input data, updating and creating.
            :param name: Property field's name.
            :param model: Model name.
            :param values: Values to modify; {local record: property related
            record}.
            :return: None.
        """
        def clean(value):
            return value.id if isinstance(value, models.BaseModel) else value

        if not values:
            return

        domain = self._get_domain(name, model)
        if domain is None:
            raise Exception()

        # Retrieve the default value for the field.
        default_value = clean(self.get(name, model))

        # Retrieve the properties corresponding to the given record ids.
        self._cr.execute("SELECT id FROM ir_model_fields WHERE name=%s AND model=%s", (name, model))
        field_id = self._cr.fetchone()[0]
        company_id = self.env.context.get('force_company') or self.env['res.company']._company_default_get(model, field_id)
        operating_unit_id = self.env['res.users']._get_operating_unit().id
        refs = {('%s,%s' % (model, id)): id for id in values}
        props = self.search([
            ('fields_id', '=', field_id),
            ('company_id', '=', company_id),
            ('operating_unit_id', '=', operating_unit_id),
            ('res_id', 'in', list(refs)),
        ])

        # Modify existing properties.
        for prop in props:
            id = refs.pop(prop.res_id)
            value = clean(values[id])
            if value == default_value:
                prop.unlink()
            elif value != clean(prop.get_by_record(prop)):
                prop.write({'value': value})

        # Create new properties for records that do not have one yet.
        for ref, id in refs.iteritems():
            value = clean(values[id])
            if value != default_value:
                self.create({
                    'fields_id': field_id,
                    'company_id': company_id,
                    'operating_unit_id': operating_unit_id,
                    'res_id': ref,
                    'name': name,
                    'value': value,
                    'type': self.env[model]._fields[name].type,
                })
