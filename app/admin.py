from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# 注册你的模型
admin.site.register(CustomUser, UserAdmin)


