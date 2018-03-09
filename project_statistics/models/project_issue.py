#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.parser import parse
from pytz import timezone
    
    
class ProjectIssue(models.Model):
    _inherit = 'project.issue'
            
    def compute_next_datetime(self, xdate, hours):
        hour_start  = int(self.env['ir.config_parameter'].get_param('project_start_time_working_day')) or 9
        hour_end    = int(self.env['ir.config_parameter'].get_param('project_end_time_working_day')) or 19
        working_hours = hour_end - hour_start
        date_obj = datetime.strptime(xdate, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone('UTC'))
        dt_value = date_obj.astimezone(timezone(self.env.user.partner_id.tz or 'UTC'))
                
        days_factor = hours / working_hours # dias requeridos para calcular
        weeks_factor = days_factor / 5.0 # De lunes a viernes
        if dt_value.weekday() in (5,6): # Se reporto en Fin de semana (Sabado / Domingo)
            dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)
            dt_value = dt_value.replace(hour=hour_start,minute=0,second=0)
            
        if dt_value.hour >= hour_end: # La Incidencia se reporto fuera de horario de trabajo en dia laboral
            dt_value = dt_value + timedelta(days=int(days_factor + 1))
            if dt_value.weekday() >= 5: # Sabado o Domingo
                dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)
            dt_value = dt_value.replace(hour=hour_start,minute=0,second=0)
            
        if not bool(int(days_factor)):
            total_hours = dt_value.hour + hours
            if total_hours < hour_end:
                dt_value = dt_value.replace(hour=total_hours)
            else:
                diff_hours = total_hours - hour_end
                dt_value = dt_value + timedelta(days=1,hours=hour_start+(total_hours - hour_end))
        else:
            dt_value = dt_value + timedelta(days=int(days_factor) + (int(weeks_factor)*2))
            xhours = hours * (days_factor - int(days_factor))
            total_hours = dt_value.hour + xhours            
            if total_hours < hour_end:
                dt_value = dt_value.replace(hour=int(total_hours))
            else:
                diff_hours = total_hours - hour_end
                dt_value = dt_value + timedelta(days=1,hours=int(hour_start+(total_hours - hour_end))) 
        
        # Nos aseguramos que no quede en sabado o domingo
        if dt_value.weekday() in (5,6):
            dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)

        dt_value = dt_value.astimezone(timezone('UTC'))
        return dt_value.strftime('%Y-%m-%d %H:%M:%S')
        
    @api.one
    @api.depends('create_date', 'date_open', 'date_closed')
    def _get_data(self):
        hour_start  = int(self.env['ir.config_parameter'].get_param('project_start_time_working_day')) or 9
        hour_end    = int(self.env['ir.config_parameter'].get_param('project_end_time_working_day')) or 19
        working_hours = hour_end - hour_start
        priority = self.priority
        std_open = int(self.env['ir.config_parameter'].get_param('standard_between_creation_and_assigned_%s_stars' % priority)) or 0
        std_close = int(self.env['ir.config_parameter'].get_param('standard_between_assigned_and_close_%s_stars' % priority)) or 0
        
        self.date_open_std = self.compute_next_datetime(self.create_date, std_open)
        self.date_close_std = self.compute_next_datetime(self.date_open_std, std_close)
        create_date = datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S')
        date_open = self.date_open and datetime.strptime(self.date_open, '%Y-%m-%d %H:%M:%S') or False
        date_open_std = datetime.strptime(self.date_open_std, '%Y-%m-%d %H:%M:%S')
        date_close_std = datetime.strptime(self.date_close_std, '%Y-%m-%d %H:%M:%S')
        date_closed = self.date_closed and datetime.strptime(self.date_closed, '%Y-%m-%d %H:%M:%S') or False
        
        self.hours_delayed_open = 0
        if date_open and date_open_std:
            days = (date_open - date_open_std).days * working_hours
            self.hours_delayed_open = (days  + ((date_open - date_open_std).seconds / 60.0 / 60.0)) or 0.0
            if (days and days < 0) or self.hours_delayed_open < 0:
                self.hours_delayed_open = 0
                
        self.hours_delayed_close = 0
        if date_closed and date_close_std:
            days = (date_closed - date_close_std).days * working_hours
            self.hours_delayed_close = (days + ((date_closed - date_close_std).seconds / 60.0 / 60.0)) or 0.0
            if (days and days < 0) or self.hours_delayed_close < 0:
                self.hours_delayed_close = 0
        
        
    #date_deadline = fields.Date(string='Expected Deadline',compute="_get_data", store=True)
    date_open_std = fields.Datetime(string='Expected Assigned', compute="_get_data", store=True)
    date_close_std = fields.Datetime(string='Expected Close',compute="_get_data", store=True)
    hours_delayed_open = fields.Float(string="Delayed Hours Assign", compute="_get_data",
                                      help="Time between Creation and Assignment", store=True)
    hours_delayed_close = fields.Float(string="Delayed Hours Close", compute="_get_data",
                                      help="Time between Assignment and Close", store=True)
            
    
    