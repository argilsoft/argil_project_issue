#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from pytz import timezone

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    def get_number_days_inbetween(self, date1, date2):
        if not (date1 and date2):
            return 0        
        d1 = date1.replace(tzinfo=timezone('UTC'))
        d2 = date2.replace(tzinfo=timezone('UTC'))
        return (d2-d1).days
    
    
    @api.multi
    @api.depends('create_date', 'date_assign', 'date_qa', 'date_customer_testing', 'date_closed')
    def _compute_duration(self):
        for task in self:
            task.duration_create_open   = task.get_number_days_inbetween(task.create_date, task.date_assign)
            task.duration_open_qa       = task.get_number_days_inbetween(task.date_assign, task.date_qa)
            task.duration_qa_customer_testing = task.get_number_days_inbetween(task.date_qa, task.date_customer_testing)
            task.duration_customer_testing_close = task.get_number_days_inbetween(task.date_customer_testing, task.date_closed)
            task.duration_create_close = task.get_number_days_inbetween(task.create_date, task.date_closed)
    
    
    
    duration_create_open = fields.Integer(string="Days bw Creation & Assigned", 
                                          help="Days between Creation and Assigned", 
                                          compute="_compute_duration", store=True)
    duration_open_qa = fields.Integer(string="Days bw Assigned & QA", 
                                      help="Days between Assigned and Quality Assurance", 
                                          compute="_compute_duration", store=True)
    duration_qa_customer_testing = fields.Integer(string="Days bw QA & Customer Test", 
                                                    help="Days between Quality Assurance and Customer Testing", 
                                                    compute="_compute_duration", store=True)
    duration_customer_testing_close = fields.Integer(string="Days bw Customer Test & Close", 
                                                      help="Days between Customer Testing and Close", 
                                                      compute="_compute_duration", store=True)
    duration_create_close = fields.Integer(string="Days bw Creation & Close", 
                                             help="Days between Creation and Close", 
                                             compute="_compute_duration", store=True)
    
    
    
    date_qa = fields.Datetime(string='Date QA', readonly=True, index=True)
    date_customer_testing = fields.Datetime(string='Date Customer Testing', readonly=True, index=True)
    date_closed = fields.Datetime(string='Date Closed', readonly=True, index=True)
    
    
    
    # -------------------------------------------------------
    # Stage management
    # -------------------------------------------------------
    def update_dates(self, stage_id):
        project_task_type = self.env['project.task.type'].browse(stage_id)
        #if project_task_type.fold and project_task_type.mark_as_ended:
        values = {'date_closed': self.date_closed}
        if project_task_type.mark_as_internal_testing:
            values.update({'date_qa': fields.Datetime.now()})
        if project_task_type.mark_as_customer_testing:
            values.update({'date_customer_testing': fields.Datetime.now()})
            if not self.date_qa:
                values.update({'date_qa': fields.Datetime.now()})
        if project_task_type.mark_as_ended:
            values.update({'date_closed': fields.Datetime.now()})
            if not self.date_qa:
                values.update({'date_qa': fields.Datetime.now()})
            if not self.date_customer_testing:
                values.update({'date_customer_testing': fields.Datetime.now()})
        return values

    
    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals.update(self.update_dates(vals['stage_id']))
        result = super(ProjectTask, self).write(vals)
        return result