import frappe
from frappe import _

def get_context(context):
    matter_name = frappe.form_dict.get("name")
    if not matter_name:
        frappe.local.flags.redirect_to = "/matters"
        return

    matter = frappe.get_doc("Matter", matter_name)
    
    # Permission Check
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

    if matter.customer != customer:
        frappe.throw(_("You do not have permission to view this matter"), frappe.PermissionError)

    context.doc = matter
    
    # Get Attachments
    context.attachments = frappe.get_all("File", 
        filters={"attached_to_doctype": "Matter", "attached_to_name": matter_name},
        fields=["file_name", "file_url", "creation"],
        ignore_permissions=True
    )
