from django.shortcuts import render,redirect
from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse 
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from urllib.parse import quote
from datetime import datetime
from django.db import transaction
from collections import defaultdict

from django.contrib import auth
from django.conf import settings

import json
import re
import pandas as pd
import json
import boto3
from .utils import *
from .models import *

# Create your views here.

## (메모) views.py : 백엔드 코드 (실제 데이터 처리 및 기능 제공이 이뤄지는 곳) 정의 파일


## (메모) main : 홈페이지 백엔드
def main(request):
    return render(request, 'main_copy.html')

## (메모) signup : 회원가입 백엔드
def signup(request):
    if request.method == "POST":
        user_id = request.POST.get('username')               ## (메모) 회원 ID
        user_pw = request.POST.get('password')               ## (메모) 비밀번호
        user_pwCheck = request.POST.get('passwordCheck')     ## (메모) 비밀번호 확인
        user_name = request.POST.get('mb_name')              ## (메모) 회원 실명
        user_email=request.POST.get('mb_email')              ## (메모) 회원 이메일
        user_hp = request.POST.get('mb_hp')                  ## (메모) 회원 전화번호
        user_type = request.POST.get('mb_type')              ## (메모) 회원 유형

        ## 가입정보 유효성 확인 (예: 모든 필드가 입력되었는가?)
        validity = is_valid_info([user_id, user_pw, user_pwCheck, user_name, user_email, user_hp,user_type])

        ## (메모) 회원 가입 정보가 유효하지 않은 경우
        if not validity['status']:
            return render(request, 'signup.html', {'error':validity['msg']})
        ## (메모) 동일한 회원 ID가 존재하는 경우
        if User.objects.filter(username=user_id).exists():
            return render(request, 'signup.html', {'error':"이미 존재하는 아이디입니다."})
        ## (메모) 동일한 회원 Email이 존재하는 경우
        if User.objects.filter(email=user_email).exists():
            return render(request, 'signup.html', {'error':"이미 존재하는 아이디입니다."})
        ## (메모) 동일한 회원 전화번호가 존재하는 경우
        if kaia_user_profile.objects.filter(mb_hp = user_hp).exists():
            return render(request, 'signup.html', {'error': '이미 등록된 연락처입니다.'})
        if not is_email_vrfied(request)['status']:
            return render(request, 'signup.html', {'error': is_email_vrfied(request)['msg']})
        
        user = User.objects.create_user(username=user_id, password=user_pw,email=user_email)
        kaia_user=kaia_user_profile()
        kaia_user.user=user
        kaia_user.mb_hp=user_hp
        kaia_user.mb_name=user_name
        kaia_user.mb_type = user_type

        kaia_user.save()
        auth.login(request, user)
        return redirect('/')
    else:
        if '' in request.session:
            del request.session['email_verify']
        return render(request,'signup.html')
        
    return render(request,'signup.html')


## (메모) send_code : 인증번호 전송 관련 백엔드
@csrf_exempt
def send_code (request):
    print('here')
    if 'email_verify' in list(request.session.keys()):
        print('here send_code')
        del request.session['email_verify']
        request.session.save()
    if request.method=="POST":
        data = json.loads(request.body)
        mb_hp = data['mb_email']
        random_code = random_code_generator()
        request.session['email_verify'] = {}
        request.session['email_verify']['email_code'] = random_code 
        request.session['email_verify']['expire'] = set_expire()
        request.session['email_verify']['is_vrfd'] = False
        request.session.save()

        template_body = f'[From WEB 발신] 인증코드는 {random_code} 입니다.'
        template_title = f'[중요] 인증코드 발송'
        email = EmailMessage(template_title, template_body, to=[mb_hp])
        email.send()
        return JsonResponse({'message' : '인증번호가 발송되었습니다'}, status=200)


## (메모) verify_code : 인증번호 확인 관련 백엔드
@csrf_exempt
def verify_code (request):
    if request.method=="POST":
        print(request.session['email_verify'])
        if 'email_verify' in list(request.session.keys()):
            vrfy_info = request.session['email_verify']
            data = json.loads(request.body)
            code = data['mb_code']
            expire = vrfy_info['expire']

            if code != vrfy_info['email_code']:
                return JsonResponse  ({'message' : '인증번호 틀립니다'}, status=500)
            if is_expired(expire):
                return JsonResponse  ({'message' : '인증번호가 만료되었습니다'}, status=500) 
            request.session['email_verify']['is_vrfd'] = True
            request.session.save()
            return JsonResponse({'message' : '인증 성공'}, status=200)
        return JsonResponse({'message' : '먼저 인증을 해주십시오.'}, status=500)
    return JsonResponse({'message' : 'Only POST Allowed'}, status=405)


## (메모) login : 로그인 기능 관련 백엔드
def login(request):
    if request.method == "POST":
        username = request.POST['username']      
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            remember_session = request.POST.get('remember_session') ## (메모) remember_session : 로그인 유지 버튼 활성화 여부 
            if remember_session:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False    ## (메모) 활성화된 경우 : 브라우저 창 닫혀도 세션 유지 
            else:
                request.session.set_expiry(0)                       ## (메모) 비활성화된 경우 : 브라우저 창 닫히면 바로 세션 종료 
                request.session.modified = True
            return redirect('/') 
        else:
            return render(request, 'login.html',{'error':"사용자 이름 혹은 패스워드가 일치하지 않습니다."})
    return render(request,'login.html')
    

## (메모) logout : 로그아웃 관련 백엔드
@login_required
def logout(request):
    auth.logout(request)              ## (메모) 세션 삭제 
    return redirect('/')              ## (메모) 메인 페이지로 리다이렉트


## (메모) about : 소개 페이지 백엔드
def about(request):
    return HttpResponse("This page is about.")

'''
    path('oem_list_eval/', views.oem_list_eval, name="oem_list_eval"),
    path('oem_submit_eval/', views.oem_submit_eval, name="oem_submit_eval"),
'''


## (메모)  : 평가항목 페이지 제출 백엔드
@login_required
def oem_submit_eval(request):
    ## S3 버킷 접근 코드
    table_data, columns = get_current_checklist(settings.S3_CLIENT)
    
    ## 병합셀 있는 버전 (추후 시간 남으면 구현)
    ##df, merge_data = read_excel_with_merge(excel_file)

    ## 병합셀 없는 버전
    request.session['current_checklist'] = get_Etag(settings.S3_CLIENT,'current_eval_list/checklist.xlsx')
    print(request.session['current_checklist'])
    request.session.save()

    return render(request, 'oem_submit_eval_copy.html', {"table_data": table_data, "columns": columns})


    
@login_required
@csrf_exempt
def oem_submit_evidence(request):
    if request.method == 'POST':
        zip_file = request.FILES.get('zip_file')
        print(zip_file.name)
        if not zip_file:
            return JsonResponse({"status": "error", "message": "파일이 업로드되지 않았습니다."}, status=400)
        try:
            print(zip_file)
            upload_submission_file(settings.S3_CLIENT,request.user.username,zip_file,request.session['current_checklist'])
            request.session['current_checklist'] = ""
            return JsonResponse({"status": "success", "message": "파일이 성공적으로 업로드되었습니다."}, status=200)
        except Exception as e:
            print(f'파일 업로드 중 오류 발생: {str(e)}')
            return JsonResponse({"status": "error", "message": "파일 업로드 중 오류가 발생했습니다."}, status=500)
    else:
        return alert_and_redirect( '잘못된 접근 방식입니다.', request.META.get('HTTP_REFERER', '/'))

    '''
    if request.method == 'POST':
        zip_file = request.FILES.get('zip_file')
        print(zip_file.name)
        if not zip_file:
            return alert_and_redirect( 'ZIP 파일을 업로드해주세요.', request.META.get('HTTP_REFERER', '/'))
        try:
            upload_submission_file(settings.S3_CLIENT,request.user.username,zip_file,request.session['current_checklist'])
            return alert_and_redirect("평가 신청이 성공적으로 완료되었습니다.", '/')
        except Exception as e:
            return alert_and_redirect( f'파일 업로드 중 오류 발생: {str(e)}', request.META.get('HTTP_REFERER', '/'))
    else:
        return alert_and_redirect( '잘못된 접근 방식입니다.', request.META.get('HTTP_REFERER', '/'))
    '''

 ## name &#x27;request&#x27; is not defined

@login_required
def oem_list_eval(request):
    ## 사용자 id 폴더에 있는 파일 몇개인지 전부 확인
    try:
        files_metadata = search_user_files(settings.S3_CLIENT, request.user.username)
        files_metadata = sorted(files_metadata, key=lambda x: x['created_time'],reverse=True)
        
        for d in files_metadata:
            d["created_time"] = datetime.datetime.strptime(d["created_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        
        current_page_number = request.GET.get('page')
        if not(current_page_number is None):
            current_page_number = int(current_page_number )
        else:
            current_page_number = 1    

        paination_obj = get_paginater(current_page_number,files_metadata)
        return render(request, 'oem_list_eval.html',paination_obj)

    except Exception as e:
        return alert_and_redirect(f'파일 조회 중 오류 발생: {str(e)}', request.META.get('HTTP_REFERER', '/'))


@login_required
def evl_list_eval(request):
    if request.user.kaia_user_profile.mb_type != 'EVL':
        return alert_and_redirect(f'평가 내역은 평가자만이 조회 가능합니다', request.META.get('HTTP_REFERER', '/'))
        
    try:
        files_metadata = search_all_files(settings.S3_CLIENT)
        files_metadata = sorted(files_metadata, key=lambda x: x['created_time'],reverse=True)
        
        for d in files_metadata:
            d["created_time"] = datetime.datetime.strptime(d["created_time"], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        
        current_page_number = request.GET.get('page')
        if not(current_page_number is None):
            current_page_number = int(current_page_number )
        else:
            current_page_number = 1    

        paination_obj = get_paginater(current_page_number,files_metadata)
        print(paination_obj['page_data'])
        return render(request, 'evl_list_eval.html',paination_obj)

    except Exception as e:
        return alert_and_redirect(f'파일 조회 중 오류 발생: {str(e)}', request.META.get('HTTP_REFERER', '/'))
 

@login_required
def checklist_evaluate(request):
    if request.user.kaia_user_profile.mb_type != 'EVL':
        alert_and_redirect(f'평가는 평가자만이 수행 가능합니다', request.META.get('HTTP_REFERER', '/'))
    
    file_key = request.GET.get('submit')

    ## 평가 대상이 되는 증거 파일이 있는지 확인
    if not has_such_file_with_key(settings.S3_CLIENT, file_key):
        return alert_and_redirect(f'그런 파일은 존재하지 않습니다', request.META.get('HTTP_REFERER', '/'))
    
    if kaia_eval_result.objects.filter(submission_id=file_key).exists():
        return JsonResponse({"status": "error", "message": "이미 누군가에 의해 평가가 완료된 파일입니다."}, status=500)
    
    ## 현재 버전에 대한 증거 파일인지 확인
    submission_checklist_Etag = get_file_metadata(settings.S3_CLIENT,file_key,"checklist_hash")
    checklist_etag = get_Etag(settings.S3_CLIENT,'current_eval_list/checklist.xlsx')

    if submission_checklist_Etag != checklist_etag:
        return alert_and_redirect('구버전의 평가항목을 사용한 파일입니다',request.META.get('HTTP_REFERER', '/'))

    ## 증거 파일에 대한 다운로드 링크와 현재 버전의 평가항목 표 데이터 로드
    download_link = get_download_link(settings.S3_CLIENT,file_key)
    table_data, columns =  get_current_checklist(settings.S3_CLIENT)
    columns = columns + ['평가 결과', '평가 사유']
    original_name=get_file_metadata(settings.S3_CLIENT,file_key,"original_name")

    context = {
        'table_data': table_data, 
        'columns': columns, 
        'download_link': download_link,
        'original_name': original_name,
        'file_key' : file_key
    }
    return render (request, 'checklist_evaluate_copy.html', context)



@login_required
@csrf_exempt
def eval_result_submit(request):
    if request.user.kaia_user_profile.mb_type != 'EVL':
        return JsonResponse({"status": "error", "message": "평가자만이 평가 가능합니다."}, status=500)

    if request.method == 'GET':
        return JsonResponse({"status": "error", "message": "잘못된 접근입니다."}, status=500)
    
    file_key = request.POST.get('file_key')    

    if kaia_eval_result.objects.filter(submission_id=file_key).exists():
        return JsonResponse({"status": "error", "message": "이미 누군가에 의해 평가가 완료된 파일입니다."}, status=500)
   
    eval_results= [] 
    key_count = 0

    grouped_data = defaultdict(dict)

        # 정규표현식으로 접두사와 나머지 부분 분리
    pattern = r'(result\d+)\[(.*?)\]'
    for key, value in request.POST.items():
        match = re.fullmatch(pattern, key)
        if match:
            prefix = match.group(1)  # result와 번호 (예: result1, result2)
            sub_key = match.group(2)  # 대괄호 안의 키 (예: aaa, bbb, gggg)
    
            grouped_data[prefix][sub_key] = value

    for prefix, group in grouped_data.items():
        eval_result = kaia_eval_result()

        eval_result.number = int(group['number'])
        eval_result.category = group['category']
        eval_result.passfail = group['passfail']
        eval_result.rationale = group['rationale']
        eval_result.evaluated_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        print('1')
        eval_result.submission_id = file_key
        eval_result.evaluator_email = request.user.email

        eval_results.append(eval_result)

    try:
        with transaction.atomic():
            print('2')
            modify_submission_metadata(settings.S3_CLIENT,file_key,'state','done')
            print('3')
            kaia_eval_result.objects.bulk_create(eval_results)
        return JsonResponse({"status": "success", "message": "평가 결과 제출 완료"}, status=200)
    except Exception as e:
        modify_submission_metadata(settings.S3_CLIENT,file_key,'state','pend')
        return JsonResponse({"status": "error", "message": "평가 결과 제출 도중 오류 발생"}, status=500)

        ##print(f"{prefix}: {group}")

    '''
    if request.user.kaia_user_profile.mb_type != 'EVL':
        return alert_and_redirect(f'평가는 평가자만이 수행 가능합니다', request.META.get('HTTP_REFERER', '/'))

    if request.method == 'GET':
        return alert_and_redirect(f'잘못된 접근입니다.', request.META.get('HTTP_REFERER', '/'))

    file_key = request.POST.get('file_key')    
    eval_results= [] 
    key_count = 0

    grouped_data = defaultdict(dict)

        # 정규표현식으로 접두사와 나머지 부분 분리
    pattern = r'(result\d+)\[(.*?)\]'
    for key, value in request.POST.items():
        match = re.fullmatch(pattern, key)
        if match:
            prefix = match.group(1)  # result와 번호 (예: result1, result2)
            sub_key = match.group(2)  # 대괄호 안의 키 (예: aaa, bbb, gggg)
            print(prefix)
            grouped_data[prefix][sub_key] = value

    for prefix, group in grouped_data.items():
        eval_result = kaia_eval_result()

        eval_result.number = int(group['number'])
        eval_result.category = group['category']
        eval_result.passfail = group['passfail']
        eval_result.rationale = group['rationale']
        eval_result.submission_id = file_key

        eval_results.append(eval_result)

    try:
        with transaction.atomic():
            modify_submission_metadata(settings.S3_CLIENT,file_key,'state','done')
            kaia_eval_result.objects.bulk_create(eval_results)
        return alert_and_redirect( '평가 결과 제출 완료',  '/')
    except Exception as e:
        modify_submission_metadata(settings.S3_CLIENT,file_key,'state','pend')
        return alert_and_redirect(f'평가 결과 제출 중 오류 발생: {str(e)}', request.META.get('HTTP_REFERER', '/'))

        ##print(f"{prefix}: {group}")
    
    return alert_and_redirect( '평가 결과 제출 완료',  '/')
'''

@login_required
def show_eval_result(request):
    file_key = request.GET.get('submit')
    
    ## DB 검색
    queryset=kaia_eval_result.objects.filter(submission_id=file_key)
    result_list = list(queryset.values())
    ##print(eval_results)

    ## 범주의 리스트
    category = list(set(item["category"] for item in result_list))

    ##항목별 달성률
    completion_ratio = get_completion_ratio(result_list)

    evaluation_date = list(set(item["evaluated_date"] for item in result_list))[0]
    evaluation_date = datetime.datetime.strptime(evaluation_date, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

    evaluator_email = list(set(item["evaluator_email"] for item in result_list))[0]

    created_time = get_file_metadata(settings.S3_CLIENT,file_key,"created_time")
    created_time = datetime.datetime.strptime(created_time, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")



    table_data, columns = get_current_checklist(settings.S3_CLIENT)
    columns = columns + ['평가 결과', '평가 사유']

    ##print(table_data)

    for key in completion_ratio:
        completion_ratio[key] = round(completion_ratio[key] * 100, 1)

    
    # 딕셔너리를 합칠 리스트 초기화
    merged_list = []

    # list1을 기준으로 병합 수행
    for item1 in table_data:
        for item2 in result_list:
            # '항목'과 'num' 키의 값이 같을 경우
            if item1["번호"] == item2["number"]:
                # 두 딕셔너리를 병합
                merged_dict = {**item1, **item2}
                merged_list.append(merged_dict)
    
    print(merged_list)

    ## 범주
    context = {
        'category' : category,                       
        'completion_ratio' : json.dumps(completion_ratio),
        'result_list' : merged_list,
        'evaluation_date' : evaluation_date,
        'evaluator_email': evaluator_email,
        'created_date' : created_time,
        'table_data' : table_data,
        "columns" : columns
    }
    return render(request,'show_eval_result.html',context)


'''

{
    '정보보호 관리체계': {'P_ratio': 0.7916666666666666, 'F_ratio': 0.20833333333333334}, 
    '사이버보안 위험관리': {'P_ratio': 0.5454545454545454, 'F_ratio': 0.45454545454545453}, 
    '사이버보안 엔지니어링': {'P_ratio': 0.8125, 'F_ratio': 0.1875}}
'''




'''

[{'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120448.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=3d0d018aed8cee4031897d849b0e527b13d724b5c1286a850d7e21ba06f57ded', 'created_time': '2024-12-05 12:04:48', 'filename': 'sinse100_20241205120448.zip', 'original_name': '평가제출물_6.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120448.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120439.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=41dcca72dbb0b3cbfc6ebce090512be6b28844590af9af42aea22ea8042feff3', 'created_time': '2024-12-05 12:04:39', 'filename': 'sinse100_20241205120439.zip', 'original_name': '평가제출물_5.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120439.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120425.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=cba224472e82f0129f84819729d173d1198b875381ccc58116f3b01601eb6f32', 'created_time': '2024-12-05 12:04:25', 'filename': 'sinse100_20241205120425.zip', 'original_name': '평가제출물_2.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120425.zip', 'state': 'done'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120346.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=608dfc6642208e31a28931c14d3950fcd5a89da1d67b89e8b88d190e9e61ee01', 'created_time': '2024-12-05 12:03:46', 'filename': 'sinse100_20241205120346.zip', 'original_name': '평가제출물_6.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120346.zip', 'state': 'done'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120306.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=aaa6ccc9e3a40b997bdc165204fd6ae5e0be21cc5f03245bd6aa4a3d505cbcec', 'created_time': '2024-12-05 12:03:06', 'filename': 'sinse100_20241205120306.zip', 'original_name': '평가제출물_5.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120306.zip', 'state': 'done'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205120146.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=458bb41d38bab6799e6e7d52deec50df9762b9812d005b296ce9d4543d5aac38', 'created_time': '2024-12-05 12:01:46', 'filename': 'sinse100_20241205120146.zip', 'original_name': '평가제출물_3.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205120146.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205115159.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034035Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=2daad1d3ae7be2425f1eea48cb2bbb5087238ffc38233bf46dd073db270fa53e', 'created_time': '2024-12-05 11:51:59', 'filename': 'sinse100_20241205115159.zip', 'original_name': '평가제출물_6.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205115159.zip', 'state': 'done'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205115149.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=78b55125bec57d5c3e1824f9c89b1a91fb91b2ee4b6e8685c63932f2680f9893', 'created_time': '2024-12-05 11:51:49', 'filename': 'sinse100_20241205115149.zip', 'original_name': '평가제출물_2.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205115149.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205114942.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=39f6ec5cf3707a348f2ec83a81c642ae1d566c36b92a96ec7ad814abff26b230', 'created_time': '2024-12-05 11:49:42', 'filename': 'sinse100_20241205114942.zip', 'original_name': '평가제출물_3.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205114942.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205114933.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e7d4f19442a7b4d756fe1ee5993562db515493f8ecf6d8732a64ee9fa68ccd43', 'created_time': '2024-12-05 11:49:33', 'filename': 'sinse100_20241205114933.zip', 'original_name': '평가제출물_2.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205114933.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205113538.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=89e570a39e0ab25797820daac19d5f023750203efb0bb6ecf29768044a356209', 'created_time': '2024-12-05 11:35:38', 'filename': 'sinse100_20241205113538.zip', 'original_name': '평가제출물_2.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205113538.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205113223.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=b9a4783524d079d71341c233d3e7433c4301a1d8544493d79186eabe074fef20', 'created_time': '2024-12-05 11:32:23', 'filename': 'sinse100_20241205113223.zip', 'original_name': '평가제출물_3.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205113223.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205113127.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e05f98bf7bc75eb1057093f64910a1d88624d6234a2a1f96f2555685285e7991', 'created_time': '2024-12-05 11:31:27', 'filename': 'sinse100_20241205113127.zip', 'original_name': '평가제출물_6.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205113127.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205113013.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=da7739162c7c67b8ed60eda67bc0cc6f9af40c1a8ab1f733bc0c0f21abc6a34b', 'created_time': '2024-12-05 11:30:13', 'filename': 'sinse100_20241205113013.zip', 'original_name': '평가제출물_4.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205113013.zip', 'state': 'pend'}, {'download_url': 'https://kaiaapp.s3.amazonaws.com/eval_state/sinse100_20241205111427.zip?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAULJHDEA3DB2AUIW7%2F20241205%2Fap-northeast-2%2Fs3%2Faws4_request&X-Amz-Date=20241205T034034Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=e82022db8d33bf2c32c9c8bf866ea968885996fa1e51b50021578503eec11358', 'created_time': '2024-12-05 11:14:27', 'filename': 'sinse100_20241205111427.zip', 'original_name': '평가제출물_3.zip', 'username': 'sinse100', 'oem': 'Hyundai', 'key': 'eval_state/sinse100_20241205111427.zip', 'state': 'pend'}]

[
{
    'id': 154, 
    'submission_id': 'eval_state/sinse100_20241205120425.zip', 
    'rationale': 'asd', 
    'number': 1, 
    'passfail': 'P', 
    'category': '정보보호 관리체계'
}, 

{'id': 155, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 2, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 156, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 3, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 157, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 4, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 158, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 5, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 159, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 6, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 160, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 7, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 161, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 8, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 162, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 9, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 163, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 10, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 164, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 11, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 165, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 12, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 166, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 13, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 167, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 14, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 168, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 15, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 169, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 16, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 170, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 17, 'passfail': 'P', 'category': ' 정보보호 관리체계'}, {'id': 171, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 18, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 172, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 19, 'passfail': 'P', 'category': '정보보호 관리체 계'}, {'id': 173, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 20, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 174, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 21, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 175, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 22, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 176, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 23, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 177, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 24, 'passfail': 'P', 'category': '정보보호 관리체계'}, {'id': 178, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 25, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 179, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 26, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 180, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 27, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 181, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 28, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 182, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 29, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 183, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 30, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 184, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 31, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 185, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 32, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 186, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 33, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 187, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 34, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 188, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 35, 'passfail': 'P', 'category': '사이버보안 위험관리'}, {'id': 189, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 36, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 190, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 37, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 191, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 38, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 192, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 39, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 193, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 40, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 194, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 41, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 195, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 42, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 196, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 43, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 197, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 44, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 198, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 45, 'passfail': 'P', 'category': ' 사이버보안 엔지니어링'}, {'id': 199, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 46, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 200, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 47, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 201, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 48, 'passfail': 'P', 'category': '사이버보안  엔지니어링'}, {'id': 202, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 49, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 203, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 50, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}, {'id': 204, 'submission_id': 'eval_state/sinse100_20241205120425.zip', 'rationale': 'asd', 'number': 51, 'passfail': 'P', 'category': '사이버보안 엔지니어링'}]


'''



'''

시간나면 반영
-> 파일 제출 로딩창 (o)
-> 파일 정보를 별도의 DB로 저장
-> 평가항목 수정
-> 홈 화면 

'''
