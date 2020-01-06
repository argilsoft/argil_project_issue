# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Statistics',
    'version': '1.0',
    'category': 'Project',
    'description': """
This module adds fields to track Statistics based on Stages.
============================================================

You can have some statistics based on parameters

                """,
    'website': 'https://www.argil.mx',
    'depends': [
        'project_issue',
        'project'
    ],
    'data': [
        'views/ir_config_parameter_data.xml',
        'views/project_issue_view.xml',
        'views/project_task_view.xml',
    ],
    'auto_install': False,
}
