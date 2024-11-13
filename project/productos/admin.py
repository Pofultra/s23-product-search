from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .models import Product
import csv
import io

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock']
    search_fields = ['name', 'description']
    list_filter = ['category']
    ordering = ['name']
    actions = ['export_as_csv']
    change_list_template = 'admin/products/product_changelist.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv, name='import_csv'),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'The file must be CSV')
                return HttpResponseRedirect(request.path_info)
            
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            reader = csv.DictReader(io_string)
            
            for row in reader:
                try:
                    Product.objects.create(
                        name=row['name'],
                        description=row['description'],
                        category=row['category'],
                        price=float(row['price']),
                        stock=int(row['stock'])
                    )
                except Exception as e:
                    messages.error(request, f'Error in line {reader.line_num}: {str(e)}')
                    continue
            
            messages.success(request, 'Import completed successfully')
            return HttpResponseRedirect("../")
            
        form = CsvImportForm()
        payload = {
            "form": form,
            "title": "Import products from CSV"
        }
        return render(request, "admin/csv_form.html", payload)

    def export_as_csv(self, request, queryset):
        """
        Export selected products as CSV
        """
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "Export selected products as CSV"
