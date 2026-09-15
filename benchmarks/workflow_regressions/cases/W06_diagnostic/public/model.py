from odoo import models
class Demo(models.Model):
    _name = "lab.demo"
    _positive = models.Constraint("CHECK(amount >= 0)", "Positive amount")
