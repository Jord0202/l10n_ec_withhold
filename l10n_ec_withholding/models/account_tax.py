from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval
from odoo.tools.safe_eval import safe_eval as eval
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
import logging
_logger = logging.getLogger(__name__)

TYPE_TAX_USE = [
    ('sale', 'Ventas'),
    ('purchase', 'Compras'),
    ('VAT Withhold', 'Retención de IVA'),
    ('Profit Withhold', 'Retención a la fuente'),
    ('none', 'Ninguno'),
]


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    type_tax_use = fields.Selection(TYPE_TAX_USE, string='Tipo de Impuesto', required=True, default="sale",
        help="Determina dónde se puede seleccionar el impuesto. Nota: 'Ninguno' significa que un impuesto no se puede usar solo, sin embargo, aún se puede usar en un grupo. 'Ajuste' se utiliza para realizar el ajuste de impuestos.")

class AccountTax(models.Model):
    _inherit = "account.tax"

    type_tax_use = fields.Selection(TYPE_TAX_USE, string='Tax Type', required=True, default="sale",
        help="Determina dónde se puede seleccionar el impuesto. Nota: 'Ninguno' significa que un impuesto no se puede usar solo, sin embargo, aún se puede usar en un grupo. 'Ajuste' se utiliza para realizar el ajuste de impuestos.")