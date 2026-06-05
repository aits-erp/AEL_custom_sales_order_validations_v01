frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {

        if (!frm.is_new()) {

            frm.add_custom_button('Duty Invoice', function() {
                create_invoice(frm, "Duty Invoice");
            }, 'Create');

            frm.add_custom_button('Freight Certificate', function() {
                create_invoice(frm, "Freight Certificate");
            }, 'Create');
        }
    }
});

function create_invoice(frm, type) {

    frappe.call({
        method: "sales_invoice.sales_invoice.make_sales_invoice",
        args: {
            sales_order: frm.doc.name,
            invoice_type: type
        },
        callback: function(r) {
            if (r.message) {
                frappe.set_route("Form", "Sales Invoice", r.message);
            }
        }
    });
}