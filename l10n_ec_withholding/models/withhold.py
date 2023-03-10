import logging
from contextlib import contextmanager


from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

STATES = {"draft": [("readonly", False)]}
_logger = logging.getLogger(__name__)


class L10nEcWithhold(models.Model):

    _name = "l10n_ec.withhold"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Ecuadorian Withhold"
    _rec_name = "document_number"
    _mail_post_access = "read"
    _order = "issue_date DESC, document_number DESC"

    issue_date = fields.Date(string="Fecha de retencion", readonly=True, states=STATES, required=True, tracking=True)

    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        readonly=True,
        default="draft",
        tracking=True,
    )
    type_document = fields.Integer(default="11")



    partner_id = fields.Many2one(
        "res.partner",
        string="Cliente",
        readonly=True,
        states=STATES,
        index=True,
        auto_join=True,
        tracking=True,
    )

    document_number = fields.Char(
        string="Numero de Retencion",
        required=True,
        readonly=True,
        states=STATES,
        tracking=True,
        size=17,
    )

    concept = fields.Char(string="Concept", readonly=True, states=STATES, required=False, tracking=True)

    electronic_authorization = fields.Char(
        string="Electronic authorization",
        size=49,
        required=False,
        tracking=True,
        readonly=True,
        states=STATES,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        related="company_id.currency_id",
        store=True,
    )

    no_number = fields.Boolean("Withholding  without Number?")

    document_type = fields.Selection(
        string="Tipo de documento",
        selection=[
            ("electronic", "Electronic"),
            ("pre_printed", "Pre Printed"),
        ],
        required=True,
        readonly=True,
        states=STATES,
        default="electronic",
        tracking=True,
    )

    type = fields.Selection(
        string="Type",
        selection=[("sale", "On Sales"), ("purchase", "On Purchases"), ("credit_card", "On Credit Card Liquidation")],
        readonly=True,
        states=STATES,
        default="sale",
    )

    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Related Document",
        readonly=True,
        states=STATES,
        required=False,
        tracking=True,
    )

    l10n_ec_supplier_authorization_number = fields.Char(
        string="Supplier Authorization",
        required=False,
        size=10,
        readonly=True,
        states=STATES,
    )

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        readonly=True,
        states=STATES,
        ondelete="restrict",
        default=lambda self: self.env.company,
    )
    
    withhold_totals = fields.Float(
        string= "Total retenido",
        store= True,
        compute= "_compute_total_withhold"
    )



    l10n_ec_withhold_id = fields.Many2one(comodel_name="l10n_ec.withhold", string="Withhold", required=False)

    line_ids = fields.One2many(
        comodel_name="l10n_ec.withhold.line",
        inverse_name="withhold_id",
        string="Lines",
        readonly=True,
        states=STATES,
        required=True,
    )



    @api.depends('withhold_totals', "line_ids.withhold_amount")           
    def _compute_total_withhold(self):
        for amount_base in self:
            amount_base.withhold_totals = sum(line_ids.withhold_amount for line_ids in amount_base.line_ids )

    def button_validate(self):
        """
        Botón de validación de Retención que se usa cuando
        se creó una retención manual, esta se relacionará
        con la factura seleccionada.
        """
        for ret in self:
            if not ret.line_ids:
                raise UserError('No ha aplicado impuestos.')
            #self.action_validate(self.document_number)
            if ret.type == 'sale':
                    self.create_move()
                    
        return True   
    
    def action_cancel(self):
        """
        Método para cambiar de estado a cancelado el documento
        """
        self.write({'state': 'cancelled'})
        return True 

    def action_draft(self):
        self.write({'state': 'draft'})
        return True
    
    @api.depends('withhold_totals', "line_ids.withhold_amount", 'line_ids', 'document_number' , 'partner_id')      
    def create_move(self):
        """
        Generacion de asiento contable para aplicar como
        pago a factura relacionada
        """
        for ret in self:
            inv = ret.invoice_id
            move_data = {
                'journal_id': ret.type_document,
                'ref': "RET" + ret.document_number,
                'date': ret.issue_date
            }
            total_counter = 0
            lines = []
            for line in ret.line_ids:
                if self.type == 'in_invoice':
                    lines.append((0, 0, {
                    'partner_id': ret.partner_id.id,
                    'account_id': line.tax_withhold_ids.tax_group_id.property_advance_tax_payment_account_id.account_id.id,
                    'name': ret.name,
                    'debit': 0.00,
                    'credit': abs(line.withhold_amount)
                    }))
                else:
                    lines.append((0, 0, {
                    'partner_id': ret.partner_id.id,
                    'account_id': line.tax_withhold_ids.tax_group_id.property_advance_tax_payment_account_id.id,
                    'name': "RET " + ret.document_number,
                    'debit': abs(line.withhold_amount),
                    'credit': 0.00
                    }))

                total_counter += abs(line.withhold_amount)

            if self.type == 'in_invoice':
                    lines.append((0, 0, {
                'partner_id': ret.partner_id.id,
                'account_id': inv.account_id.id,
                'name': ret.name,
                'debit': total_counter,
                'credit': 0.00
                }))
            else:
                lines.append((0, 0, {
                'partner_id': ret.partner_id.id,
                'account_id': inv.partner_id.property_account_receivable_id.id,
                'name': "RET " + ret.document_number,
                'debit': 0.00,
                'credit': total_counter
                }))
            move_data.update({'line_ids': lines})
            move = self.env['account.move'].create(move_data)
            acctype = self.type == 'in_invoice' and 'payable' or 'receivable'
            inv_lines = inv.line_ids
            acc2rec = inv_lines.filtered(lambda l: l.account_id.internal_type == acctype)  # noqa
            acc2rec += move.line_ids.filtered(lambda l: l.account_id.internal_type == acctype)  # noqa
            #ret.write({'move_ret_id': move.id})
            move.post()
            acc2rec.reconcile()
            ret.state = "done"
        return True    
