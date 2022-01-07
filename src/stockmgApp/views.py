from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import csv
from .models import *
from .forms import *
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
	context = {
		"webtitle" : "Home Page",
		"title" : "Welcome: Stock Management Web Application",
		"home_page" : "active",
		"navbartitle" : "Add Items"
	}
	return render(request, "home.html", context)


@login_required
def list_items(request):
	form = StockSearchForm(request.POST or None)
	queryset = Stock.objects.all()
	if request.method=='POST':
		queryset=Stock.objects.filter(#category__icontains=form['category'].value(), 
									item_name__icontains=form['item_name'].value()
									)

	if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="List of stock.csv"'
			writer = csv.writer(response)
			writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY', 'PRODUCT_URL'])
			instance = queryset
			for stock in instance:
				writer.writerow([stock.category, stock.item_name, stock.quantity, stock.product_url])
			return response
	context = {
		"webtitle" : "List Items",
		"title" : "List of Items",
		"list_items_page" : "active",
		"queryset" : queryset,
		"form" : form,
		"navbartitle" : "Add Items"
	}
	return render(request, "list_items.html", context)

@login_required
def add_items(request):
	form = StockCreateForm(request.POST or None)
	if form.is_valid():
		form.save()
		messages.success(request, 'Successfully Saved')
		return redirect('/list_items')
	context = {
		"webtitle" : "Add Items",
		"title" : "Add Items",
		"add_items_page" : "active",
		"navbartitle" : "Add Items",
		"form": form
	}
	return render(request, "add_items.html", context)

@login_required
def update_items(request, myID):
	queryset = Stock.objects.get(id=myID)
	form = StockUpdateForm(instance=queryset)

	if request.method == 'POST':
		form = StockUpdateForm(request.POST, instance=queryset)

		if form.is_valid():
			form.save()
			messages.success(request, 'Successfully Updated!')
			return redirect('/list_items')

	context = {
		"webtitle" : "Update Items",
		"title" : "Update Items",
		"add_items_page" : "active",
		"navbartitle" : "Update Items",
		"form": form
	}
	return render(request, "add_items.html", context)

@login_required
def delete_items(request, myID):
	queryset = Stock.objects.get(id=myID)
	if request.method == 'POST':
		queryset.delete()
		messages.success(request, 'Successfully Deleted!')
		return redirect('/list_items')

	context = {
		"webtitle" : "Delete Item"
	}

	return render(request, 'delete.html', context)

@login_required
def stock_details(request, pk):
	queryset = Stock.objects.get(id=pk)
	context = {
		"webtitle" : "Item Details",
		"add_items_page" : "active",
		"navbartitle" : "Item Details",
		"title": queryset.item_name,
		"queryset": queryset
	}
	return render(request, "stock_details.html", context)

@login_required
def issue_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = IssueForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.receive_quantity = 0
		instance.quantity -= instance.issue_quantity
		instance.issue_by = str(request.user)
		messages.success(request, "Issued SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name) + "s now left in Store")
		instance.save()

		return redirect('/stock_details/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())

	context = {
		"webtitle" : "Issue Item",
		"title": 'Issue ' + str(queryset.item_name),
		"queryset": queryset,
		"form": form,
		"username": 'Issue By: ' + str(request.user),
	}
	return render(request, "add_items.html", context)


@login_required
def receive_items(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReceiveForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.issue_quantity = 0
		instance.quantity += instance.receive_quantity
		instance.receive_by = str(request.user)
		instance.save()
		messages.success(request, "Received SUCCESSFULLY. " + str(instance.quantity) + " " + str(instance.item_name)+"s now in Store")

		return redirect('/stock_details/'+str(instance.id))
		# return HttpResponseRedirect(instance.get_absolute_url())
	context = {
			"webtitle" : "Receive Items",
			"title": 'Receive ' + str(queryset.item_name),
			"instance": queryset,
			"form": form,
			"username": 'Receive By: ' + str(request.user),
		}
	return render(request, "add_items.html", context)


@login_required
def reorder_level(request, pk):
	queryset = Stock.objects.get(id=pk)
	form = ReorderLevelForm(request.POST or None, instance=queryset)
	if form.is_valid():
		instance = form.save(commit=False)
		instance.save()
		messages.success(request, "Reorder level for " + str(instance.item_name) + " is updated to " + str(instance.reorder_level))

		return redirect("/list_items")
	context = {
			"webtitle" : "Update Re-Order Level",
			"add_items_page" : "active",
			"navbartitle" : "Update Re-Order Level",
			"instance": queryset,
			"form": form,
		}
	return render(request, "add_items.html", context)


@login_required
def list_history(request):
	form = StockHistorySearchForm(request.POST or None)
	queryset = StockHistory.objects.all()
	if request.method == 'POST':
		category = form['category'].value()
		if form['start_date'].value()=="" and form['end_date'].value()=="":
			queryset = StockHistory.objects.filter(
									item_name__icontains=form['item_name'].value()
									)
		else:
			queryset = StockHistory.objects.filter(
				item_name__icontains=form['item_name'].value(),
				last_updated__range=[
										form['start_date'].value(),
										form['end_date'].value()
									]
				)

		if (category != ''):
			queryset = queryset.filter(category_id=category)

		if form['export_to_CSV'].value() == True:
			response = HttpResponse(content_type='text/csv')
			response['Content-Disposition'] = 'attachment; filename="Stock History.csv"'
			writer = csv.writer(response)
			writer.writerow(
				['CATEGORY', 
				'ITEM NAME',
				'QUANTITY', 
				'ISSUE QUANTITY', 
				'RECEIVE QUANTITY', 
				'RECEIVE BY', 
				'ISSUE BY', 
				'LAST UPDATED'])
			instance = queryset
			for stock in instance:
				writer.writerow(
				[stock.category, 
				stock.item_name, 
				stock.quantity, 
				stock.issue_quantity, 
				stock.receive_quantity, 
				stock.receive_by, 
				stock.issue_by, 
				stock.last_updated])
			return response

	context = {
		"webtitle" : "History of Items",
		"title" : "History of Items",
		"item_history_page" : "active",
		"navbartitle" : "Add Items",
		"queryset": queryset,
		"form": form,
	}
	return render(request, "list_history.html",context)