from django.db import models
from django.contrib.auth.models import User

# Create your models here.

## (메모) models.py : DB 테이블 및 기타 유틸 함수를 정의

## (메모) 시용자 프로필 테이블
class kaia_user_profile(models.Model):            

    ## (메모) 사용자 프로필 사진 경로 가져오기
    def get_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join('imgs/users', filename)
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)     ## (메모) User 모델에 대한 외래키
    mb_hp = models.CharField(max_length=20, null=True, unique=True) ## (메모) 회원 전화번호
    mb_name = models.CharField(max_length=20, null=True)            ## (메모) 회원 이름
    ##mb_img = models.ImageField(upload_to=get_file_path, default='imgs/default_user.png')
    mb_type = models.CharField(max_length=3, null=True)

    def save(self, *args, **kwargs):                                               ## 닉네임 기본값 : 회원 ID 로 하여 저장
        super(kaia_user_profile, self).save(*args, **kwargs)


## kaia 평가 결과
class kaia_eval_result(models.Model):
    submission_id = models.CharField(max_length=255)  # 첫 번째 문자열 속성
    rationale = models.CharField(max_length=255)  # 두 번째 문자열 속성
    number = models.IntegerField()              # 숫자형 속성
    passfail = models.CharField(max_length=1)       # 1글자 문자형 속성
    category = models.CharField(max_length=255)
    evaluated_date= models.CharField(max_length=255)
    evaluator_email = models.CharField(max_length=255)


    def __str__(self):
        return f"(제출물 파일 : {self.submission_id}, 범주: {self.category}, 문항: {self.number}, 통과여부: {self.passfail}, 사유: {self.rationale}, 평가일자: {self.evaluated_date})"
    
