import json
import os
from html import escape
from json import JSONDecodeError
from time import time

import cloudpickle as pickle
from flask import Blueprint, jsonify, make_response, render_template
from locust import FastHttpUser, between, events, task

class NeuroUser(FastHttpUser):
    wait_time = between(0.5, 2.0)
    host = "http://localhost:3003"
    def generate_payload(self):
        def square(x):
            return x*x
        pickled = pickle.dumps(square)
        json_f = json.dumps(pickled.decode("latin-1"))
        data = {
            "args": [2],
            "kwargs": {},
            "name": square.__name__,
            "function": json_f
        }
        return {"method": "rpc", "params": data}
    @task(1)
    def neuro_api_concurrent(self):
        payload = self.generate_payload()
        with self.client.post("/rpc", json=payload, catch_response=True) as response:
            try:
                if response.json()["result"] != 4:
                    response.failure("Wrong RPC result calculation")
            except JSONDecodeError:
                response.failure("Response could not be decoded as JSON")
            except KeyError:
                response.failure("Response did not contain expected key 'greeting'")

stats = {}
path = os.path.dirname(os.path.abspath(__file__))
extend = Blueprint(
    "extend",
    "extend_web_ui",
    static_folder=f"{path}/static/",
    static_url_path="/extend/static/",
    template_folder=f"{path}/templates/",
)


@events.init.add_listener
def locust_init(environment, **kwargs):
    """
    We need somewhere to store the stats.
    On the master node stats will contain the aggregated sum of all content-lengths,
    while on the worker nodes this will be the sum of the content-lengths since the
    last stats report was sent to the master
    """
    if environment.web_ui:
        # this code is only run on the master node (the web_ui instance doesn't exist on workers)
        @extend.route("/content-length")
        def total_content_length():
            """
            Add a route to the Locust web app where we can see the total content-length for each
            endpoint Locust users are hitting. This is also used by the Content Length tab in the
            extended web UI to show the stats. See `updateContentLengthStats()` and
            `renderContentLengthTable()` in extend.js.
            """
            report = {"stats": []}
            if stats:
                stats_tmp = []

                for name, inner_stats in stats.items():
                    q_size = inner_stats["queue_size"]
                    running_workers = inner_stats["running_workers"]
                    peak_q_size = inner_stats["peak_queue_size"]

                    stats_tmp.append(
                        {"name": name, "safe_name": escape(name, quote=False),"peak_queue_size": peak_q_size, "queue_size": q_size, "running_workers": running_workers}
                    )

                    # Truncate the total number of stats and errors displayed since a large number of rows will cause the app
                    # to render extremely slowly.
                    report = {"stats": stats_tmp[:500]}
                return jsonify(report)
            return jsonify(stats)

        @extend.route("/neuro")
        def extend_web_ui():
            """
            Add route to access the extended web UI with our new tab.
            """
            # ensure the template_args are up to date before using them
            environment.web_ui.update_template_args()
            return render_template("extend.html", **environment.web_ui.template_args)

        @extend.route("/neuro/csv")
        def request_content_length_csv():
            """
            Add route to enable downloading of neuro api stats as CSV
            """
            response = make_response(content_length_csv())
            file_name = "neuro_api{0}.csv".format(time())
            disposition = "attachment;filename={0}".format(file_name)
            response.headers["Content-type"] = "text/csv"
            response.headers["Content-disposition"] = disposition
            return response

        def content_length_csv():
            """Returns the some neuro api stats as CSV."""
            rows = [
                ",".join(
                    [
                        '"Name"',
                        '"Peak Queue Size"'
                        '"Queue Size"',
                        '"Running Workers"'
                    ]
                )
            ]

            if stats:
                for url, inner_stats in stats.items():
                    rows.append(
                        '"%s",%.2f, %.2f, %.2f'
                        % (
                            url,
                            inner_stats["peak_queue_size"],
                            inner_stats["queue_size"],
                            inner_stats["running_workers"],
                        )
                    )
            return "\n".join(rows)

        # register our new routes and extended UI with the Locust web UI
        environment.web_ui.app.register_blueprint(extend)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, exception, context, **kwargs):
    """
    Event handler that get triggered on every request
    """
    r_json = response.json()
    stats.setdefault(name, {"peak_queue_size": 0, "queue_size": 0, "running_workers": 0})
    if r_json["queued_tasks"] > stats[name]["peak_queue_size"]:
        stats[name]["peak_queue_size"] = r_json["queued_tasks"]
    stats[name]["queue_size"] = r_json["queued_tasks"]
    stats[name]["running_workers"] = r_json["workers"]


@events.reset_stats.add_listener
def on_reset_stats():
    """
    Event handler that get triggered on click of web UI Reset Stats button
    """
    global stats
    stats = {}
