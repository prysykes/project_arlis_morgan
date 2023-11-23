from authlib.integrations.django_client import OAuth

appConf = {
    "OAUTH2_CLIENT_ID": "workbench_user",
    "OAUTH2_CLIENT_SECRET": "ltwZ0G1bPnTrFlWnMJ5msOYJRlKWK1g0",
    "OAUTH2_ISSUER": "http://localhost:8080/realms/arlis_workbench",
    "DJANGO_PORT": 8000


}
oauth = OAuth()


