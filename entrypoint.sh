cd /home/ubuntu
python3 -m venv myvenv
source myvenv/bin/activate
cd KAIA_CSMS_BETA/kaia_app
pip3 install -r requirements.txt
python3 manage.py migrate --run-syncdb
python3 manage.py createsuperuser --username admin --email admin@example.com --noinput
python3 manage.py collectstatic
python3 manage.py runserver 0.0.0.0:8080