from django.db import models
from django.utils import timezone

# Create your models here.

class Blog(models.Model):
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='内容')
    created_date = models.DateTimeField(default=timezone.now, verbose_name='作成日')
    published_date = models.DateTimeField(blank=True, null=True, verbose_name='公開日')
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, verbose_name='画像')
    
    def publish(self):
        self.published_date = timezone.now()
        self.save()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'ブログ'
        verbose_name_plural = 'ブログ'

class Price(models.Model):
    drawing_size = models.CharField(max_length=100, verbose_name='図面サイズ', default='')
    price = models.IntegerField(verbose_name='料金')
    note = models.CharField(max_length=100, blank=True, null=True, verbose_name='備考')
    
    def __str__(self):
        return self.drawing_size
    
    class Meta:
        verbose_name = '料金'
        verbose_name_plural = '料金'

class EstimateItem(models.Model):
    """見積書の項目モデル"""
    name = models.CharField(max_length=200, verbose_name='項目名')
    description = models.TextField(blank=True, null=True, verbose_name='詳細')
    quantity = models.IntegerField(verbose_name='数量', default=1)
    unit_price = models.IntegerField(verbose_name='単価')
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0, verbose_name='税率 (%)')
    
    @property
    def subtotal(self):
        """小計 (税抜)"""
        return self.quantity * self.unit_price
    
    @property
    def tax_amount(self):
        """消費税額"""
        return int(self.subtotal * (self.tax_rate / 100))
    
    @property
    def total(self):
        """合計 (税込)"""
        return self.subtotal + self.tax_amount
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '見積項目'
        verbose_name_plural = '見積項目'

class Estimate(models.Model):
    """見積書モデル"""
    estimate_number = models.CharField(max_length=50, verbose_name='見積番号')
    issue_date = models.DateField(default=timezone.now, verbose_name='発行日')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='有効期限')
    client_name = models.CharField(max_length=100, verbose_name='クライアント名')
    client_address = models.TextField(verbose_name='クライアント住所')
    client_email = models.EmailField(blank=True, null=True, verbose_name='クライアントメール')
    client_tel = models.CharField(max_length=20, blank=True, null=True, verbose_name='クライアント電話番号')
    items = models.ManyToManyField(EstimateItem, related_name='estimates', verbose_name='見積項目')
    notes = models.TextField(blank=True, null=True, verbose_name='備考')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    @property
    def subtotal(self):
        """小計 (税抜合計)"""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def tax_amount(self):
        """消費税額合計"""
        return sum(item.tax_amount for item in self.items.all())
    
    @property
    def total(self):
        """合計 (税込)"""
        return sum(item.total for item in self.items.all())
    
    def __str__(self):
        return f"{self.estimate_number} - {self.client_name}"
    
    class Meta:
        verbose_name = '見積書'
        verbose_name_plural = '見積書'
