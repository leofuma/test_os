# -*- coding: utf-8 -*-

from openerp import api, models, fields


class ResUsersRole(models.Model):
    _inherit = 'res.users.role'

    @api.model
    def create(self, vals):
        record = super(ResUsersRole, self).create(vals)
        if not self._context.get('avoid_clear_caches', False):
            self.env['res.groups'].clear_caches()
        return record


    @api.multi
    def write(self, vals):
        res = super(ResUsersRole, self).write(vals)
        if 'implied_ids' in vals:
            self.env['res.groups'].clear_caches()
        return res

    @api.multi
    def unlink(self):
        associated_groups = self.mapped('group_id')
        res = super(ResUsersRole, self).unlink()
        if not self._context.get('avoid_clear_caches', False):
            self.env['res.groups'].clear_caches()
        if associated_groups:
            associated_groups.unlink()
        return res
