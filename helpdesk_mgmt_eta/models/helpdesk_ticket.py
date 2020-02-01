from odoo import _, api, fields, models, tools


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    date_expected = fields.Date(string="Fecha Estimada")