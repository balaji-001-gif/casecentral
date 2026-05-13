import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access this page"), frappe.PermissionError)

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

    if not customer:
        context.no_customer = True
        return

    # Pre-select case if passed in URL
    context.selected_case = frappe.form_dict.get("case")
    
    # Get all active cases for selection
    context.cases = frappe.get_all("Case", 
        filters={"customer": customer, "status": ["not in", ["Disposed", "NOC"]]},
        fields=["name", "case_title"],
        ignore_permissions=True
    )
