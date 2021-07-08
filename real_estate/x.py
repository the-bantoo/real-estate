import frappe
from frappe import _
"""
def create_sales_order(opportunity, method):
    sales_order = frappe.get_doc({
	"doctype": "Sales Order",
	"customer": "My new project",
	"status": "Open"
    })
    sales_order.insert()
"""

@frappe.whitelist()
def insert_lead(id, name):
    opportunity = frappe.get_all('Opportunity', filters={'property_id': id})
    length = len(opportunity)
    if length != 0:
        for value in opportunity:
            x = value.get('name')
            z = frappe.get_doc('Opportunity', x)
            row = z.append("property_bidding", {
                "lead": name,
                })
            row.insert()