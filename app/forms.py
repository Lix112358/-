from django import forms
from .models import CourseIdeologyProjects, Announcement, MidTermReview, ProjectFinalReport
from django.db import models


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=15)
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
    user_type = forms.ChoiceField(label='用户类型', choices=[('user', '普通用户'), ('admin', '管理员')],
                                  widget=forms.RadioSelect)


class ProjectApplicationForm(forms.ModelForm):
    class Meta:
        model = CourseIdeologyProjects
        fields = ['projectName', 'projectPerson', 'description', 'designation', 'startDate', 'endDate', 'status']
        labels = {
            'projectName': '项目名',
            'projectPerson': '申请人',
            'designation': '项目设计',
            'description': '项目描述',
            'startDate': '开始日期',
            'endDate': '结束日期',
            'status': '项目状态'
        }
        widgets = {
            'startDate': forms.DateInput(attrs={'type': 'date'}),
            'endDate': forms.DateInput(attrs={'type': 'date'})
        }


class MidTermReviewForm(forms.ModelForm):
    project = models.ForeignKey(CourseIdeologyProjects, on_delete=models.CASCADE, related_name='midterm_reviews')

    class Meta:
        model = MidTermReview
        fields = ['project_name', 'achievements', 'next_steps', 'issues', 'solutions']
        labels = {
            'project_name': '项目名称',
            'achievements': '已取得的成果',
            'next_steps': '下一步的计划',
            'issues': '存在的问题',
            'solutions': '拟解决措施',
        }
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'next_steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'solutions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ProjectFinalReportForm(forms.ModelForm):
    class Meta:
        model = ProjectFinalReport
        fields = ['results_summary', 'main_research_content', 'ideological_education_significance', ]
        labels = {
            'results_summary': '项目成果汇总',
            'main_research_content': '项目主要研究内容',
            'ideological_education_significance': '项目的思政教育意义',
        }
        widgets = {
            'results_summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'main_research_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ideological_education_significance': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'link']  # 包含链接字段，可以为空
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'link': forms.URLInput(attrs={'class': 'form-control'}),
        }


class ProjectResultsForm(forms.Form):
    project_name = forms.ChoiceField(choices=[])  # 初始化为空的选择字段
    results_file = forms.FileField()

    def __init__(self, *args, **kwargs):
        projects = kwargs.pop('projects', None)
        super(ProjectResultsForm, self).__init__(*args, **kwargs)
        if projects is not None:
            self.fields['project_name'].choices = [(project.projectName, project.projectName) for project in projects]
