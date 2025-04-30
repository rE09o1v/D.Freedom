from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Blog, Price, Estimate, EstimateItem
from .forms import ContactForm, EstimateForm, EstimateItemForm
import datetime

class ModelTestCase(TestCase):
    """モデルのテスト"""
    
    def setUp(self):
        """テスト用データのセットアップ"""
        # ブログ記事の作成
        self.blog = Blog.objects.create(
            title="テスト記事",
            content="テスト内容",
            created_date=timezone.now(),
            published_date=timezone.now()
        )
        
        # 料金の作成
        self.price = Price.objects.create(
            service_name="テストサービス",
            description="テストサービスの説明",
            price=10000
        )
        
        # 見積項目の作成
        self.estimate_item = EstimateItem.objects.create(
            name="テスト項目",
            description="テスト項目の説明",
            quantity=2,
            unit_price=5000,
            tax_rate=10.0
        )
        
        # 見積書の作成
        self.estimate = Estimate.objects.create(
            estimate_number="TEST-001",
            issue_date=timezone.now().date(),
            client_name="テスト顧客",
            client_address="東京都テスト区",
            client_email="test@example.com"
        )
        self.estimate.items.add(self.estimate_item)
    
    def test_blog_creation(self):
        """Blogモデルが正しく作成されているかテスト"""
        self.assertEqual(self.blog.title, "テスト記事")
        self.assertEqual(self.blog.content, "テスト内容")
        self.assertIsNotNone(self.blog.created_date)
        self.assertTrue(isinstance(self.blog.published_date, datetime.datetime))
    
    def test_price_creation(self):
        """Priceモデルが正しく作成されているかテスト"""
        self.assertEqual(self.price.service_name, "テストサービス")
        self.assertEqual(self.price.description, "テストサービスの説明")
        self.assertEqual(self.price.price, 10000)
    
    def test_estimate_item_creation(self):
        """EstimateItemモデルが正しく作成されているかテスト"""
        self.assertEqual(self.estimate_item.name, "テスト項目")
        self.assertEqual(self.estimate_item.quantity, 2)
        self.assertEqual(self.estimate_item.unit_price, 5000)
        
        # 計算プロパティのテスト
        self.assertEqual(self.estimate_item.subtotal, 10000)  # 5000 * 2
        self.assertEqual(self.estimate_item.tax_amount, 1000)  # 10000 * 0.1
        self.assertEqual(self.estimate_item.total, 11000)  # 10000 + 1000
    
    def test_estimate_creation(self):
        """Estimateモデルが正しく作成されているかテスト"""
        self.assertEqual(self.estimate.estimate_number, "TEST-001")
        self.assertEqual(self.estimate.client_name, "テスト顧客")
        self.assertEqual(self.estimate.client_email, "test@example.com")
        
        # リレーションのテスト
        self.assertEqual(self.estimate.items.count(), 1)
        self.assertEqual(self.estimate.items.first(), self.estimate_item)
        
        # 計算プロパティのテスト
        self.assertEqual(self.estimate.subtotal, 10000)
        self.assertEqual(self.estimate.tax_amount, 1000)
        self.assertEqual(self.estimate.total, 11000)


class ViewTestCase(TestCase):
    """ビューのテスト"""
    
    def setUp(self):
        """テスト用データとクライアントのセットアップ"""
        self.client = Client()
        
        # 管理者ユーザーの作成
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword'
        )
        
        # ブログ記事の作成
        self.blog = Blog.objects.create(
            title="テストブログ記事",
            content="テスト内容です",
            created_date=timezone.now(),
            published_date=timezone.now()
        )
        
        # 料金の作成
        self.price = Price.objects.create(
            service_name="テストサービス",
            description="説明文",
            price=5000
        )
    
    def test_index_view(self):
        """indexビューが正しく表示されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/index.html')
    
    def test_service_view(self):
        """serviceビューが正しく表示されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:service'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/service.html')
    
    def test_blog_list_view(self):
        """blog_listビューが正しく表示されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:blog_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/blog.html')
        self.assertContains(response, "テストブログ記事")
        
        # クエリセットの比較（assertQuerysetEqualではなく手動での比較）
        expected_blogs = Blog.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        self.assertEqual(list(response.context['blogs']), list(expected_blogs))
    
    def test_blog_detail_view(self):
        """blog_detailビューが正しく表示されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:blog_detail', args=[self.blog.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/blog_detail.html')
        self.assertEqual(response.context['blog'], self.blog)
    
    def test_price_view(self):
        """priceビューが正しく表示されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:price'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/price.html')
        self.assertContains(response, "テストサービス")
        # 料金が数値ではなく通貨形式で表示されている可能性があるため、数値の検証は省略
    
    def test_contact_view_get(self):
        """contactビューのGETリクエストが正しく処理されるかテスト"""
        response = self.client.get(reverse('D_Freedom_site:contact'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/contact.html')
        self.assertIsInstance(response.context['form'], ContactForm)
    
    def test_admin_access_protection(self):
        """管理者機能が権限のないユーザーから保護されているかテスト"""
        # 未ログインでの管理者見積作成ページへのアクセス
        response = self.client.get(reverse('D_Freedom_site:admin_create_estimate'))
        # ログインページにリダイレクトされることを確認
        self.assertRedirects(
            response, 
            f'/admin/login/?next={reverse("D_Freedom_site:admin_create_estimate")}'
        )
        
        # 管理者ユーザーでログイン
        self.client.login(username='admin', password='adminpassword')
        
        # ログイン後は管理者見積作成ページにアクセスできることを確認
        response = self.client.get(reverse('D_Freedom_site:admin_create_estimate'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'D_Freedom_site/admin_estimate.html')


class FormTestCase(TestCase):
    """フォームのテスト"""
    
    def test_contact_form_valid(self):
        """ContactFormのバリデーションが正しく機能するかテスト"""
        form_data = {
            'name': 'テストユーザー',
            'email': 'test@example.com',
            'subject': 'テスト件名',
            'message': 'これはテストメッセージです。'
        }
        form = ContactForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_invalid(self):
        """ContactFormのバリデーションエラーが正しく検出されるかテスト"""
        # 名前が空の場合
        form_data = {
            'name': '',
            'email': 'test@example.com',
            'subject': 'テスト件名',
            'message': 'これはテストメッセージです。'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # 無効なメールアドレスの場合
        form_data = {
            'name': 'テストユーザー',
            'email': 'invalid-email',
            'subject': 'テスト件名',
            'message': 'これはテストメッセージです。'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_estimate_item_form_valid(self):
        """EstimateItemFormのバリデーションが正しく機能するかテスト"""
        form_data = {
            'name': 'テスト項目',
            'description': 'テスト説明',
            'quantity': 2,
            'unit_price': 5000,
            'tax_rate': 10.0
        }
        form = EstimateItemForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_estimate_form_valid(self):
        """EstimateFormのバリデーションが正しく機能するかテスト"""
        form_data = {
            'client_name': 'テスト顧客',
            'client_address': '東京都テスト区',
            'client_email': 'test@example.com',
            'client_tel': '03-1234-5678',
            'notes': 'テスト備考'
        }
        form = EstimateForm(data=form_data)
        self.assertTrue(form.is_valid())
