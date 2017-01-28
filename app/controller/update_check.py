from urllib.request import urlopen, Request
import yaml, subprocess, os, traceback, json
from datetime import datetime
from app import logger

class UpdateChecker():
    def __init__(self):
        self.version_file = "VERSION"
        self.config_file  = "config.yaml"
        self.zhao = self.get_zhao()
        pass

    def get_zhao(self):
        fr = open(os.path.join(os.getcwd(), self.config_file), "r")
        docs = yaml.load(fr)
        fr.close()

        _zhao = docs.get("global").get("zhao")
        if _zhao == None:
            return 0
        else:
            return int(_zhao)

    def get_current_version(self):
        f = open(os.path.join(os.getcwd(), self.version_file), "r")
        data = f.read()
        f.close()
        return data.strip()

    def check_newest_release(self):
        # use GitHub API
        # https://developer.github.com/v3/repos/releases/
        if self.zhao == 0:
            _url = "https://api.github.com/repos/DemoHn/obsidian-panel/releases"
            req  = Request(url = _url)
            try:
                resp = urlopen(req, timeout=15)
                release_info = resp.read().decode()
                r_json = json.loads(release_info)

                # GitHub itself has arranged all release by the order of publish time.
                # Thus, the first element must be the newest version
                release = r_json[0]
                release_model = {
                    "version": release["tag_name"],
                    "publish_date": datetime.strptime(release["published_at"],"%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                    "release_note": release["body"]
                }
                return release_model
            except:
                logger.error(traceback.format_exc())
                return None
        elif self.zhao == 1:
            # use coding.net OpenAPI
            _url = "https://coding.net/api/user/DemoHn2016/project/obsidian-panel/git/tags"
            req  = Request(url = _url)
            try:
                resp = urlopen(req, timeout=15)
                release_info = resp.read().decode()
                r_json = json.loads(release_info)

                # GitHub itself has arranged all release by the order of publish time.
                # Thus, the first element must be the newest version
                release = r_json["data"]["list"][0]

                created_timestamp = release["created_at"]

                created_time = datetime.fromtimestamp(created_timestamp / 1e3)
                release_model = {
                    "version": release["name"],
                    "publish_date": created_time.strftime("%Y-%m-%d"),
                    "release_note": release["message"]
                }
                return release_model
            except:
                logger.error(traceback.format_exc())
                return None
        else:
            return None

    def update_software(self):
        # execute command
        p = subprocess.Popen("ob-panel upgrade",shell=True)
        rc = p.wait()
        if str(rc) == "0":
            return True
        else:
            return False

    def reboot(self):
        os.system("ob-panel restart")
