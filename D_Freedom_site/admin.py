from django.contrib import admin
from .models import Blog, Price, Estimate, EstimateItem

# Register your models here.
admin.site.register(Blog)
admin.site.register(Price)

class EstimateItemInline(admin.TabularInline):
    model = Estimate.items.through
    extra = 0
    verbose_name = "見積項目"
    verbose_name_plural = "見積項目一覧"
    
    def get_readonly_fields(self, request, obj=None):
        return ['estimateitem']
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ['estimate_number', 'client_name', 'issue_date', 'subtotal', 'tax_amount', 'total']
    search_fields = ['estimate_number', 'client_name', 'client_email']
    list_filter = ['issue_date', 'created_at']
    readonly_fields = ['estimate_number', 'issue_date', 'expiry_date', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'total']
    fieldsets = [
        ('基本情報', {'fields': ['estimate_number', 'issue_date', 'expiry_date']}),
        ('クライアント情報', {'fields': ['client_name', 'client_address', 'client_email', 'client_tel']}),
        ('備考', {'fields': ['notes']}),
        ('金額情報', {'fields': ['subtotal', 'tax_amount', 'total']}),
        ('システム情報', {'fields': ['created_at', 'updated_at'], 'classes': ['collapse']}),
    ]
    inlines = [EstimateItemInline]
    
    def subtotal(self, obj):
        return f"¥{obj.subtotal:,}"
    subtotal.short_description = '小計 (税抜)'
    
    def tax_amount(self, obj):
        return f"¥{obj.tax_amount:,}"
    tax_amount.short_description = '消費税'
    
    def total(self, obj):
        return f"¥{obj.total:,}"
    total.short_description = '合計 (税込)'

@admin.register(EstimateItem)
class EstimateItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit_price', 'tax_rate', 'subtotal', 'total']
    search_fields = ['name', 'description']
    list_filter = ['tax_rate']
    
    def subtotal(self, obj):
        return f"¥{obj.subtotal:,}"
    subtotal.short_description = '小計 (税抜)'
    
    def total(self, obj):
        return f"¥{obj.total:,}"
    total.short_description = '合計 (税込)'
