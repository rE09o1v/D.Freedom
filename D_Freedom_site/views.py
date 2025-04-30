from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.forms import formset_factory
from django.db import transaction
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from .models import Blog, Price, Estimate, EstimateItem
from .forms import ContactForm, EstimateForm, EstimateItemForm
from .utils import generate_estimate_pdf
import uuid

def index(request):
    """トップページ"""
    return render(request, 'D_Freedom_site/index.html')

def service(request):
    """取扱内容ページ"""
    return render(request, 'D_Freedom_site/service.html')

def blog_list(request):
    """ブログ一覧ページ"""
    blogs = Blog.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    return render(request, 'D_Freedom_site/blog.html', {'blogs': blogs})

def blog_detail(request, pk):
    """ブログ詳細ページ"""
    blog = get_object_or_404(Blog, pk=pk)
    return render(request, 'D_Freedom_site/blog_detail.html', {'blog': blog})

def contact(request):
    """問い合わせページ"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # フォームのデータを取得
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject'] or 'D.Freedom サイトからのお問い合わせ'
            message = form.cleaned_data['message']
            
            # メール本文の作成
            email_context = {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            }
            email_text = render_to_string('D_Freedom_site/email/contact_email.txt', email_context)
            
            # 管理者へのメール送信
            admin_email = settings.EMAIL_HOST_USER
            send_mail(
                subject=f'[D.Freedom問い合わせ] {subject}',
                message=email_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                fail_silently=False,
            )
            
            # ユーザーへの自動返信
            auto_reply_subject = 'D.Freedom - お問い合わせありがとうございます'
            auto_reply_message = render_to_string('D_Freedom_site/email/auto_reply_email.txt', {
                'name': name,
            })
            send_mail(
                subject=auto_reply_subject,
                message=auto_reply_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # 完了メッセージを追加
            messages.success(request, 'お問い合わせを送信しました。回答をお待ちください。')
            
            # 送信後はフォームをクリアしてリダイレクト
            return redirect('D_Freedom_site:contact_thanks')
    else:
        form = ContactForm()
    
    return render(request, 'D_Freedom_site/contact.html', {'form': form})

def contact_thanks(request):
    """問い合わせ完了ページ"""
    return render(request, 'D_Freedom_site/contact_thanks.html')

def price(request):
    """料金ページ"""
    prices = Price.objects.all()
    return render(request, 'D_Freedom_site/price.html', {'prices': prices})

def modeling(request):
    """3Dモデリングページ"""
    return render(request, 'D_Freedom_site/modeling.html')

def drawing(request):
    """図面作成ページ"""
    return render(request, 'D_Freedom_site/drawing.html')

def printing(request):
    """3Dプリンタ試作品提供ページ"""
    return render(request, 'D_Freedom_site/printing.html')

def create_estimate(request):
    """一般ユーザーから見積書作成ページへのアクセスをリダイレクト"""
    messages.info(request, '見積書作成機能は移動しました。必要な場合は管理者にご連絡ください。')
    return redirect('D_Freedom_site:price')

def estimate_detail(request, pk):
    """見積書詳細ページ"""
    estimate = get_object_or_404(Estimate, pk=pk)
    return render(request, 'D_Freedom_site/estimate_detail.html', {'estimate': estimate})

def download_estimate_pdf(request, pk):
    """見積書PDFダウンロード"""
    estimate = get_object_or_404(Estimate, pk=pk)
    
    # PDF生成 (ReportLab使用)
    pdf = generate_estimate_pdf(estimate)
    
    if pdf:
        # HTTPレスポンスとしてPDFを返す
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"estimate_{estimate.estimate_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    # エラーが発生した場合
    messages.error(request, 'PDFの生成中にエラーが発生しました。')
    return redirect('D_Freedom_site:estimate_detail', pk=estimate.pk)

@staff_member_required(login_url='admin:login')
def admin_create_estimate(request):
    """管理者用見積書作成ページ"""
    # 料金情報を取得
    services = Price.objects.all()
    
    # フォームセットを作成（複数の項目を追加できるように）
    EstimateItemFormSet = formset_factory(EstimateItemForm, extra=1)
    
    if request.method == 'POST':
        # POSTリクエストの処理
        estimate_form = EstimateForm(request.POST)
        formset = EstimateItemFormSet(request.POST, prefix='items')
        
        if estimate_form.is_valid() and formset.is_valid():
            with transaction.atomic():
                # 見積書の保存
                estimate = estimate_form.save(commit=False)
                estimate.estimate_number = f"EST-{uuid.uuid4().hex[:8].upper()}"
                estimate.issue_date = timezone.now().date()
                estimate.expiry_date = timezone.now().date() + timezone.timedelta(days=30)
                estimate.save()
                
                # 見積項目の保存
                for form in formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.save()
                        estimate.items.add(item)
                
                messages.success(request, '見積書が正常に作成されました')
                return redirect('D_Freedom_site:estimate_detail', pk=estimate.pk)
    else:
        # GETリクエストの処理
        estimate_form = EstimateForm()
        formset = EstimateItemFormSet(prefix='items')
    
    context = {
        'estimate_form': estimate_form,
        'formset': formset,
        'services': services,
    }
    
    return render(request, 'D_Freedom_site/admin_estimate.html', context)
