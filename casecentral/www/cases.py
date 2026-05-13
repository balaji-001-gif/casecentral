import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access this page"), frappe.PermissionError)

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

    if not customer:
        context.no_customer = True
        return

    context.cases = frappe.get_all("Case", 
        filters={"customer": customer},
        fields=["name", "case_title", "status", "next_hearing_date", "case_no", "case_year", "court_number_and_judge"],
        order_by="creation desc"
    )
    
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
