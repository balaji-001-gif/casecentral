import frappe
from frappe import _

def get_context(context):
    case_name = frappe.form_dict.get("name")
    if not case_name:
        frappe.local.flags.redirect_to = "/cases"
        return

    case = frappe.get_doc("Case", case_name)
    
    # Permission Check: Ensure the case belongs to the logged-in customer
    user_email = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user_email}, "name")
    
    if not customer:
        # Fallback to contact check
        customer_id = frappe.db.sql("""
            SELECT dl.link_name 
            FROM `tabDynamic Link` dl
            JOIN `tabContact` c ON c.name = dl.parent
            WHERE dl.link_doctype = 'Customer' 
            AND c.email_id = %s
        """, (user_email,))
        if customer_id:
            customer = customer_id[0][0]

    if case.customer != customer:
        frappe.throw(_("You do not have permission to view this case"), frappe.PermissionError)

    context.doc = case
    
    # Get Hearing History (assuming Case History table)
    context.history = sorted(case.case_history, key=lambda x: x.hearing_date or "", reverse=True)
    
    # Get Matter Details
    context.matter_doc = frappe.get_doc("Matter", case.matter)
    
    # Get Attachments
    context.attachments = frappe.get_all("File", 
        filters={"attached_to_doctype": "Case", "attached_to_name": case_name},
        fields=["file_name", "file_url", "creation"],
        ignore_permissions=True
    )
