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

    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
    
    # Counts for Dashboard
    context.matter_count = frappe.db.count("Matter", {"customer": customer, "status": ["not in", ["Completed", "Cancelled"]]})
    context.case_count = frappe.db.count("Case", {"customer": customer, "status": ["not in", ["Disposed", "NOC"]]})
    context.appointment_count = frappe.db.count("Customer Appointment", {"customer": customer, "status": ["not in", ["Completed", "Cancelled"]]})

    # Recent Records
    context.recent_cases = frappe.get_all("Case", 
        filters={"customer": customer}, 
        fields=["name", "case_title", "status", "next_hearing_date"], 
        limit=3, order_by="modified desc", ignore_permissions=True
    )
    
    context.recent_appointments = frappe.get_all("Customer Appointment",
        filters={"customer": customer},
        fields=["name", "appointment_date", "status"],
        limit=3, order_by="modified desc", ignore_permissions=True
    )
