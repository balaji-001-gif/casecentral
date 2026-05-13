import frappe
from frappe import _

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.throw(_("Please login to access this page"), frappe.PermissionError)

    # Get Customer linked to the User
    customer = frappe.db.get_value("Contact", {"email_id": frappe.session.user}, "links")
    # Alternatively, use Customer directly if User is linked
    customer = frappe.db.get_value("Customer", {"email_id": frappe.session.user}, "name")
    
    if not customer:
        # Check if the user is a customer contact
        customer = frappe.db.sql("""
            SELECT parent FROM `tabDynamic Link` 
            WHERE link_doctype='Customer' AND parenttype='Contact' 
            AND EXISTS (SELECT name FROM `tabContact` WHERE name=`tabDynamic Link`.parent AND email_id=%s)
        """, (frappe.session.user,))
        if customer:
            customer = customer[0][0]

    if not customer:
        context.no_customer = True
        return

    context.cases = frappe.get_all("Case", 
        filters={"customer": customer},
        fields=["name", "case_title", "status", "next_hearing_date", "case_no", "case_year", "court_number_and_judge"],
        order_by="creation desc"
    )
    
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
