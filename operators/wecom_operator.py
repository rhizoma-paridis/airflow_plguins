from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults

from hooks.wecom_hook import WecomHook


class WecomOperator(BaseOperator):

    template_fields = ('message',)

    ui_color = '#4ea4d4'  # wecom icon color

    @apply_defaults
    def __init__(self,
                 wecom_conn_id='wecom_default',
                 message_type='text',
                 message=None,
                 at_mobiles=None,
                 at_all=False,
                 *args,
                 **kwargs):
        super(WecomOperator, self).__init__(*args, **kwargs)
        self.wecom_conn_id = wecom_conn_id
        self.message_type = message_type
        self.message = message
        self.at_mobiles = at_mobiles
        self.at_all = at_all

    def execute(self, context):
        self.log.info('Sending WeChat message.')
        hook = WecomHook(
            self.wecom_conn_id,
            self.message_type,
            self.message,
            self.at_mobiles,
            self.at_all
        )
        hook.send()


def failure_callback_wecom(context):
    message = f"""## DAG: `{context['task_instance'].dag_id}`
    OWNER: `{context['dag'].owner}`
    TASKS: `{context['task_instance'].task_id}`
    Exception:
    ```python
    {context['exception']}
    ```
    """
    
    return WecomOperator(
        task_id='failure_callback_wecom',
        message_type='markdown',
        message=message,
    ).execute(context)

