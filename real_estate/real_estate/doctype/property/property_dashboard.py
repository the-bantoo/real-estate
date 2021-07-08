from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'transactions': [
			{
				'label': _('Orders'),
				'items': ['Customer', 'Lead', 'Opportunity']
			},
			{
				'label': _('Sales'),
				'items': ['Payment Entry', 'Sales Invoice']
			},
		]
	}