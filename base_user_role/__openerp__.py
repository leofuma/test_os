# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'User roles',
    'version': '8.0.1.0.1',
    'category': 'Tools',
    'author': 'ABF OSIELL, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'maintainer': 'ABF OSIELL',
    'website': 'http://www.osiell.com',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_module_category.xml',
        'data/ir_cron.xml',
        'views/role.xml',
        'views/user.xml',
    ],
    'installable': True,
    'auto_install': False,
}
