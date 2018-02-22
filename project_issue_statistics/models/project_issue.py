#-*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.parser import parse
import pandas as pd
import pytz    
    
    
class ProjectIssue(models.Model):
    _inherit = 'project.issue'

    def convert_date_from_tz_to_tz(self, datetime_obj, tz_source, tz_dest): 
        """ Params:
                datetime_obj: Date in datetime class
                tz_source   : Timezone (string) 
                tx_dest     : Timezone (string) 
            Returns:
                datetime class object
        """
        
        print('datetime_obj: %s' % datetime_obj)
        src_tz = pytz.timezone(tz_source)
        print("src_tz.zone: %s" % src_tz.zone)
        dst_tz = pytz.timezone(tz_dest)
        print("dst_tz.zone: %s" % dst_tz.zone)        
        src_dt = src_tz.localize(datetime_obj, is_dst=False)
        return src_dt.astimezone(dst_tz)
        
    
    def compute_next_datetime(self, xdate, hours):
        hour_start  = int(self.env['ir.config_parameter'].get_param('argil_project_start_time_working_day')) or 9
        hour_end    = int(self.env['ir.config_parameter'].get_param('argil_project_end_time_working_day')) or 19
        working_hours = hour_end - hour_start
        print("-----------------------------")
        print("xdate: %s" % xdate)
        date_obj = datetime.strptime(xdate, '%Y-%m-%d %H:%M:%S')
        dt_value = date_obj #self.convert_date_from_tz_to_tz(date_obj, 'UTC', self.env.user.partner_id.tz)
                
        days_factor = hours / working_hours # dias requeridos para calcular
        weeks_factor = days_factor / 5.0 # De lunes a viernes
        print("days_factor: %s" % days_factor)
        print("weeks_factor: %s" % weeks_factor)
        print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
        print("dt_value.weekday(): %s" % dt_value.weekday())
        if dt_value.weekday() in (5,6): # Se reporto en Fin de semana (Sabado / Domingo)
            print("111111111111111")
            dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)
            dt_value = dt_value.replace(hour=hour_start,minute=0,second=0)
            print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
            
        if dt_value.hour >= hour_end: # La Incidencia se rerporto fuera de horario de trabajo en dia laboral
            print("22222222222222")
            dt_value = dt_value + timedelta(days=int(days_factor + 1))
            if dt_value.weekday() >= 5: # Sabado o Domingo
                dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)
            dt_value = dt_value.replace(hour=hour_start,minute=0,second=0)
            print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
            
        if not bool(int(days_factor)):
            print("Valor menor al rango del dia")
            total_hours = dt_value.hour + hours
            print("dt_value.hour + hours: %s" % (dt_value.hour + hours))
            if total_hours < hour_end:
                print("............ 111 .............")
                print("Entrando aqui.....")
                dt_value = dt_value.replace(hour=total_hours)
                print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
                print(".........................")
            else:
                print("............ 222 .............")
                diff_hours = total_hours - hour_end
                print("diff_hours: %s" % diff_hours )
                dt_value = dt_value + timedelta(days=1,hour=hour_start+(total_hours - hour_end))
                print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
                print(".........................")
        else:
            print("Valor MAYOR al rando del dia")
            dt_value = dt_value + timedelta(days=int(days_factor) + (int(weeks_factor)*2))
            print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
            print("hours: %s" % hours)
            print("days_factor: %s" % days_factor)
            print("int(days_factor): %s" % int(days_factor))
            xhours = hours * (days_factor - int(days_factor))
            print("xhours: ", xhours)
            total_hours = dt_value.hour + xhours            
            print("dt_value.hour + xhours: %s" % (dt_value.hour + xhours))
            if total_hours < hour_end:
                dt_value = dt_value.replace(hour=int(total_hours))
            else:
                diff_hours = total_hours - hour_end
                print("diff_hours: %s" % diff_hours )
                dt_value = dt_value + timedelta(days=1,hour=int(hour_start+(total_hours - hour_end))) 
            print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
        
        # Nos aseguramos que no quede en sabado o domingo
        if dt_value.weekday() in (5,6):
            dt_value = dt_value + timedelta(days=dt_value.weekday() == 5 and 2 or 1)
            
        print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
        #dt_value = self.convert_date_from_tz_to_tz(dt_value, self.env.user.partner_id.tz or 'UTC','UTC')
        #print("dt_value: %s" % dt_value.strftime('%Y-%m-%d %H:%M:%S'))
        return dt_value.strftime('%Y-%m-%d %H:%M:%S')
        
    @api.one
    @api.depends('create_date', 'date_open', 'date_closed','stage_id')
    def _get_data(self):
        priority = self.priority
        std_open = int(self.env['ir.config_parameter'].get_param('argil_standard_between_creation_and_assigned_%s_stars' % priority)) or 0
        std_close = int(self.env['ir.config_parameter'].get_param('argil_standard_between_assigned_and_close_%s_stars' % priority)) or 0
        
        print("priority: %s" % priority)
        print("std_open: %s" % std_open)
        print("std_close: %s" % std_close)
        
        self.date_open_std = self.compute_next_datetime(self.create_date, std_open)
        self.date_close_std = self.compute_next_datetime(self.date_open_std, std_close)
        create_date = datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S')
        date_open = datetime.strptime(self.date_open, '%Y-%m-%d %H:%M:%S')
        date_open_std = datetime.strptime(self.date_open_std, '%Y-%m-%d %H:%M:%S')
        date_close_std = datetime.strptime(self.date_close_std, '%Y-%m-%d %H:%M:%S')
        date_closed = self.date_closed and datetime.strptime(self.date_closed, '%Y-%m-%d %H:%M:%S') or False
        print("--------------------------------")
        print("--------------------------------")
        print("--------------------------------")
        print("--------------------------------")
        print("create_date: %s" % create_date)
        print("date_open: %s" % date_open)
        print("date_open_std: %s" % date_open_std)
        print("date_close_std: %s" % date_close_std)
        print("date_closed: %s" % date_closed)
        print("(date_open_std - create_date): %s" % (date_open_std - create_date))
        print("(date_open_std - create_date).seconds: %s" % (date_open_std - create_date).seconds)
        self.hours_delayed_open = ((date_open - date_open_std).seconds / 60.0 / 60.0) or 0.0
        if self.hours_delayed_open < 0:
            self.hours_delayed_open = 0
        self.hours_delayed_close = date_closed and ((date_closed - date_close_std).seconds / 60.0 / 60.0) or 0.0
        if self.hours_delayed_close < 0:
            self.hours_delayed_close = 0
        
        
        
    #date_deadline = fields.Date(string='Expected Deadline',compute="_get_data", store=True)
    date_open_std = fields.Datetime(string='Expected Assigned', compute="_get_data")
    date_close_std = fields.Datetime(string='Expected Close',compute="_get_data")
    hours_delayed_open = fields.Float(string="Delayed Hours Assign", compute="_get_data",
                                      help="Time between Creation and Assignment")
    hours_delayed_close = fields.Float(string="Delayed Hours Close", compute="_get_data",
                                      help="Time between Assignment and Close")    
            
    
    