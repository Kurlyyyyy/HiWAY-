from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import InfrastructureReport
from .forms import ReportForm, AdminUpdateForm

def role_select_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'registration/role_select.html')

def public_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not (user.is_staff or user.is_superuser):
                login(request, user)
                return redirect('public_dashboard')
            else:
                form.add_error(None, "Administrators must log in through the Staff Portal.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'registration/public_login.html', {'form': form})

def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                form.add_error(None, "Access restricted to authorized city staff accounts.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'registration/admin_login.html', {'form': form})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('public_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def dashboard_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('public_dashboard')

@login_required
def public_dashboard_view(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
        
    reports = InfrastructureReport.objects.exclude(status='Resolved').order_by('created_at')
    
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                report.latitude = float(lat)
                report.longitude = float(lng)
                
            report.save()
            return redirect('public_dashboard')
    else:
        form = ReportForm()

    context = {
        'reports': reports,
        'count': reports.count(),
        'form': form,
    }
    return render(request, 'core/public_dashboard.html', context)

@login_required
def admin_dashboard_view(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('public_dashboard')

    CATEGORY_CHOICES = [
        'Road Damage',
        'Excessive Flooding',
        'Landslide',
        'Faded Pavement Markings',
        'Clogged Drainage',
        'Long-standing Unfinished Construction',
        'Neglected / Broken Infrastructure',
        'Fallen Tree Obstruction',
        'Improper Garbage Dump Sites',
        'Defective Street Lights',
        'Electrical Grid Unreliability',
        'Defective Traffic Lights',
    ]

    reports = InfrastructureReport.objects.all()

    # 1. Search / Filter by Category
    selected_category = request.GET.get('category', '')
    if selected_category and selected_category != 'All':
        reports = reports.filter(category=selected_category)

    # 2. Sorting Options
    sort_by = request.GET.get('sort', 'priority')
    if sort_by == 'priority':
        reports = reports.order_by('-priority_score', '-created_at')
    elif sort_by == 'oldest':
        reports = reports.order_by('created_at')
    elif sort_by == 'newest':
        reports = reports.order_by('-created_at')
    else:
        reports = reports.order_by('-priority_score', '-created_at')

    context = {
        'reports': reports,
        'categories': CATEGORY_CHOICES, 
        'selected_category': selected_category,
        'current_sort': sort_by,
        'total_open': InfrastructureReport.objects.exclude(status='Resolved').count(),
        'critical_count': InfrastructureReport.objects.filter(severity__gte=4).exclude(status='Resolved').count(),
        'in_repair_count': InfrastructureReport.objects.filter(status='In Progress').count(),
        'resolved_count': InfrastructureReport.objects.filter(status='Resolved').count(),
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def create_report_view(request):
    """ View para sa pag-submit ng bagong ulat mula sa modal ng base.html """
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
            if lat and lng:
                report.latitude = float(lat)
                report.longitude = float(lng)
                
            report.save()
    return redirect(request.META.get('HTTP_REFERER', 'public_dashboard'))

@login_required
def report_detail_view(request, pk):
    report = get_object_or_404(InfrastructureReport, pk=pk)
    return render(request, 'core/report_detail.html', {'report': report})

@login_required
def support_report_view(request, pk):
    report = get_object_or_404(InfrastructureReport, pk=pk)
    report.support_votes += 1
    report.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def delete_report_view(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        report = get_object_or_404(InfrastructureReport, pk=pk)
        report.delete()
    return redirect('admin_dashboard')

@login_required
def archive_view(request):
    reports = InfrastructureReport.objects.filter(status='Resolved').order_by('-updated_at')
    redo_stack = request.session.get('last_undone_ids', [])
    
    context = {
        'reports': reports,
        'has_undo': reports.exists(), 
        'has_redo': len(redo_stack) > 0, 
        'last_resolved': reports.first(),
    }
    return render(request, 'core/archive.html', context)

@login_required
def advance_report_status_view(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        report = get_object_or_404(InfrastructureReport, pk=pk)
        status_sequence = ['Reported', 'Verified', 'Dispatched', 'In Progress', 'Resolved']
        
        try:
            current_index = status_sequence.index(report.status)
            if current_index < len(status_sequence) - 1:
                old_status = report.status
                new_status = status_sequence[current_index + 1]
                report.status = new_status
                report.save()
                
                undo_stack = request.session.get('status_undo_stack', [])
                undo_stack.append({
                    'report_id': report.id,
                    'title': report.title,
                    'from_status': old_status,
                    'to_status': new_status
                })
                request.session['status_undo_stack'] = undo_stack
                request.session['status_redo_stack'] = []
        except ValueError:
            pass

    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))

@login_required
def archive_undo_last_view(request):
    if request.user.is_staff or request.user.is_superuser:
        last_resolved = InfrastructureReport.objects.filter(status='Resolved').order_by('-updated_at').first()
        if last_resolved:
            last_resolved.status = 'In Progress'
            last_resolved.save()
    return redirect('archive')

@login_required
def archive_redo_last_view(request):
    if request.user.is_staff or request.user.is_superuser:
        
        last_in_progress = InfrastructureReport.objects.filter(status='In Progress').order_by('-updated_at').first()
        if last_in_progress:
            last_in_progress.status = 'Resolved'
            last_in_progress.save()
    return redirect('archive')

@login_required
def revert_report_status_view(request, pk):
    if request.user.is_staff or request.user.is_superuser:
        report = get_object_or_404(InfrastructureReport, pk=pk)
        status_sequence = ['Reported', 'Verified', 'Dispatched', 'In Progress', 'Resolved']
        try:
            current_index = status_sequence.index(report.status)
            if current_index > 0:
                report.status = status_sequence[current_index - 1]
                report.save()
        except ValueError:
            report.status = 'Reported'
            report.save()
    return redirect('admin_dashboard')

@login_required
def delete_report_view(request, pk):
    """ View para sa pag-delete ng ulat mula sa admin dashboard """
    if request.user.is_staff or request.user.is_superuser:
        report = get_object_or_404(InfrastructureReport, pk=pk)
        report.delete()
    return redirect('admin_dashboard')