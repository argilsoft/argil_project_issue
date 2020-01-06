# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProjectStage(models.Model):
    _inherit = ['project.task.type']

    
    def _get_mail_template_id_domain(self):
        domain = super(ProjectStage, self)._get_mail_template_id_domain()
        return ['|'] + domain + [('model', '=', 'project.issue')]
    
    
    mark_as_internal_testing = fields.Boolean(string='Internal QA',
        help='This stage is used for calculating Issues Statistics.')
    
    mark_as_customer_testing = fields.Boolean(string='Customer Testing',
        help='This stage is used for calculating Issues Statistics.')
    
    mark_as_ended = fields.Boolean(string='Set as Done',
        help='This stage is used for calculating Project Tasks & Issues Statistics.')
