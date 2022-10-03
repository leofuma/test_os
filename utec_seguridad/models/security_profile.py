# -*- coding: utf-8 -*-

from openerp import fields, models, api


class SecurityProfile(models.Model):
    _name = "security.profile"
    _description = "Perfil de seguridad"
    _order = 'create_date desc, id desc'
    _rec_name = 'profile_id'


    profile_id = fields.Integer('profile id')
    name = fields.Char("Nombre", required=True)
    create_date = fields.Datetime(u'Fecha de creación', readonly=True)
    role_ids = fields.Many2many("res.users.role", "security_profile_user_role_rel",
                                'profile_id', 'role_id', string="Roles")
    group_ids = fields.Many2many('res.groups', string='Grupos', compute="_compute_group_info")
    user_ids = fields.Many2many('res.users', string='Usuarios', compute="_compute_user_ids")
    group_category_ids = fields.Many2many('ir.module.category', string='Aplicaciones', compute="_compute_group_info")
    profile_job_ids = fields.One2many('security.profile.job', 'profile_id', string="Cargos")
    description = fields.Text(u'Descripción')

    @api.depends('role_ids', 'role_ids.implied_ids')
    def _compute_group_info(self):
        for profile in self:
            profile.group_ids = profile.role_ids.mapped('trans_implied_ids')
            profile.group_category_ids = profile.group_ids.mapped('category_id')

    @api.multi
    def _compute_user_ids(self):
        for profile in self:
            user_profiles = self.env['res.users.security.profile'].search([('profile_id', '=', profile.id)])
            profile.user_ids = user_profiles.filtered(lambda x: x.is_enabled).mapped('user_id')

    @api.model
    def create(self, vals):
        #  Here be change .write(vals) to .create(vals) because error record = True...
        record = super(SecurityProfile, self).create(vals)
        if record.role_ids:
            user_profiles = self.env['res.users.security.profile'].search([('profile_id','=',record.id)])
            users = user_profiles.filtered(lambda x: x.is_enabled).mapped('user_id')
            if users:
                users.set_role_lines_from_profiles()
        return record

    @api.multi
    def write(self, vals):
        res = super(SecurityProfile, self).write(vals)
        if 'role_ids' in vals and self:
            user_profiles = self.env['res.users.security.profile'].search([('profile_id','in',self.ids)])
            users = user_profiles.filtered(lambda x: x.is_enabled).mapped('user_id')
            if users:
                users.set_role_lines_from_profiles()
        return res


class SecurityProfileJob(models.Model):
    _name = "security.profile.job"
    _description = "Cargo en Perfil de seguridad"
    _rec_name = 'job_id'

    profile_id = fields.Many2one("security.profile", "Perfil de seguridad", required=True, ondelete="cascade", index=True)
    job_id = fields.Many2one('hr.job', 'Cargo', required=True)
    department_id = fields.Many2one('hr.department', u'Área/Carrera')

    _sql_constraints = [
        ('job_department_uniq', 'unique(profile_id, job_id, department_id)', u'Ya existe esta combinación de Cargo y Área/Carrera para este perfil')
    ]


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_profile') and self._context.get('dep_id'):
            query = "SELECT DISTINCT job_id FROM hr_employee WHERE department_id=%s and job_id is not null"
            self._cr.execute(query, (self._context['dep_id'],))
            ids = [x[0] for x in self._cr.fetchall()]
            args = [('id', 'in', ids)] + (args or [])
        if self._context.get('filter_by_employee') and self._context.get('user_id') and isinstance(self._context['user_id'], (int, long)):
            user = self.env['res.users'].sudo().browse(self._context['user_id'])
            if user.exists() and user.employee_ids:
                ids = user.employee_ids.mapped('job_id').ids
                args = [('id', 'in', ids)] + (args or [])
        return super(HrJob, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_profile') and self._context.get('job_id'):
            query = "SELECT DISTINCT department_id FROM hr_employee WHERE job_id=%s and department_id is not null"
            self._cr.execute(query, (self._context['job_id'],))
            ids = [x[0] for x in self._cr.fetchall()]
            args = [('id', 'in', ids)] + (args or [])
        return super(HrDepartment, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)
