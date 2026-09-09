from odoo import fields, models


class QualityRightsRecord(models.Model):
    _name = 'quality.rights.record'
    _description = 'Synthetic company isolation record'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', required=True)
    value = fields.Integer()
