app_name = "casecentral"
app_title = "Case Central"
app_publisher = "4C Solutions"
app_description = "Legal Practice Management Application"
app_email = "info@4csolutions.in"
app_license = "MIT"
app_version = "0.0.1"

fixtures = [
    {
		"doctype": "Custom Field",
		"filters" : [
            [
                "name",
                "in",
                [
                    "Task-matter",
                    "Task-custom_matter_type",
                    "Task-case",
                    "Task Type-naming_series",
                    "Task Type-matter_type",
                    "Sales Invoice-matter",
                    "Sales Invoice Item-reference_doctype",
                    "Sales Invoice Item-reference_name",
                    "Payment Entry-custom_matter",
                    "Quality Review-matter",
                    "Quality Review-service",
                    "Quality Goal-service",
                    "Item-isbn",
                    "Item-book_type",
                    "Employee-appointments",
                    "Employee-employee_schedules",
                    "Employee-google_calendar",
                    "Timesheet-matter",
                    "Timesheet-appointment",
                    "Timesheet-case",
                    "Project Template-custom_section_break_jjuzl",
                    "Project Template-custom_service",
                    "Project Template-custom_service_type",
                    "Project Template-custom_matter_type",
                    "Project Template-custom_column_break_9mzvp",
                    "Issue-custom_matter",
                    "Issue-custom_contact_no",
                    "Issue-custom_service"
                ]
            ]
        ]
    },
    {
        "doctype": "Property Setter",
        "filters": [
            [
                "name",
                "in",
                [
                    "Customer-main-search_fields",
                    "Customer-lead_name-hidden",
                    "Customer-opportunity_name-hidden",
                    "Customer-customer_type-default",
                    "Task-project-hidden",
                    "Task-issue-hidden",
                    "Task-task_weight-hidden",
                    "Task-sb_depends_on-hidden",
                    "Task-sb_costing-hidden",
                    "Task-project-in_list_view",
                    "Task-project-in_standard_filter",
                    "Task-is_group-in_list_view",
                    "Task-is_milestone-in_list_view",
                    "Task-main-quick_entry",
                    "Task-subject-allow_in_quick_entry",
                    "Task-status-allow_in_quick_entry",
                    "Task-is_group-bold",
                    "Task-parent_task-bold",
                    "Task-priority-allow_in_quick_entry",
                    "Task-type-allow_in_quick_entry",
                    "Task-type-in_standard_filter",
                    "Task Type-main-naming_rule",
                    "Task Type-main-autoname",
                    "Task Type-main-search_fields",
                    "Task Type-description-in_list_view",
                    "Task Type-description-in_standard_filter",
                    "Task Type-main-title_field",
                    "Task Type-main-show_title_field_in_link",
                    "Issue-customer-fetch_from",
                    "Issue-raised_by-fetch_if_empty"
                ]
            ]
        ]
    },
    {
		"doctype": "Client Script",
		"filters" : [
            [
                "name",
                "in",
                [
                    "Duplicate Contact Check",
                    "Remove Referral from Client",
                    "Quality Review",
                    "Task",
                    "Timsheet",
                    "Issue"
                ]
            ]
        ]
    }
]

# Includes in <head>
app_include_js = "casecentral.bundle.js"

# DocType JS
doctype_js = {
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Payment Entry" : "public/js/payment_entry.js"
}

# Installation
after_install = "casecentral.install.after_install"

# DocType Class Override
override_doctype_class = {
	'Sales Invoice': 'casecentral.overrides.CustomSalesInvoice'
}

# Document Events
doc_events = {
    "Task": {
        "after_insert": "casecentral.doc_events.task.after_insert",
        "on_update": "casecentral.doc_events.task.update_task_matter",
        "after_delete": "casecentral.doc_events.task.update_task_matter"
    },
    "Case": {
        "on_update": "casecentral.doc_events.case.update_case_matter",
        "after_delete": "casecentral.doc_events.case.update_case_matter"
    },
    "Sales Invoice": {
        "on_submit": "casecentral.doc_events.sales_invoice.manage_invoice_submit_cancel",
		"on_cancel": "casecentral.doc_events.sales_invoice.manage_invoice_submit_cancel"
    },
    "Purchase Invoice": {
        "on_submit": "casecentral.doc_events.purchase_invoice.create_book_on_submit"
    },
    "Timesheet": {
        "after_insert": "casecentral.doc_events.timesheet.after_insert",
        "after_delete": "casecentral.doc_events.timesheet.after_delete",
        "on_submit": "casecentral.doc_events.timesheet.on_submit",
        "on_cancel": "casecentral.doc_events.timesheet.on_cancel"
    }
}

# Scheduled Tasks
scheduler_events = {
	"daily": [
		"casecentral.case_central.doctype.caveat.caveat.set_expired_status",
        "casecentral.case_central.doctype.customer_appointment.customer_appointment.update_appointment_status"
	]
}
