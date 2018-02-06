from openerp import models, SUPERUSER_ID
from openerp.tools.safe_eval import safe_eval


class IrActionsAct_window(models.Model):
    _inherit = 'ir.actions.act_window'

    def read(self, cr, uid, ids, fields=None,
             context=None, load='_classic_read'):
        act = res = super(IrActionsAct_window, self).read(
            cr, uid, ids, fields=fields, context=context, load=load)

        if isinstance(res, list):
            act = res[0]

        if uid != SUPERUSER_ID and \
           act.get('res_model', False) and \
           self.pool.get(act['res_model'], False) and \
           'operating_unit_id' in self.pool[act['res_model']]._fields:

            user_ou = self.pool.get('res.users').read(
                cr, SUPERUSER_ID, uid, [
                    'default_operating_unit_id'])[
                        'default_operating_unit_id']

            if not user_ou:
                return res

            if act.get('domain', False):
                try:
                    act_ctx = safe_eval(act.get('domain', ''))
                    act_ctx.append(
                        ('operating_unit_id', 'in', [False, user_ou[0]]))
                    act['domain'] = str(act_ctx)
                except ValueError:
                    pass
            else:
                act['domain'] = str([
                    ('operating_unit_id', 'in', [False, user_ou[0]])])

        return res
