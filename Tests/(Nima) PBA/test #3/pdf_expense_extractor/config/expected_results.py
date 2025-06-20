"""
Expected validation results for PDF files.
"""

EXPECTED_RESULTS = {
    "AV - MC - 02 - FEB-2025": {
        "total": 434980.00,
        "count": 5
    },
    "AV - MC - 03 - MAR-2025": {
        "total": 44900.00,
        "count": 2
    },
    "AV - MC - 04 - ABR-2025": {
        "total": 1068097.00,
        "count": 9
    },
    "AV - VS - 02 - FEB-2025": {
        "total": 1702961.00,
        "count": 18
    },
    "AV - VS - 03 - MAR-2025": {
        "total": 810460.00,
        "count": 14
    },
    "AV - VS - 04 - ABR-2025": {
        "total": 1058980.00,
        "count": 20
    }
}

# Expected transactions with zero amounts (payments, adjustments) that should be excluded
EXCLUDED_TRANSACTION_TYPES = [
    "PAGO ATH CANALES ELECTRONICOS",
    "SEGURO DE VIDA DEUDOR",
    "INTERESES FACTURADOS",
    "ABONO SUCURSAL VIRTUAL",
    "AJUSTE MANUAL A FAVOR",
    "APLICACION SALDO A FAVO"
]