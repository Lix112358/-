from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse
from .forms import LoginForm, ProjectApplicationForm, AnnouncementForm, MidTermReviewForm, ProjectFinalReportForm, \
    ProjectResultsForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import CustomUser, CourseIdeologyProjects, Announcement, MidTermReview, ProjectFinalReport, MoneyReport
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from datetime import date

User = get_user_model()


def create_announcement(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.author = request.user  # 设置通知的发布者为当前登录的用户
            announcement.save()
            return redirect('announcement_list')  # 假设有一个显示所有通知的页面
    else:
        form = AnnouncementForm()

    return render(request, 'create_announcement.html', {'form': form})


def announcement_list(request):
    announcements = Announcement.objects.all()
    return render(request, 'announcements.html', {'announcements': announcements})


def delete_announcement(request, pk):
    Announcement.objects.filter(pk=pk).delete()
    return redirect('announcement_list')


# 模板登录页
def login2(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']

            user = authenticate(username=username, password=password)

            if user is not None:
                # 确定用户类型
                is_admin = user.is_staff
                if (user_type == 'admin' and is_admin) or (user_type == 'user' and not is_admin):
                    login(request, user)
                    # 根据用户类型重定向到不同页面
                    return redirect('index3' if is_admin else 'index2')
                else:
                    messages.error(request, '用户类型不匹配。')
            else:
                messages.error(request, '学号或密码不正确。')
    else:
        form = LoginForm()
    return render(request, 'login2.html')


# 模板用户主页
def index2(request):
    # 获取当前登录的用户
    user = request.user
    # 获取该用户负责的所有项目
    user_projects = user.led_projects.all()
    # 获取已提交成果的项目
    projects_with_results = CourseIdeologyProjects.objects.filter(
        results__isnull=False,
        leader=request.user  # 可以选择添加这个过滤条件，确保只显示当前用户负责的项目
    ).order_by('-startDate')

    # 合并所有需要传递到模板的数据
    context = {
        'projects': user_projects,
        'projects_with_results': projects_with_results
    }
    return render(request, 'index2.html', context)



# 模板管理员主页
def index3(request):
    User = get_user_model()  # 使用自定义用户模型
    users = User.objects.all()  # 获取所有用户的信息
    return render(request, 'index3.html', {'users': users})


# 模板通知页
def announcements2(request):
    announcements = Announcement.objects.all()
    return render(request, 'announcements2.html', {'announcements': announcements})


# 模板申请项目页
def apply_projects2(request):
    if request.method == 'POST':
        form = ProjectApplicationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.leader = request.user
            project.save()
            # 这里你可以重定向到一个确认页面或者项目进度页面
            return redirect('apply_projects2')
    else:
        form = ProjectApplicationForm()
    return render(request, 'apply_projects2.html', {'form': form})


# 模板进度提示页
def tips(request):
    return render(request, 'tips.html')


# 模板提交中期报告页
def submit_midterm_review(request, project_name):
    project = get_object_or_404(CourseIdeologyProjects, projectName=project_name)

    try:
        mid_term_review = MidTermReview.objects.get(project_name=project_name)
        form = MidTermReviewForm(request.POST or None, instance=mid_term_review)
    except MidTermReview.DoesNotExist:
        form = MidTermReviewForm(request.POST or None, initial={'project_name': project_name})

    if request.method == 'POST':
        if form.is_valid():
            # Save the form first to create or update the MidTermReview instance
            review = form.save(commit=False)
            review.project_name = project_name  # Ensure the project_name is correctly assigned
            review.save()

            # Update the project's midterm report submission status
            project.midterm_report_submitted = True
            project.save()

            # Redirect to the 'my_projects' page after successful submission
            return redirect('my_projects')  # Ensure this is the correct URL name for your projects list page

    # Render the form page with the form instance
    return render(request, 'submit_midterm_review.html', {'form': form, 'project': project})


# 模板查看进度页
def my_projects(request):
    if not request.user.is_authenticated:
        # 可以重定向到登录页面或显示错误消息
        return redirect('login2')  # 替换 'login_url' 为你的登录页面的 URL 名称

    # 获取当前用户的所有项目
    projects = CourseIdeologyProjects.objects.filter(leader=request.user)
    return render(request, 'my_projects.html', {'projects': projects})


# 模板查看中期报告页
def view_midterm_review(request, project_name):
    # 获取中期报告对象，如果不存在则返回404
    review = get_object_or_404(MidTermReview, project_name=project_name)

    # 渲染带有中期报告数据的模板
    return render(request, 'view_midterm_review.html', {'review': review})


def submit_final_report(request, project_name):
    project = get_object_or_404(CourseIdeologyProjects, projectName=project_name)
    try:
        final_report = ProjectFinalReport.objects.get(project_name=project_name)
        form = ProjectFinalReportForm(request.POST or None, instance=final_report)
    except ProjectFinalReport.DoesNotExist:
        final_report = None
        form = ProjectFinalReportForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            if final_report is None:
                # 如果不存在final_report，则创建一个新的，并立即保存
                final_report = form.save(commit=False)
                final_report.project_name = project_name
                final_report.save()
            else:
                # 更新已存在的final_report
                final_report = form.save()

            # 更新项目的结项报告提交状态
            project.final_report_submitted = True
            project.save()

            return redirect('my_projects')  # Redirect to a success page

    context = {
        'form': form,
        'project': project
    }
    return render(request, 'submit_final_report.html', context)


def view_final_report(request, project_name):
    final_report = get_object_or_404(ProjectFinalReport, project_name=project_name)
    context = {
        'final_report': final_report
    }
    return render(request, 'view_final_report.html', context)


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')
        user_id = request.POST.get('userID')

        # 检查两次输入的密码是否一致
        if password != repeat_password:
            return render(request, 'register.html', {
                'error': '两次输入的密码不一致，请重新输入。'
            })

        # 检查用户名是否已经存在
        if not get_user_model().objects.filter(username=username).exists():
            user = get_user_model().objects.create(
                username=username,
                password=make_password(password),
                userID=user_id
            )
            user.save()
            return redirect('login2')  # Assuming you have a 'login' view to redirect to
        else:
            return render(request, 'register.html', {
                'error': '用户名已存在'
            })

    return render(request, 'register.html')


def delete_user(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    user.delete()
    return redirect('index3')  # 重定向到用户列表页面


def pending_projects1(request):
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        action = request.POST.get('action')

        project = get_object_or_404(CourseIdeologyProjects, projectName=project_name)
        if action == 'approve':
            project.projectStatus = 'approved'
        elif action == 'reject':
            project.projectStatus = 'rejected'
        project.save()

        # Redirect to avoid re-posting if the user refreshes the page
        return redirect('pending_projects1')

        # Fetch projects that are still pending approval
    projects = CourseIdeologyProjects.objects.filter(projectStatus='pending')
    return render(request, 'pending_projects1.html', {'projects': projects})


def submit_feedback(request, project_name):
    if request.method == 'POST':
        feedback = request.POST.get('feedback', '')
        project = get_object_or_404(CourseIdeologyProjects, projectName=project_name)
        project.feedback = feedback
        project.save()
        return redirect('pending_projects1')
    else:
        return redirect('pending_projects1')


def pending_projects2(request):
    if request.method == "POST":
        project_name = request.POST.get('project_name')
        action = request.POST.get('action')

        midterm_review = get_object_or_404(MidTermReview, project_name=project_name)
        if action == 'approve':
            midterm_review.midterm_review_Status = 'approved'
            messages.success(request, '中期报告已批准。')
        elif action == 'reject':
            midterm_review.midterm_review_Status = 'rejected'
            messages.error(request, '中期报告已拒绝。')
        midterm_review.save()
        return redirect('pending_projects2')

        # 获取所有已批准的项目
    approved_projects = CourseIdeologyProjects.objects.filter(projectStatus='approved')

    project_details = []
    for project in approved_projects:
        # 尝试获取与项目关联的中期报告，无论其状态如何
        try:
            midterm_review = MidTermReview.objects.get(project_name=project.projectName)
            # 只添加那些中期报告状态为'pending'的项目
            if midterm_review.midterm_review_Status == 'pending':
                project_details.append({
                    'project': project,
                    'midterm_review': midterm_review
                })
        except MidTermReview.DoesNotExist:
            # 如果中期报告不存在，表明中期报告未提交，也添加到列表中
            project_details.append({
                'project': project,
                'midterm_review': None  # 表明没有中期报告提交
            })
    return render(request, 'pending_projects2.html', {'project_details': project_details})


def submit_review(request, project_name):
    if request.method == 'POST':
        review_comments = request.POST.get('review_comments')
        midterm_review = get_object_or_404(MidTermReview, project_name=project_name)
        midterm_review.review_comments = review_comments
        midterm_review.save()
        messages.success(request, '评论已成功添加。')
        return redirect('pending_projects2')
    else:
        messages.error(request, '无效的请求。')
        return redirect('pending_projects2')


def pending_projects3(request):
    # 获取所有项目状态为 'approved' 的项目
    projects = CourseIdeologyProjects.objects.filter(projectStatus='approved')

    # 准备数据列表
    project_details = []

    # 遍历项目
    for project in projects:
        # 初始化字典以存放项目信息及其相关审核状态
        project_info = {
            'project': project,
            'midterm_review': None,
            'final_report': None
        }

        # 尝试获取对应的中期报告
        try:
            midterm_review = MidTermReview.objects.get(project_name=project.projectName)
            project_info['midterm_review'] = midterm_review
            # 只处理中期报告状态为 'approved' 的项目
            if midterm_review.midterm_review_Status != 'approved':
                continue
        except MidTermReview.DoesNotExist:
            # 如果中期报告不存在，可以选择继续显示该项目或直接跳过
            continue

        # 尝试获取对应的结项报告，仅当中期报告已批准时
        if project_info['midterm_review'] and project_info['midterm_review'].midterm_review_Status == 'approved':
            try:
                final_report = ProjectFinalReport.objects.get(project_name=project.projectName)
                # 仅将结项报告状态为 'pending' 的项目添加到列表
                if final_report.final_report_Status == 'pending':
                    project_info['final_report'] = final_report
                else:
                    # 如果结项报告已经被处理（批准或拒绝），则不添加到列表
                    continue
            except ProjectFinalReport.DoesNotExist:
                # 结项报告不存在，项目信息中已标记为 None
                pass

        # 将准备好的项目信息添加到列表中
        project_details.append(project_info)

    return render(request, 'pending_projects3.html', {'project_details': project_details})


def update_final_report_comments(request, project_name):
    # 从POST请求中获取审核意见文本
    comments = request.POST.get('final_report_comments', '')

    # 获取对应的结项报告对象
    final_report = get_object_or_404(ProjectFinalReport, project_name=project_name)

    # 更新审核意见字段
    final_report.final_report_comments = comments
    final_report.save()  # 保存更改

    # 添加一条成功消息，将在页面上显示为反馈
    messages.success(request, '审核意见已更新成功！')

    # 重定向回原页面，或到其他页面
    return redirect('pending_projects3')  # 确保替换 'some_view_name' 为实际的视图名或适当的URL


def update_final_report_status(request, project_name):
    if request.method == 'POST':
        action = request.POST.get('action', None)
        final_report = get_object_or_404(ProjectFinalReport, project_name=project_name)

        if action == 'approve':
            final_report.final_report_Status = 'approved'
            messages.success(request, '结项报告已批准。')
        elif action == 'reject':
            final_report.final_report_Status = 'rejected'
            messages.error(request, '结项报告已拒绝。')

        final_report.save()
        return redirect('pending_projects3')  # 重定向到列表页

    # 如果不是POST请求，或没有'action'，重定向回列表页
    return redirect('pending_projects3')


def funding_application_view(request):
    # 假设当前用户的相关项目（用户可以是项目的申请人或负责人）
    user_projects = CourseIdeologyProjects.objects.filter(leader=request.user)
    if request.method == 'POST':
        # 这里处理表单提交
        project_name = request.POST.get('project_name')
        project = CourseIdeologyProjects.objects.get(projectName=project_name)
        project.application_submitted = True  # 标记申请已提交
        project.save()
        # 获取表单数据
        project_name = request.POST.get('project_name')
        project_person = request.POST.get('project_person')
        requested_funding = request.POST.get('requested_funding')
        funding_purpose = request.POST.get('funding_purpose')
        contact_info = request.POST.get('contact_info')
        application_date = date.today()

        # 确认项目是否存在，并确保该项目属于当前用户
        project = get_object_or_404(CourseIdeologyProjects, projectName=project_name)

        # 创建并保存新的资金报告
        funding_report = MoneyReport.objects.create(
            project_name=project_name,
            projectPerson=project_person,
            requested_funding=requested_funding,
            funding_purpose=funding_purpose,
            contact_info=contact_info,
            application_date=application_date
        )

        # 保存申请记录
        funding_report.save()

        messages.success(request, f"经费申请已成功提交！")

        # 重定向到申请表单的页面或其他合适的页面
        return redirect('funding_application')
    else:
        # 查询并显示用户相关的所有项目
        projects = CourseIdeologyProjects.objects.filter(leader=request.user)
        projects_with_reports = []
        for project in projects:
            reports = MoneyReport.objects.filter(project_name=project.projectName)
            projects_with_reports.append({
                'project': project,
                'reports': reports,
            })
        return render(request, 'funding_application.html', {'projects_with_reports': projects_with_reports})


def pending_projects0(request):
    if request.method == 'POST':
        # Handle form submission
        report_id = request.POST.get('report_id')
        action = request.POST.get('action')
        report = get_object_or_404(MoneyReport, id=report_id)

        if action == "approve":
            report.money_report_Status = 'approved'
            report.save()
            messages.success(request, "经费申请已批准。")
        elif action == "reject":
            report.money_report_Status = 'rejected'
            report.save()
            messages.error(request, "经费申请已被拒绝。")
        else:
            messages.error(request, "未知操作。")
        return redirect('pending_projects0')  # Redirect to the same page to display the updated list

    # For GET requests, or after handling POST
    money_reports = MoneyReport.objects.filter(money_report_Status='pending')
    return render(request, 'pending_projects0.html', {'money_reports': money_reports})


def submit_results(request):
    # 获取所有审批通过的项目，同时确保关联的中期和结项报告也已经被批准
    approved_projects = CourseIdeologyProjects.objects.filter(
        projectStatus='approved',  # 项目申请状态也是审批通过
        midterm_reviews__midterm_review_Status='approved',  # 关联的中期报告被审批通过
        final_reports__final_report_Status='approved'  # 关联的结项报告也被审批通过
    ).distinct()  # 使用 distinct() 避免因多个中期或结项报告而出现重复的项目

    if request.method == 'POST':
        form = ProjectResultsForm(request.POST, request.FILES, projects=approved_projects)
        if form.is_valid():
            project_name = form.cleaned_data['project_name']
            results_file = form.cleaned_data['results_file']
            # 保存结果文件到项目
            project = CourseIdeologyProjects.objects.get(projectName=project_name)
            project.results = results_file
            project.save()
            return redirect('submit_results')  # 重定向到成功页面
    else:
        # 如果GET请求，则创建表单实例，传入已审批的项目
        form = ProjectResultsForm(projects=approved_projects)

    return render(request, 'submit_results.html', {'form': form, 'projects': approved_projects})
