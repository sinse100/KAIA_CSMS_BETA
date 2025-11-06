from django.contrib import admin
from .models import *
# Register your models here.

## (메모) django 관리자 페이지에서 사용자 프로필을 마음대로 접근하기 위한 코드
admin.site.register(kaia_user_profile)

admin.site.register(kaia_eval_result)