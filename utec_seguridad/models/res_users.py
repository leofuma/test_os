# -*- coding: utf-8 -*-

from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.osv.orm import setup_modifiers
from datetime import date
from lxml import etree


class Users(models.Model):
    _inherit = 'res.users'
    _rec_name = 'id'

    job_id = fields.Many2one('hr.job', 'Cargo')
    user_profile_ids = fields.One2many('res.users.security.profile', 'user_id', string="Perfiles")
    groups_readonly = fields.Boolean(compute="_compute_groups_readonly", hide=True)


    def __init__(self, pool, cr):
        cr.execute("SELECT column_name FROM information_schema.columns WHERE table_name='res_users' and column_name='job_id'")
        if not cr.fetchone():
            cr.execute('ALTER TABLE public.res_users ADD COLUMN job_id integer')
        super(Users, self).__init__(pool, cr)

    @api.depends('role_line_ids', 'role_line_ids.date_from', 'role_line_ids.date_to')
    def _compute_groups_readonly(self):
        for user in self:
            user.groups_readonly = any([role_line.is_enabled for role_line in user.role_line_ids])

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            user_profile_ids = [(5, 0)]
            domain = [('job_id', '=', self.job_id.id)]
            if self.employee_ids:
                dep_ids = self.employee_ids.mapped('department_id').ids
                domain += ['|',('department_id','=',False),('department_id','in',dep_ids)]
            profiles = self.env['security.profile.job'].search(domain).mapped('profile_id')
            user_profile_ids += [(0, 0, {'profile_id': profile.id}) for profile in profiles]
            self.user_profile_ids = user_profile_ids

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Users, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc = etree.fromstring(res['arch'])
            group_nodes = doc.xpath("//field[contains(@name, 'in_group_')]") + doc.xpath("//field[contains(@name, 'sel_groups_')]")
            for node in group_nodes:
                node.set('attrs', "{'readonly': [('groups_readonly','=',True)]}")
                setup_modifiers(node)
            res['arch'] = etree.tostring(doc)
        return res

    @api.model
    def create(self, vals):
        obj_seq = self.env['ir.sequence']
        if vals.get('user_id', 'New') == 'New':
            f = obj_seq.next_by_code('res_users_id_seq')
            vals['user_id'] = f
        record = super(Users, self).create(vals)
        record.sudo().set_role_lines_from_profiles()
        return record

    @api.multi
    def write(self, vals):

        res = super(Users, self).write(vals)
        self.sudo().set_role_lines_from_profiles()
        return res

    @api.multi
    def set_role_lines_from_profiles(self):
        for user in self:
            if user.id == SUPERUSER_ID:
                continue
            role_line_ids = [(2, _id) for _id in user.role_line_ids.ids]
            for profile_line in user.user_profile_ids:
                for role in profile_line.profile_id.role_ids:
                    role_line_ids.append((0, 0, {
                        'role_id': role.id,
                        'date_from': profile_line.date_from,
                        'date_to': profile_line.date_to,
                    }))
            super(Users, user).write({'role_line_ids': role_line_ids})
        return True


class UsersSecurityProfile(models.Model):
    _name = 'res.users.security.profile'
    _description = 'Usuario Perfil de seguridad'

    user_id = fields.Many2one('res.users', 'Usuario', required=True, ondelete="cascade", index=True)
    profile_id = fields.Many2one('security.profile', 'Perfil', required=True)
    date_from = fields.Date("Desde")
    date_to = fields.Date("Hasta")
    is_enabled = fields.Boolean("Activado", compute='_compute_is_enabled')

    @api.depends('date_from', 'date_to')
    def _compute_is_enabled(self):
        today = date.today()
        for line in self:
            line.is_enabled = True
            if line.date_from:
                date_from = fields.Date.from_string(line.date_from)
                if date_from > today:
                    line.is_enabled = False
            if line.date_to:
                date_to = fields.Date.from_string(line.date_to)
                if today > date_to:
                    line.is_enabled = False

    @api.multi
    def unlink(self):
        users = self.mapped('user_id')
        res = super(UsersSecurityProfile, self).unlink()
        users.set_role_lines_from_profiles()
        return res
