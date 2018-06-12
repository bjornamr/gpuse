from flask import Flask, \
    render_template, \
    send_from_directory, \
    redirect, \
    url_for
import time
import subprocess
import xmltodict
app = Flask(__name__, static_url_path="", template_folder="static")

OLD_STAMP = 0
NVIDIA_SMI_XML = None

GPU_information = {}


@app.route('/inuse')
def nvidia_smi():
    gpu_information = parsed_nvidiasmi()

    res = render_template("html/nvidiasmi.html",
                          toPass=gpu_information
                          )
    return res


def nvidiasmi_xml(caching=10):
    global OLD_STAMP
    global NVIDIA_SMI_XML
    stamp = time.time()
    subprocess.getoutput('nvidia-smi --xml-format -q')
    diff = stamp - OLD_STAMP
    if diff > caching:
        OLD_STAMP = stamp
        print("changed xml", NVIDIA_SMI_XML)
        NVIDIA_SMI_XML = subprocess.getoutput('nvidia-smi --xml-format -q')
    return NVIDIA_SMI_XML


def parsed_nvidiasmi():
    xml = nvidiasmi_xml()
    gpu_information = xmltodict.parse(xml)
    gpus = gpu_information["nvidia_smi_log"]["gpu"]
    gpu_result = {}
    for gpu in gpus:
        id = int(gpu["minor_number"])
        fan_speed = gpu["fan_speed"]
        name = gpu["product_name"]
        gpu_temp = gpu["temperature"]["gpu_temp"]
        used = float(gpu["fb_memory_usage"]["used"].split()[0])
        total = float(gpu["fb_memory_usage"]["total"].split()[0])
        memory_percentage = round((used / total) * 100, 2)
        gpu_load = gpu["utilization"]["gpu_util"]
        gpu_result[id] = (id,
                          str(memory_percentage) + " %",
                          gpu_load,
                          fan_speed,
                          gpu_temp,
                          name
                          )
    return gpu_result


@app.route("/")
def root():
    return redirect(url_for("nvidia_smi"))


@app.route('/html/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

