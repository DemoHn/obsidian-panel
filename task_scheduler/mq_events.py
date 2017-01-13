from app.tools.mq_proxy import WS_TAG, MessageEventHandler, MessageQueueProxy

class TaskEventHandler(MessageEventHandler):

    __prefix__ = "task"
    def __init__(self):
        MessageEventHandler.__init__(self)

    def start_download(self, flag, values):
        from task_scheduler.tasks import DownloadTaskManager
        manager = DownloadTaskManager()
        manager.add_download_java_task(
            values.get("download_link"),
            values.get("binary_dir"),
            values.get("uid")
        )

    def terminate_download(self, flag, values):
        pass

    def download_pool_status(self, flag, values):
        from task_scheduler.tasks import DownloadingTasksPool
        dp = DownloadingTasksPool()
        return dp.get_all()
