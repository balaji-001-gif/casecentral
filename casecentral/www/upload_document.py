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
            SELECT parent FROM `tabDynamic Link` 
            WHERE link_doctype='Customer' AND parenttype='Contact' 
            AND EXISTS (SELECT name FROM `tabContact` WHERE name=`tabDynamic Link`.parent AND email_id=%s)
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
        filters={"customer": customer, "status": ["in", ["Pending", "InProgress"]]},
        fields=["name", "case_title"]
    )
