import frappe
from frappe import _
from frappe.utils import today

DUTY_INVOICE = "1"
FREIGHT_CERTIFICATE = "2"


@frappe.whitelist()
def get_invoice_count(sales_order):
    count = frappe.db.count("Sales Invoice", {
        "custom_sales_order_ref": sales_order,
        "docstatus": ["!=", 2]
    })
    return count


@frappe.whitelist()
def make_sales_invoice(sales_order, invoice_type):
    existing = frappe.db.count("Sales Invoice", {
        "custom_sales_order_ref": sales_order,
        "custom_invoice_type": invoice_type,
        "docstatus": ["!=", 2]
    })

    if existing >= 1:
        type_label = "Duty Invoice" if invoice_type == DUTY_INVOICE else "Freight Certificate"
        frappe.throw(_(f"A {type_label} already exists for this Sales Order."))

    so = frappe.get_doc("Sales Order", sales_order)
    company = so.company

    si = frappe.new_doc("Sales Invoice")
    si.customer = so.customer
    si.company = company
    si.posting_date = today()
    si.due_date = today()
    si.currency = so.currency
    si.selling_price_list = so.selling_price_list
    si.custom_sales_order_ref = sales_order
    si.custom_invoice_type = invoice_type

    label = "Duty Invoice" if invoice_type == DUTY_INVOICE else "Freight Certificate"
    si.remarks = f"{label} | SO: {sales_order}"
    # si.title = label
    si.title = so.customer

    si.debit_to = frappe.db.get_value("Company", company, "default_receivable_account")

    for item in so.items:
        income_account = frappe.db.get_value("Company", company, "default_income_account")
        cost_center = frappe.db.get_value("Company", company, "cost_center")
        uom = item.uom or frappe.db.get_value("Item", item.item_code, "stock_uom")
        item_name = item.item_name or frappe.db.get_value("Item", item.item_code, "item_name")

        si.append("items", {
            "item_code": item.item_code,
            "item_name": item_name,
            "qty": item.qty,
            "rate": item.rate,
            "uom": uom,
            "income_account": income_account,
            "cost_center": cost_center,
            "sales_order": sales_order,
            "so_detail": item.name
        })

    # si.insert(ignore_permissions=True)
    # return si.name
    return si.as_dict()


@frappe.whitelist()
def get_created_invoice_types(sales_order):
    # Hide if Draft OR Submitted (not cancelled)
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_sales_order_ref": sales_order,
            "docstatus": ["!=", 2]
        },
        fields=["custom_invoice_type"]
    )
    types = []
    for inv in invoices:
        if inv.custom_invoice_type:
            types.append(inv.custom_invoice_type)
    return types


def on_cancel_sales_order(doc, method):
    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_sales_order_ref": doc.name,
            "docstatus": 1
        },
        fields=["name"]
    )
    for inv in invoices:
        try:
            si = frappe.get_doc("Sales Invoice", inv["name"])
            si.cancel()
            frappe.msgprint(
                _("Sales Invoice {0} cancelled.").format(inv["name"]),
                alert=True
            )
        except Exception as e:
            frappe.log_error(
                message=str(e),
                title=f"Failed to cancel Sales Invoice {inv['name']}"
            )
