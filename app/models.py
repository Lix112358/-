from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model


class CourseIdeologyProjects(models.Model):
    """课程思政项目表"""
    # 项目状态
    STATUS_CHOICES = [
        ('planning', '规划中'),
        ('ongoing', '进行中'),
        ('completed', '已完成'),
    ]
    # 项目申请状态
    STATUS = [
        ('pending', '待审批'),
        ('approved', '审批通过'),
        ('rejected', '审批不通过'),
    ]
    projectPerson = models.CharField(max_length=10, null=True)  # 项目的申请人
    projectName = models.CharField(max_length=255, primary_key=True)  # 项目名称
    description = models.TextField(max_length=255)  # 项目描述
    designation = models.TextField(max_length=255, null=True)  # 项目设计
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)  # 项目状态（规划中、进行中、已完成）
    projectStatus = models.CharField(max_length=10, choices=STATUS, default='pending')  # 项目申请状态
    startDate = models.DateField()  # 项目开始日期
    endDate = models.DateField()  # 项目结束日期
    results = models.FileField(upload_to='project_videos/', blank=True, null=True, verbose_name="项目视频")  # 项目的成果
    feedback = models.TextField(blank=True, null=True)  # 项目反馈和监督意见
    midterm_report_submitted = models.BooleanField(default=False, verbose_name="中期报告已提交")  # 中期报告提交状态
    final_report_submitted = models.BooleanField(default=False, verbose_name="结项报告已提交")  # 结项报告提交状态
    application_submitted = models.BooleanField(default=False, verbose_name="申请已提交") # 经费申请提交状态
    # 项目负责人ID字段，与自定义用户模型关联
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='led_projects'
    )

    # 获取状态的显示名称
    def get_status_display(self):
        return dict(self.STATUS).get(self.projectStatus, "Unknown status")


class MidTermReview(models.Model):
    """
    中期检查信息表
    """
    STATUS = [
        ('pending', '待审批'),
        ('approved', '审批通过'),
        ('rejected', '审批不通过'),
    ]
    # 项目名称，设为主键
    project_name = models.CharField(max_length=255, primary_key=True, verbose_name='项目名称')
    # 已取得的成果
    achievements = models.TextField(verbose_name='已取得的成果')
    # 下一步的计划
    next_steps = models.TextField(verbose_name='下一步的计划')
    # 存在的问题
    issues = models.TextField(verbose_name='存在的问题')
    # 拟解决措施
    solutions = models.TextField(verbose_name='拟解决措施')
    # 中期检查审核意见
    review_comments = models.TextField(verbose_name='中期检查审核意见')
    # 中期报告状态
    midterm_review_Status = models.CharField(max_length=10, choices=STATUS, default='pending')

    project = models.ForeignKey(CourseIdeologyProjects, on_delete=models.CASCADE, related_name='midterm_reviews',null=True)

    class Meta:
        verbose_name = '中期检查信息'
        verbose_name_plural = '中期检查信息'

    def __str__(self):
        return self.project_name


class ProjectFinalReport(models.Model):
    """
    项目结项报告表
    """
    STATUS = [
        ('pending', '待审批'),
        ('approved', '审批通过'),
        ('rejected', '审批不通过'),
    ]
    # 项目名称，设为主键
    project_name = models.CharField(max_length=255, primary_key=True, verbose_name='项目名称')
    # 项目成果汇总
    results_summary = models.TextField(verbose_name='项目成果汇总')
    # 项目主要研究内容
    main_research_content = models.TextField(verbose_name='项目主要研究内容')
    # 项目的思政教育意义
    ideological_education_significance = models.TextField(verbose_name='项目的思政教育意义')
    # 结项报告审核意见
    final_report_comments = models.TextField(verbose_name='结项报告审核意见')
    # 结项报告状态
    final_report_Status = models.CharField(max_length=10, choices=STATUS, default='pending')

    project = models.ForeignKey(CourseIdeologyProjects, on_delete=models.CASCADE, related_name='final_reports',null=True)
    class Meta:
        verbose_name = '项目结项报告'
        verbose_name_plural = '项目结项报告'

    def __str__(self):
        return self.project_name


class CustomUser(AbstractUser):
    """用户表"""

    institution = models.CharField(max_length=255)  # 用户的学院
    userID = models.CharField(max_length=15)  # 用户的学号/工号


User = get_user_model()


class Announcement(models.Model):
    """通知表"""
    title = models.CharField(max_length=200)  # 通知的标题
    content = models.TextField()  # 通知的内容
    created_at = models.DateTimeField(auto_now_add=True)  # 通知发布的时间
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # 通知的发布者
    link = models.URLField(max_length=200, blank=True, null=True)  # 通知的链接，允许为空

    def __str__(self):
        return self.title


class MoneyReport(models.Model):
    """
    经费申请表
    """
    STATUS = [
        ('pending', '待审批'),
        ('approved', '审批通过'),
        ('rejected', '审批不通过'),
    ]
    project_name = models.CharField(max_length=255, verbose_name="项目名称")
    projectPerson = models.CharField(max_length=100, verbose_name="申请人")
    requested_funding = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="申请的经费")
    funding_purpose = models.TextField(verbose_name="经费主要用途")
    contact_info = models.CharField(max_length=100, verbose_name="申请人的联系方式")
    application_date = models.DateField(verbose_name="申请日期")
    money_report_Status= models.CharField(max_length=10, choices=STATUS, default='pending')

    def __str__(self):
        return f"{self.project_name} - {self.projectPerson}"

    class Meta:
        verbose_name = "项目报表"
        verbose_name_plural = "项目报表"
