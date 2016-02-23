# vim: expandtab:tabstop=4:shiftwidth=4
''' python-flask wsgi REST API for receiving zagg-sender metrics '''

# Reason: disable pylint import-error because our libs/deps aren't loaded on jenkins.
# Status: temporary until we start testing in a container where our stuff is installed.
# pylint: disable=import-error
from flask import Flask
from flask import jsonify
from flask import request
from openshift_tools.monitoring.metricmanager import UniqueMetric, MetricManager
import yaml

# Reason: pylint is complaining about an invalid constant name
# Status: When doing python-flask apps as a single small file, globals are used.
# pylint: disable=invalid-name
flask_app = Flask(__name__)

@flask_app.route('/metric', methods=['GET', 'POST'])
def process_metric():
    ''' Receive POSTs to the '/metric' URL endpoint and
        process/save them '''
    if request.method == 'POST':
        config_file = '/etc/openshift_tools/zagg_server.yaml'
        config = yaml.load(file(config_file))

        json = request.get_json()

        for target in config['targets']:
            new_metric = UniqueMetric.from_request(json)
            mymm = MetricManager(target['path'])
            mymm.write_metrics(new_metric)

        return jsonify({"success": True})

    else:
        flask_app.logger.error('Unexpectedly received non-POST request (GET?)')
        return jsonify({"success": False})

if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler
    log_handler = RotatingFileHandler('zagg.log', maxBytes=100000, backupCount=1)
    log_handler.setLevel(logging.DEBUG)
    flask_app.logger.addHandler(log_handler)
    flask_app.run(host='0.0.0.0')
