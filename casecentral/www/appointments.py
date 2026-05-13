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

    context.appointments = frappe.get_all("Customer Appointment", 
        filters={"customer": customer},
        fields=["name", "status", "appointment_date", "appointment_time", "service"],
        order_by="appointment_date desc",
        ignore_permissions=True
    )
    context.customer_name = frappe.db.get_value("Customer", customer, "customer_name")
