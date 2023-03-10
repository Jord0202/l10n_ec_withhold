# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)



class AccountPaymentGroup(models.Model):
    _inherit = "account.payment.group"


    withhold_bool = fields.Boolean(string="Retencion", default=False)

    document_withhold =fields.Many2one(
        comodel_name="l10n_ec.withhold",
        string="Documento de retencion",
        required=False,
        store=True,
        ondelete="cascade",
    )



    @api.depends(
        'payments_amount','payment_ids.signed_amount_company_currency',
        'withhold_bool', 'document_withhold.withhold_totals', 'document_withhold')
    def _compute_payments_amount(self):
        for rec in self:
            if rec.withhold_bool :
                rec.payments_amount = sum(rec.payment_ids.mapped('signed_amount_company_currency')) + rec.document_withhold.withhold_totals
            else:
                rec.payments_amount = sum(rec.payment_ids.mapped('signed_amount_company_currency'))

    
    @api.depends(
        'payment_difference', 'payments_amount', 'withhold_bool', 'document_withhold.withhold_totals', 'document_withhold','to_pay_amount'  )
    def _compute_payment_difference(self):
        for rec in self:
            if rec.withhold_bool :
                rec.payment_difference = rec.to_pay_amount - rec.payments_amount - rec.document_withhold.withhold_totals
            else:
                rec.payment_difference = rec.to_pay_amount - rec.payments_amount




            

