app_name = "sales_invoice"
app_title = "Sales Invoice"
app_publisher = "kp"
app_description = "add 2 fields"
app_email = "k@gmail.com"
app_license = "mit"

doctype_js = {
    "Sales Order": "public/js/sales_invoice.js"
}

doc_events = {
    "Sales Order": {
        "on_cancel": "sales_invoice.api.on_cancel_sales_order"
    }
}

fixtures = [
    {
        "dt" :"Custom Field",
        "filters":[
            ["module", "=", "sales_invoice"]
        ]
    }
]
