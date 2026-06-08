import frappe
from frappe import _


@frappe.whitelist()
def get_invoice_count(sales_order):
    """Returns count of active Sales Invoices linked to this Sales Order"""
    count = frappe.db.count("Sales Invoice", {
        "custom_sales_order_ref": sales_order,
        "docstatus": ["!=", 2]  # not cancelled
    })
    return count

@frappe.whitelist()
def make_sales_invoice(sales_order, invoice_type):
    """Creates a Sales Invoice of given type linked to the Sales Order"""

    # Double-check limit on backend (security)
    count = frappe.db.count("Sales Invoice", {
        "custom_sales_order_ref": sales_order,
        "docstatus": ["!=", 2]
    })

    if count >= 2:
        frappe.throw(_("Only 2 Sales Invoices (Duty Invoice / Freight Certificate) are allowed per Sales Order."))

    so = frappe.get_doc("Sales Order", sales_order)

    si = frappe.new_doc("Sales Invoice")
    si.customer = so.customer
    si.custom_sales_order_ref = so.name        # ✅ Hidden custom field (reliable link)
    si.custom_invoice_type = invoice_type      # ✅ Hidden custom field (Duty Invoice / Freight Certificate)

    for item in so.items:
        si.append("items", {
            "item_code": item.item_code,
            "qty": item.qty,
            "rate": item.rate,
            "sales_order": so.name,
            "so_detail": item.name
        })

    si.insert(ignore_permissions=True)
    return si.name


def on_cancel_sales_order(doc, method):
    """When Sales Order is cancelled, cancel all linked Sales Invoices"""

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "custom_sales_order_ref": doc.name,
            "docstatus": 1  # only submitted invoices
        },
        fields=["name"]
    )

    for inv in invoices:
        try:
            si = frappe.get_doc("Sales Invoice", inv["name"])
            si.cancel()
            frappe.msgprint(
                _("Sales Invoice {0} has been cancelled.").format(inv["name"]),
                alert=True
            )
        except Exception as e:
            frappe.log_error(
                message=str(e),
                title=f"Failed to cancel Sales Invoice {inv['name']}"
            )