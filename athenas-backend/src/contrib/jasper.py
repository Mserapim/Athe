# -*- coding: utf-8 -*-
import json
import urllib.parse
import http.client

from contrib.utils import getLogger

log = getLogger("tasker")


class Client:

    class __Session:

        def __init__(self, connection, cookie):
            self._connection = connection
            self._cookie = cookie

        def __enter__(self):
            return self

        def __exit__(self, *args, **kwargs):
            self._connection.logout(self._cookie)

        def __report_parameteres(self, params):
            rst = {
                "reportParameter": [
                    {
                        "name": attr,
                        "value": value if isinstance(value, (tuple, list)) else [value],
                    }
                    for attr, value in list(params.items())
                ]
            }

            return rst

        def report_executation(self, report, params={}, output_format="PDF"):
            data = {
                "reportUnitUri": report,
                "async": True,
                "outputFormat": output_format,
                "parameters": self.__report_parameteres(params),
            }

            headers = {
                "Cookie": self._cookie,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            resp = self._connection.post(
                "rest_v2/reportExecutions",
                data,
                # 'reportExecutionRequest',
                headers=headers,
            )

            if resp.status == 200:
                data_resp = json.loads(resp.read())
                if data_resp.get("status") in ("queued", "execution"):
                    return data_resp.get("requestId")
                else:
                    log.debug("HTTP_STATUS_CODE: %d", resp.status)
                    log.debug("HTTP_BODY: %s", data_resp)
                    raise Exception(
                        "Não foi possivel solicitar o relatório, o serviço esta indisponivel."
                    )
            else:
                body = resp.read()
                log.error(f"--- begin resposne ---\n{body}\n--- end response ---")
                raise Exception("%d %s" % (resp.status, resp.reason))

        def report_executation_status(self, queued_id):
            headers = {"Cookie": self._cookie, "Accept": "application/status+json"}

            resp = self._connection.get(
                "/".join(["rest_v2", "reportExecutions", queued_id, "status"]),
                headers=headers,
            )

            if resp.status == 200:
                return json.loads(resp.read())
            else:
                raise Exception("%d %s" % (resp.status, resp.reason))

        def report_executation_detail_exports(self, request_id):
            headers = {"Cookie": self._cookie, "Accept": "application/json"}

            resp = self._connection.get(
                "/".join(["rest_v2", "reportExecutions", request_id]), headers=headers
            )

            jresp = json.loads(resp.read())
            exports = jresp.get("exports")
            return exports[0]

        def report_executation_export(self, queued_id):
            headers = {
                "Cookie": self._cookie,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            params = {"outputFormat": "pdf"}

            resp = self._connection.post(
                "/".join(["rest_v2", "reportExecutions", queued_id, "exports"]),
                headers=headers,
            )

            if resp.status == 200:
                return json.loads(resp.read())
            else:
                raise Exception("%d %s" % (resp.status, resp.reason))

        def report_executation_output(self, queued_id, output_id):
            headers = {
                "Cookie": self._cookie,
            }

            params = {"outputFormat": "pdf"}

            resp = self._connection.get(
                "/".join(
                    [
                        "rest_v2",
                        "reportExecutions",
                        queued_id,
                        "exports",
                        output_id,
                        "outputResource",
                    ]
                ),
                headers=headers,
            )

            if resp.status == 200:
                return resp
            else:
                raise Exception("%d %s" % (resp.status, resp.reason))

    def __init__(
        self, username, password, resource, context="jasperserver", legarcy=True
    ):
        self._username = username
        self._password = password
        self._resource = resource
        self._context = context
        self._legarcy = legarcy

    @classmethod
    def from_config(klass, config):
        return klass(
            username=config.get("username"),
            password=config.get("password"),
            resource=(config.get("host"), config.get("port")),
            context=config.get("context"),
            legarcy=config.get("legarcy", True),
        )

    def _mk_url(self, resource):
        base = [""]
        base.append(self._context)
        base += resource.split("/")

        return "/".join(base)

    def _data_request_transform_url_encode(self, name, data):
        return urllib.parse.urlencode(data)

    def _data_request_transform_xml(self, name, data):
        return ""

    def _data_request_transform_json(self, name, data):
        params = {}

        if name:
            params.update({name: data})
        else:
            params = data

        return json.dumps(params, indent=4)

    def get(self, resource, data={}, data_name={}, headers={}):
        return self.request("GET", resource, data, data_name, headers)

    def post(self, resource, data={}, data_name={}, headers={}):
        return self.request("POST", resource, data, data_name, headers)

    def put(self, resource, data={}, data_name={}, headers={}):
        return self.request("PUT", resource, data, data_name, headers)

    def delete(self, resource, data={}, data_name={}, headers={}):
        return self.request("DELETE", resource, data, data_name, headers)

    def request(self, method, resource, data={}, data_name=None, headers={}):
        fd = http.client.HTTPConnection(*self._resource)
        log.info("jasper resource: %s", self._resource)

        data_transform_map = {
            "application/json": self._data_request_transform_json,
            "application/xml": self._data_request_transform_xml,
            "application/x-www-form-urlencoded": self._data_request_transform_url_encode,
        }

        data_transform = data_transform_map.get(
            headers.get("Content-Type", "application/x-www-form-urlencoded")
        )

        if method.lower() == "get":
            fd.request(
                "GET",
                self._mk_url(resource) + "?" + data_transform(data_name, data),
                headers=headers,
            )
        else:
            fd.request(
                method,
                self._mk_url(resource),
                body=data_transform(data_name, data),
                headers=headers,
            )

        return fd.getresponse()

    def logout(self, cookie):
        headers = {"Cookie": cookie}

        resp = self.get("logout.html", headers=headers)

    def auth(self):
        data = {
            "j_username": self._username,
            "j_password": self._password,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        httpfd = self.get(
            ("rest/login" if self._legarcy else "rest_v2/login"),
            data=data,
            headers=headers,
        )

        if httpfd.status == 200:
            return self.__Session(self, httpfd.getheader("Set-Cookie"))
        else:
            raise Exception(
                "Não consegui realizar autenticação. (Erro %d %s)"
                % (httpfd.status, httpfd.reason)
            )


#
#
# def main():
#     jc = Client(
#         JASPER_CONFIG.get('username'),
#         JASPER_CONFIG.get('password'),
#         (JASPER_CONFIG.get('host'), JASPER_CONFIG.get('port')),
#         JASPER_CONFIG.get('context')
#     )
#
#     with jc.auth() as session:
#         queued_id = session.report_executation(
#             '/to/mpe/portalservidor/requerimento_alistamento_eleitoral',
#             {
#                 'servidor': 1501
#             }
#         )
#
#         ready = False
#         while not ready:
#             status = session.report_executation_status(queued_id)
#             ready = status.get('value') not in ('execution', 'queued')
#
#             if ready and status.get('value') == 'ready':
#                 output_id = session.report_executation_export(queued_id).get('id')
#                 resp = session.report_executation_output(queued_id, output_id)
#                 with open('/home/rodrigomatias/1.pdf', 'wb') as fd:
#                     for data in iter(lambda: resp.read(8192), ''):
#                         fd.write(data)
#             elif ready and status.get('value') == 'queued':
#                 print('wating in queue!')
#             elif ready:
#                 print('failed')
#                 print(status)
#             else:
#                 print('State: %s' % status.get('value'))
#                 time.sleep(0.05)
#
# if __name__ == '__main__':
#     main()
