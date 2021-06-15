# Copyright 2017-2021 startx
# Copyright 2021 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class BaseOperatingUnitIsolation(models.AbstractModel):
    _name = "base_operating_unit_isolation"
    _description = "Extend AbstractModel for Operation Unit Isolation"

    def _register_hook(self):
        @api.model
        def _ou_search(
            self,
            args,
            offset=0,
            limit=None,
            order=None,
            count=False,
            access_rights_uid=None,
        ):
            record = self.env.context.get("record")
            if (
                record
                and "operating_unit_id" in self._fields
                and record.get("_field")
                and "_name" in record
                and record["_name"] in self.env
                and record["_field"] in self.env[record["_name"]]._fields
            ):
                fld = self.env[record["_name"]]._fields[record["_field"]]
                if getattr(fld, "operating_unit_isolation", False):
                    isolation = fld.operating_unit_isolation.split(".")
                    filter_ou = False
                    if len(isolation) == 2:
                        # import pdb; pdb.set_trace()
                        parent_record = self.env.context["parent_record"]
                        if (
                            "_o2m" in parent_record
                            and isolation[0] == parent_record["_o2m"]
                        ):
                            filter_ou = parent_record.get(isolation[1])
                    elif len(isolation) == 1:
                        filter_ou = record.get(isolation[0])
                    if filter_ou:
                        args.append(("operating_unit_id", "in", [False, filter_ou]))

            return _ou_search.origin(
                self,
                args,
                offset=offset,
                limit=limit,
                order=order,
                count=count,
                access_rights_uid=access_rights_uid,
            )

        ou_patched = getattr(models.BaseModel, "ou_patch", None)
        if not ou_patched:
            models.BaseModel._patch_method("_search", _ou_search)
            models.BaseModel.ou_patched = True

        return super()._register_hook()
