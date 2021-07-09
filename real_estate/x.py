import frappe
from frappe import _

@frappe.whitelist()
def sales_order(name):
    opportunity = frappe.get_doc('Opportunity', name)
    if opportunity.workflow_state == "Finalized":
        customer = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": opportunity.customer_name,
            })
        customer.insert()

        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": opportunity.customer_name,
            "delivery_date": "2021-07-23",
            "items": [
                {
                    "item_code": "Property",
                    "qty": 1,
                    "rate": opportunity.opportunity_amount,
                }
            ]
        })
        sales_order.insert()

"""
def create_sales_order(opportunity, method):
    if opportunity.workflow_state == "Finalized":
        frappe.errprint("Test")
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": opportunity.customer_name,
            "delivery_date": "2021-07-23",
            "items": [
                {
                    "item_code": "Property",
                    "qty": 1,
                    "rate": opportunity.opportunity_amount,
                }
            ]
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