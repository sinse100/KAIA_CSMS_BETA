import boto3

AWS_ACCESS_KEY_ID = "[**REDACTED**]"
AWS_SECRET_ACCESS_KEY = "[**REDACTED**]"
AWS_REGION = "[**REDACTED**]"
AWS_STORAGE_BUCKET_NAME =  "[**REDACTED**]"

all_files = []

s3_client = boto3.client('s3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION,
            )


try:
    # Paginator를 사용하여 모든 결과를 가져오기
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=AWS_STORAGE_BUCKET_NAME, Prefix='eval_pending/'):
        if 'Contents' in page:
            for obj in page['Contents']:
                file_info = {
                    'Key': obj['Key'],  # 파일 경로
                    'Size': obj['Size'],  # 파일 크기 (바이트)
                    'LastModified': obj['LastModified'],  # 마지막 수정 시간
                    'StorageClass': obj.get('StorageClass', 'STANDARD'),  # 저장 클래스
                }
                all_files.append(file_info)
except Exception as e:
    print(f"Error: {e}")


filtered_list = [d for d in all_files if d['Size'] != 0]
print(filtered_list)