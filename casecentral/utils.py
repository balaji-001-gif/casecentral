import frappe

@frappe.whitelist()
def get_legal_services_to_invoice(matter, company):
    items_to_invoice = []
    if matter:
        # Build a list of billable legal services
        items_to_invoice += get_uninvoced_legal_services(matter, company)
        
        return items_to_invoice

def get_uninvoced_legal_services(matter, company):
    matter = frappe.get_doc('Matter', matter)
    services_to_invoice = []
    lse_list = frappe.db.sql("""
        SELECT name, legal_service, qty
        FROM `tabLegal Service Entry`
        WHERE matter=%s and invoiced = 0
    """,(matter.name), as_dict=True)

    rate = 0.0
    for lse in lse_list:
        for lsr in matter.legal_service_rates:
            if lse.legal_service == lsr.legal_service:
                rate = lsr.rate

        if rate:
            services_to_invoice.append({
                'reference_type': 'Legal Service Entry',
                'reference_name': lse.name,
                'service': lse.legal_service,
                'qty': lse.qty,
                'rate': rate
            })
        else:
            services_to_invoice.append({
                'reference_type': 'Legal Service Entry',
                'reference_name': lse.name,
                'service': lse.legal_service,
                'qty': lse.qty
            })
    
    return services_to_invoice

@frappe.whitelist()
def upload_portal_document(doctype, docname, file_name, file_content):
    # Verify ownership
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

    doc = frappe.get_doc(doctype, docname)
    if doc.customer != customer:
        frappe.throw("Permission Denied", frappe.PermissionError)

    # Create File record
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "content": file_content,
        "is_private": 1
    })
    _file.save(ignore_permissions=True)
    
    # Notify Admin
    try:
        admin_email = frappe.db.get_value("User", {"name": "Administrator"}, "email") or "admin@example.com"
        customer_name = frappe.db.get_value("Customer", customer, "customer_name")
        
        frappe.sendmail(
            recipients=[admin_email],
            subject=f"New Document Uploaded [{doctype}]: {file_name}",
            message=f"""
                <p>Hello Administrator,</p>
                <p>A new document has been uploaded by <b>{customer_name}</b>.</p>
                <p><b>Target:</b> {doctype} - {docname}</p>
                <p><b>File Name:</b> {file_name}</p>
                <p><a href="{frappe.utils.get_url_to_form(doctype, docname)}">View Record in Desk</a></p>
            """
        )
    except Exception:
        pass

    return _file.name

@frappe.whitelist()
def send_customer_query(message):
    user_email = frappe.session.user
    customer = frappe.db.get_value("Customer", {"email_id": user_email}, "name")
    customer_name = frappe.db.get_value("Customer", customer, "customer_name") or user_email

    # 1. Create an Issue record in the system
    try:
        issue = frappe.get_doc({
            "doctype": "Issue",
            "subject": f"Portal Query: {message[:50]}...",
            "customer": customer,
            "raised_by": user_email,
            "description": message,
            "status": "Open",
            "priority": "Medium"
        })
        issue.insert(ignore_permissions=True)
        issue_name = issue.name
    except Exception:
        issue_name = None

    # 2. Send Email Notification
    admin_email = frappe.db.get_value("User", {"name": "Administrator"}, "email") or "admin@example.com"
    
    msg = f"""
        <p>You have received a new query from the customer portal:</p>
        <blockquote style="padding: 10px; background: #f1f5f9; border-left: 4px solid #4f46e5;">
            {message}
        </blockquote>
        <p><b>From:</b> {customer_name} ({user_email})</p>
    """
    if issue_name:
        msg += f'<p><a href="{frappe.utils.get_url_to_form("Issue", issue_name)}">View Issue in Desk</a></p>'

    frappe.sendmail(
        recipients=[admin_email],
        subject=f"Customer Portal Query from {customer_name}",
        message=msg
    )

@frappe.whitelist()
def get_customer_contact_info(customer):
    if not customer:
        return {}

    customer_doc = frappe.get_value("Customer", customer, ["customer_name", "mobile_no", "email_id"], as_dict=True)
    if not customer_doc:
        return {}

    res = {
        "customer_name": customer_doc.customer_name,
        "mobile_no": customer_doc.mobile_no,
        "email_id": customer_doc.email_id
    }

    # If mobile/email missing on Customer, try to fetch from linked Contact
    if not res["mobile_no"] or not res["email_id"]:
        contact_details = frappe.db.sql("""
            SELECT c.mobile_no, c.email_id 
            FROM `tabContact` c
            JOIN `tabDynamic Link` dl ON dl.parent = c.name
            WHERE dl.link_doctype = 'Customer' AND dl.link_name = %s
            ORDER BY c.is_primary_contact DESC, c.creation DESC
            LIMIT 1
        """, (customer,), as_dict=True)
        
        if contact_details:
            if not res["mobile_no"]: res["mobile_no"] = contact_details[0].mobile_no
            if not res["email_id"]: res["email_id"] = contact_details[0].email_id

    return res