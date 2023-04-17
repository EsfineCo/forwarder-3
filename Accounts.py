from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from nocodb.nocodb import NocoDBProject, APIToken
from nocodb.filters import InFilter, EqFilter
from nocodb.infra.requests_client import NocoDBRequestsClient
from time import sleep

def noco(func):
    while True:
        try:
            data = func
            break
        except:
            sleep(2)
            continue
    return data

client = NocoDBRequestsClient(
    # Your API Token retrieved from NocoDB conf
    APIToken("kufc33_c2kvv-NPvHFtEZz3D6ZHUdtzIInVJkGu4"),
    # Your nocodb root path
    "http://nocodb.promotele.ru"
)

def auth():
    def login_with_service_account():
        settings = {
                    "client_config_backend": "service",
                    "service_config": {
                        "client_json_file_path": "service-secrets.json",
                    }
                }
        # Create instance of GoogleAuth
        gauth = GoogleAuth(settings=settings)
        # Authenticate
        gauth.ServiceAuth()
        return gauth

    gauth = login_with_service_account()

    drive = GoogleDrive(gauth)
    return drive

class Main:
    project = NocoDBProject(
    "noco",
    "Main"
    )

    def download(number):
        print (number)
        project = Main.project
        table_name = "Accounts"
        drive = auth()

        count = noco(client.table_count(project, table_name, InFilter("status", "Free"))['count'])
        accounts = noco(client.table_row_list(project, table_name, InFilter("status", "Free"), params={'limit': count})['list'])

        if len(accounts[:number]) != number:
            print (f'{number-len(accounts)} accounts are missing!')
            input(f'{number-len(accounts)} accounts are missing!')
        else:
            for account in accounts[:number]:
                session = drive.CreateFile({'id': account['session']})
                session.GetContentFile(f'accounts/{account["phone"]}.session')
                json = drive.CreateFile({'id': account['json']})
                json.GetContentFile(f'accounts/{account["phone"]}.json')
                bot_session = drive.CreateFile({'id': account['bot_session']})
                bot_session.GetContentFile('forwarder_bot.session')
                bot_token = account['bot_token']
                with open('token.txt', 'w') as f:
                    f.write(bot_token)
                f.close()
                row_info = {
                    "status": "Working",
                }
                noco(client.table_row_update(project, table_name, account['Id'], row_info))