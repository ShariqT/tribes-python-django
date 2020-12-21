import requests
from channels.consumer import SyncConsumer
from channels.generic.websocket import JsonWebsocketConsumer
import subprocess
from tribes_front_matter.lib import actions

def background_message_mailer(sites_to_send_message, message):
    for site in sites_to_send_message:
        requests.post(site['url'] + "/read", data={'data': site['message']})



class MessageConsumer(SyncConsumer):
    def mailout(self, message):
        background_message_mailer(message['site_list'])

class SysCommandConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()
    def receive_json(self, content):
        try:

            output = subprocess.check_output(content['cmd'], stderr=subprocess.STDOUT, shell=True)
            output_as_str = output.decode('utf-8')
            if 'jekyll doctor' in content['cmd']:
                ok_cmd = 'doctor'
            else:
                ok_cmd = 'build'
            self.send_json({'output': actions.ansi_to_html(output_as_str), 'cmd_ok': ok_cmd  })
        except subprocess.CalledProcessError as e:
            print(e.output)
            print("error")
            if 'jekyll doctor' in content['cmd']:
                err_cmd = 'doctor'
            else:
                err_cmd = 'build'
            self.send_json({'output': actions.ansi_to_html(e.output.decode('utf-8')) , 'cmd_err': err_cmd })

        


