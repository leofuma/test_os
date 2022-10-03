# -*- coding: utf-8 -*-

{
    "name": "UTEC Seguridad",
    "version": "1.0",
    "description": """
        UTEC Seguridad
    """,
    "author": "OpenSur",
    "category": "Tools",
    "depends": [
        'base_user_role', 'hr'
    ],
    "data": [
        'security/utec_seguridad_security.xml',
        'security/ir.model.access.csv',
        'views/res_groups_view.xml',
        'views/res_users_view.xml',
        'views/security_profile_view.xml',
        'views/security_analysis_view.xml',
        'data/load_data.xml',
    ],
    'application': True,
}
