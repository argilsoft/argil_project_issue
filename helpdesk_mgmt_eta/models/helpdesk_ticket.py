from odoo import _, api, fields, models, tools


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    date_expected = fields.Date(string="Fecha Estimada")
    commercial_partner_id = fields.Many2one('res.partner', related='partner_id.commercial_partner_id',
                                           readonly=True, store=True)