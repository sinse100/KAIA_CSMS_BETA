import os
import asyncio
import boto3
from datetime import datetime, timedelta

AWS_ACCESS_KEY_ID = "[**REDACTED**]"
AWS_SECRET_ACCESS_KEY = "[**REDACTED**]"
AWS_REGION = "[**REDACTED**]"
AWS_STORAGE_BUCKET_NAME =  "[**REDACTED**]"



TARGET_PATH = 'eval_state/'

LOCAL_PATH1 = 'test_zip/completed/'
LOCAL_PATH2 = 'test_zip/pending/'


def workhorse_upload_test_file(s3_client,local_path,target_path,files_list):
    for file in files_list:
        local_file = local_path + file
        created_time  = (datetime.now() + timedelta(seconds=10)).strftime("%Y%m%d%H%M%S")
        checklist_hash = '087fb30d2a9725e02fdc77761c01f7c1'
        username = "sinse100" 
        oem= "Hyundai"
        original_name = file
        target_file = TARGET_PATH+username+'_'+created_time +'.zip'
        state = ""
        if local_path == LOCAL_PATH1:
            state = "done"
        if local_path == LOCAL_PATH2:
            state="pend"

        s3_client.upload_file(local_file, 
                          AWS_STORAGE_BUCKET_NAME, 
                          target_file,
                          ExtraArgs={
                            'Metadata': {
                                'checklist_hash': checklist_hash,
                                'created_time' : created_time, 
                                'original_name' :original_name,                            
                                'username' : username,
                                'oem' :oem,
                                'state' : state
                                },          # 사용자 정의 메타데이터
                            'ContentType': 'application/zip'      # 파일의 MIME 타입 지정 (선택)
                        })


def upload_test_file():
    s3_client = boto3.client('s3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    completed_file_list = [f for f in os.listdir(LOCAL_PATH1) if os.path.isfile(os.path.join(LOCAL_PATH1, f))]

    pending_file_list = [f for f in os.listdir(LOCAL_PATH2) if os.path.isfile(os.path.join(LOCAL_PATH2, f))]
    
    asyncio.run(main(completed_file_list,pending_file_list, s3_client,LOCAL_PATH1,LOCAL_PATH2, TARGET_PATH ))


async def task2(s3_client,local_path2,target_path,pending_file_list):
    workhorse_upload_test_file(s3_client,local_path2,target_path,pending_file_list)

async def task1(s3_client,local_path1,target_path,completed_file_list):
    workhorse_upload_test_file(s3_client,local_path1,target_path,completed_file_list)

async def main(completed_file_list,pending_file_list, s3_client,local_path1,local_path2, target_path ):
    await task1(s3_client,local_path1,target_path,completed_file_list)
    await task2(s3_client,local_path2,target_path,pending_file_list)


upload_test_file()

## S3로 바로 업로드하는 함수


## S3 버킷에서 복사 이동하는 함수




    