import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_to = "/login"
        return

    user_email = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user_email}, "name")
    
    if not customer:
        customer_id = frappe.db.sql("""
            SELECT dl.link_name FROM `tabDynamic Link` dl
            JOIN `tabContact` c ON c.name = dl.parent
            WHERE dl.link_doctype = 'Customer' AND c.email_id = %s
        """, (user_email,))
        if customer_id:
            customer = customer_id[0][0]

    if not customer:
        context.no_customer = True
        return

    # DocType selection for upload
    target_doctype = frappe.form_dict.get("doctype", "Case")
    context.target_doctype = target_doctype
    
    # Pre-selected record if any
    context.pre_selected_doc = frappe.form_dict.get("case") or frappe.form_dict.get("name")

    # Fetch available records for the selected DocType
    if target_doctype == "Case":
        context.docs = frappe.get_all("Case", 
            filters={"customer": customer, "status": ["not in", ["Disposed", "NOC"]]},
            fields=["name", "case_title as title"], ignore_permissions=True
        )
    elif target_doctype == "Matter":
        context.docs = frappe.get_all("Matter",
            filters={"customer": customer, "status": ["not in", ["Completed", "Cancelled"]]},
            fields=["name", "name as title"], ignore_permissions=True
        )
    elif target_doctype == "Customer Appointment":
        context.docs = frappe.get_all("Customer Appointment",
            filters={"customer": customer, "status": ["not in", ["Completed", "Cancelled"]]},
            fields=["name", "name as title"], ignore_permissions=True
        )
