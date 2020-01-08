#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import date, timedelta
from dateutil.parser import parse
from pytz import timezone

    
class ProjectTask(models.Model):
    _inherit = 'project.task'
            
    def compute_next_datetime(self, xdate, days):
        """
        hour_start  = int(self.env['ir.config_parameter'].get_param('project_start_time_working_day')) or 9
        hour_end    = int(self.env['ir.config_parameter'].get_param('project_end_time_working_day')) or 19
        working_hours = hour_end - hour_start
        """
        dt_value = xdate - timedelta(days=days)

        if dt_value.weekday() in (5,6): # Se reporto en Fin de semana (Sabado / Domingo)
            dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and -1 or -2)            

        return dt_value #.strftime("%Y-%m-%d")
        
    @api.multi
    @api.depends('date_deadline', 'date_qa', 'date_customer_testing')
    def _get_data(self):
        std_qa = int(self.env['ir.config_parameter'].get_param('days_for_qa_before_deadline_4_tasks')) or 2
        std_close = int(self.env['ir.config_parameter'].get_param('days_for_customer_testing_before_deadline_4_tasks')) or 0
        
        for rec in self:
            rec.days_delayed_4_qa = 0
            rec.days_delayed_4_customer_testing = 0
            if not rec.date_deadline:
                continue
            rec.date_qa_std = rec.compute_next_datetime(rec.date_deadline, std_qa)
            rec.date_customer_testing_std = rec.compute_next_datetime(rec.date_deadline, std_close)

            date_qa = rec.date_qa.date()
            date_qa_std = rec.date_qa_std
            date_customer_testing = rec.date_customer_testing
            date_customer_testing_std = rec.date_customer_testing_std

        
            if date_qa and date_qa_std:
                rec.days_delayed_4_qa = (date_qa - date_qa_std).days
                if (rec.days_delayed_4_qa and rec.days_delayed_4_qa < 0) or rec.days_delayed_4_qa < 0:
                    rec.days_delayed_4_qa = 0

            if date_customer_testing and date_customer_testing_std:
                rec.days_delayed_4_customer_testing = (date_customer_testing - date_customer_testing_std).days
                if (rec.days_delayed_4_customer_testing and rec.days_delayed_4_customer_testing < 0) or rec.days_delayed_4_customer_testing < 0:
                    rec.days_delayed_4_customer_testing = 0
                
        

    date_qa_std = fields.Date(string='Expected Date QA', compute="_get_data", store=True)
    date_customer_testing_std = fields.Date(string='Expected Date Cust. Test',compute="_get_data", store=True)
    days_delayed_4_qa = fields.Float(string="Days Delayed in QA", compute="_get_data",
                                      help="Days bw QA Date & Expected QA Date", store=True)
    days_delayed_4_customer_testing = fields.Float(string="Days Delayed in Customer Testing", compute="_get_data",
                                      help="Days bw Customer Testing & Expected Customer Testing", store=True)
            
    
    