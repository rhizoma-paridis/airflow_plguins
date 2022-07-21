import json

import requests

from airflow import AirflowException
from airflow.hooks.http_hook import HttpHook


class WecomHook(HttpHook):

    def __init__(self,
                 wecom_conn_id='wecom_default',
                 message_type='text',
                 message=None,
                 at_mobiles=None,
                 at_all=False,
                 *args,
                 **kwargs
                 ):
        super(WecomHook, self).__init__(http_conn_id=wecom_conn_id, *args, **kwargs)
        self.message_type = message_type
        self.message = message
        self.at_mobiles = at_mobiles
        self.at_all = at_all

    def _get_endpoint(self):
        """
        Get Wecom endpoint for sending message.
        """
        conn = self.get_connection(self.http_conn_id)
        token = conn.password
        if not token:
            raise AirflowException('Wecom token is requests but get nothing, '
                                   'check you conn_id configuration.')
        return 'cgi-bin/webhook/send?key={}'.format(token)

    def _build_message(self):
        """
        Build different type of Wecom message
        As most commonly used type, text message just need post message content
        rather than a dict like ``{'content': 'message'}``
        """
        if self.message_type in ['text', 'markdown']:
            data = {
                'msgtype': self.message_type,
                self.message_type: {
                    'content': self.message
                }
            }
        else:
            data = {
                'msgtype': self.message_type,
                self.message_type: self.message
            }
        return json.dumps(data)

    def get_conn(self, headers=None):
        """
        Overwrite HttpHook get_conn because just need base_url and headers and
        not don't need generic params

        :param headers: additional headers to be passed through as a dictionary
        :type headers: dict
        """
        conn = self.get_connection(self.http_conn_id)
        self.base_url = conn.host if conn.host else 'https://qyapi.weixin.qq.com'
        session = requests.Session()
        if headers:
            session.headers.update(headers)
        return session

    def send(self):
        """
        Send Wecom message
        """
        support_type = ['text', 'link', 'markdown', 'actionCard', 'feedCard']
        if self.message_type not in support_type:
            raise ValueError('WecomWebhookHook only support {} '
                             'so far, but receive {}'.format(support_type, self.message_type))

        data = self._build_message()
        self.log.info('Sending Wecom type %s message %s', self.message_type, data)
        resp = self.run(endpoint=self._get_endpoint(),
                        data=data,
                        headers={'Content-Type': 'application/json'})

        # Wecom success send message will with errcode equal to 0
        if int(resp.json().get('errcode')) != 0:
            raise AirflowException('Send Wecom message failed, receive error '
                                   'message %s', resp.text)
        self.log.info('Success Send Wecom message')

