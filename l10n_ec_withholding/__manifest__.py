{
    "name": "Retencion en venta Ecuador",
    "summary": "",
    "category": "Account",
    "author": "Jordan Centeno",
    "website": "https://github.com/Jord0202/l10n_ec.withhold",
    "version": "15.0.1.0.0",
    "depends": ["account", "account_edi", "l10n_ec", "l10n_ec_base","account_payment_group","account_payment_fix","account_financial_amount"],
    "external_dependencies": {
        "python": ["cryptography==36.0.0", "xmlsig==0.1.9", "xades==0.2.4", "zeep"]
    },
    "data": [
       #"security/ir.model.access.csv",
       "views/account_move_view.xml",
       "views/withhold_view.xml",
       "views/account_withhold.xml",
       "views/account_tax_view.xml",
       "views/account_payment_withhold.xml",

    ],
    "assets": {

    },
    "installable": True,
    "auto_install": False,
}
