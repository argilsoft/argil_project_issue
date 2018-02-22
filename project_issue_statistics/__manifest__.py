# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Statistics',
    'version': '1.0',
    'category': 'Project',
    'description': """
This module adds fields to track Statistics based on Issue Stages.
==================================================================

Worklogs can be maintained to signify number of hours spent by users to handle an issue.
                """,
    'website': 'https://www.argil.mx',
    'depends': [
        'project_issue',
        'project'
    ],
    'data': [
        'views/project_issue_view.xml',
        'views/ir_config_parameter_data.xml',
    ],
    'auto_install': True,
}
