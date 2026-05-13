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
def upload_portal_document(case, file_name, file_content):
    # Verify ownership
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

    case_doc = frappe.get_doc("Case", case)
    if case_doc.customer != customer:
        frappe.throw("Permission Denied", frappe.PermissionError)

    # Create File record
    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": "Case",
        "attached_to_name": case,
        "content": file_content,
        "is_private": 1
    })
    _file.save(ignore_permissions=True)
    
    return _file.name