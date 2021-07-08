from __future__ import unicode_literals
import os
import re
import jwt
import sys
import json
import base64
import frappe
import six
import traceback
import io
from frappe import _, bold
from pyqrcode import create as qrcreate
from erpnext.regional.india.utils import get_gst_accounts, get_place_of_supply
from frappe.utils.data import cstr, cint, format_date, flt, time_diff_in_seconds, now_datetime

from frappe.utils import cstr, cint, get_fullname
from frappe import msgprint, _
from frappe.model.mapper import get_mapped_doc
from erpnext.setup.utils import get_exchange_rate
from erpnext.utilities.transaction_base import TransactionBase
from erpnext.accounts.party import get_party_account_currency
from frappe.email.inbox import link_communication_to_document

@frappe.whitelist()
def make_customer(source_name, target_doc=None):
	return _make_customer(source_name, target_doc)


def _make_customer(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		if source.company_name:
			target.customer_type = "Company"
			target.customer_name = source.company_name
		else:
			target.customer_type = "Individual"
			target.customer_name = source.lead_name

		target.customer_group = frappe.db.get_default("Customer Group")

	doclist = get_mapped_doc("Lead", source_name,
		{"Lead": {
			"doctype": "Customer",
			"field_map": {
				"name": "lead_name",
				"company_name": "customer_name",
				"contact_no": "phone_1",
				"fax": "fax_1"
			}
		}}, target_doc, set_missing_values, ignore_permissions=ignore_permissions)

	return doclist

@frappe.whitelist()
def make_sales_order(source_name, target_doc=None):
	
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges
		sales_order = frappe.get_doc(target)
		frappe.errprint(source_name)
		opportunity = frappe.get_doc("Opportunity", source_name)
		make_customer(opportunity.party_name)

		company_currency = frappe.get_cached_value('Company',  sales_order.company,  "default_currency")

		if sales_order.customer:
			party_account_currency = get_party_account_currency("Customer", sales_order.customer, sales_order.company)
		else:
			party_account_currency = company_currency

		sales_order.currency = party_account_currency or company_currency

		if company_currency == sales_order.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(sales_order.currency, company_currency,
				sales_order.transaction_date, args="for_selling")
		
		frappe.errprint("1")

		sales_order.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges("Sales Taxes and Charges Template", company=sales_order.company)
		if taxes.get('taxes'):
			sales_order.update(taxes)

		sales_order.run_method("set_missing_values")
		sales_order.run_method("calculate_taxes_and_totals")
		if not source.with_items:
			sales_order.opportunity = source.name

	doclist = get_mapped_doc("Opportunity", source_name, {
		"Opportunity": {
			"doctype": "Sales Order",
			"field_map": {
				"customer_name": "customer",
				"opportunity_type": "order_type",
				"name": "enq_no",
			}
		},
		"Opportunity Item": {
			"doctype": "sales_order Item",
			"field_map": {
				"parent": "prevdoc_docname",
				"parenttype": "prevdoc_doctype",
				"uom": "stock_uom"
			},
			"add_if_empty": True
		}
	}, target_doc, set_missing_values)

	return doclist


def set_property_qr(property, method=None):
	if not property.qr_url:

		signed_qr_code = "https://h-saedan.saudi-bti.com" + property.get_url()
		doctype = property.doctype
		docname = property.name

		filename = 'QRCode_{}.png'.format(docname).replace(os.path.sep, "__")

		qr_image = io.BytesIO()
		url = qrcreate(signed_qr_code, error='L')
		url.png(qr_image, scale=2, quiet_zone=1)
		_file = frappe.get_doc({
			"doctype": "File",
			"file_name": filename,
			"attached_to_doctype": doctype,
			"attached_to_name": docname,
			"attached_to_field": "qrcode_image",
			"is_private": 1,
			"content": qr_image.getvalue()})
		_file.save()
		frappe.db.commit()
		property.db_set('qr_url', _file.file_url)
		property.reload()
