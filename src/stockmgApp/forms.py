from django import forms
from django.db import models
from django.forms import fields
from .models import Stock, StockHistory

class StockCreateForm(forms.ModelForm):
	class Meta:
		model=Stock
		fields = ['category', 'item_name', 'quantity', 'reorder_level', 'product_url']

	#form validation to check if category field is not blank and doesn't already exist
	# def clean_category(self):
	# 	category = self.cleaned_data.get('category')
	# 	if not category:
	# 		raise forms.ValidationError('This field is required')

	# 	for something in Stock.objects.all():
	# 		if something.category==category:
	# 			raise forms.ValidationError('Category {} already exists in the database'.format(category))

	# 	return category


	#form validation to check if item_name field is not blank and doesn't already exist
	def clean_item_name(self):
		item_name = self.cleaned_data.get('item_name')

		if not item_name:
			raise forms.ValidationError('This field is required')

		for something in Stock.objects.all():
			if something.item_name==item_name:
				raise forms.ValidationError('Item Name {} already exists in the database.'.format(item_name))

		return item_name


class StockSearchForm(forms.ModelForm):
	export_to_CSV = forms.BooleanField(required=False)
	class Meta:
		model=Stock
		fields = ["category", "item_name"]



class StockUpdateForm(forms.ModelForm):
	class Meta:
		model=Stock
		fields = ['category', 'item_name', 'quantity', 'product_url']


class IssueForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['issue_quantity', 'issue_to']


class ReceiveForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['receive_quantity']


class ReorderLevelForm(forms.ModelForm):
	class Meta:
		model = Stock
		fields = ['reorder_level']


class StockHistorySearchForm(forms.ModelForm):
	export_to_CSV = forms.BooleanField(required=False)
	start_date = forms.DateTimeField(required=False)
	end_date = forms.DateTimeField(required=False)
	class Meta:
		model = StockHistory
		fields = ['category', 'item_name', 'start_date', 'end_date']