python3 -m venv /home/ubuntu/myvenv
source /home/ubuntu/myvenv/bin/activate
cd /home/ubuntu/KAIA_CSMS_BETA/kaia_app
pip3 install -r /home/ubuntu/KAIA_CSMS_BETA/kaia_app/requirements.txt
python3 /home/ubuntu/KAIA_CSMS_BETA/kaia_app/manage.py migrate --run-syncdb
python3 /home/ubuntu/KAIA_CSMS_BETA/kaia_app/manage.py createsuperuser --username admin --email admin@example.com --noinput
python3 /home/ubuntu/KAIA_CSMS_BETA/kaia_app/manage.py collectstatic
python3 /home/ubuntu/KAIA_CSMS_BETA/kaia_app/manage.py runserver 0.0.0.0:8080
