console.log("JS WORKING");

frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frappe.call({
                method: "sales_invoice.api.get_created_invoice_types",
                args: { sales_order: frm.doc.name },
                callback: function(r) {
                    let created_types = r.message || [];

                    if (!created_types.includes("1")) {
                        frm.add_custom_button(__('Duty Invoice'), function() {
                            create_custom_invoice(frm, "1");
                        }, __('Create'));
                    }

                    if (!created_types.includes("2")) {
                        frm.add_custom_button(__('Freight Certificate'), function() {
                            create_custom_invoice(frm, "2");
                        }, __('Create'));
                    }
                }
            });
        }
    }
});

function create_custom_invoice(frm, invoice_type) {
    frappe.call({
        method: "sales_invoice.api.make_sales_invoice",
        args: {
            sales_order: frm.doc.name,
            invoice_type: invoice_type
        },
        freeze: true,
        freeze_message: __('Preparing Invoice...'),
        callback: function(r) {
            if (r.message) {
                // frappe.set_route("Form", "Sales Invoice", r.message);
                let docs = frappe.model.sync(r.message);
                frappe.set_route("Form", docs[0].doctype, docs[0].name);
            }
        }
    });
}
