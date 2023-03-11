import logging
import re
from xml.etree.ElementTree import SubElement

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import safe_eval

_logger = logging.getLogger(__name__)

_STATES = [
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],



#linea de impuestos tablita:3
class L10nEcWithholdLine(models.Model):

    _name = "l10n_ec.withhold.line"
    _description = "Ecuadorian Withhold"

    tax_withhold_ids = fields.Many2one(
        comodel_name = 'account.tax', 
        string= 'Impuesto de retencion'
    )

    base_amount =fields.Float( 
        string= "Monto base",
        store= True,
        compute= "_compute_valor_base")
    
    withhold_amount = fields.Float( 
        string= "Monto retenido",
        store= True,
        compute= "_compute_valor_withhold")

    document_related = fields.Char( default='withhold_id.invoice_id')

    withhold_id = fields.Many2one(
        comodel_name="l10n_ec.withhold",
        string="Withhold",
        required=True,
        store=True,
        ondelete="cascade",
        readonly=True,
    )


    @api.depends('withhold_id', 'tax_withhold_ids', 'base_amount')
    def _compute_valor_base(self):
        for base in self:
            if base.tax_withhold_ids.type_tax_use == "Profit Withhold":
                base.base_amount = base.withhold_id.invoice_id.amount_untaxed
                base.base_amount = round(base.base_amount,2)
            elif base.tax_withhold_ids.type_tax_use == "VAT Withhold":
                base.base_amount = base.withhold_id.invoice_id.amount_untaxed * 0.12
                base.base_amount = round(base.base_amount,2)
            else:
                0.00

    @api.depends('base_amount', 'withhold_amount')           
    def _compute_valor_withhold(self):
        for amount_base in self:
            amount_base.withhold_amount = amount_base.base_amount * amount_base.tax_withhold_ids.amount/100
            amount_base.withhold_amount = round(amount_base.withhold_amount,2)








    

