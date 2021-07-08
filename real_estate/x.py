import frappe
from frappe import _

@frappe.whitelist()
def insert_lead(name):
    opportunity = frappe.get_all('Opportunity', filters={'property_id': name}, fields=['price', 'property_bidding'])
    frappe.errprint(opportunity.price)
    """if name == opportunity.property_id:
        row = opportunity.append("property bidding", {
            "item_code": "Mentee Membership",
			"item_name": "Mentee Membership",
			"description": "Mentor Membership",
            })
        row.insert()"""