from flask import Flask, render_template, send_from_directory, redirect, url_for
import subprocess
import xmltodict
app = Flask(__name__, static_url_path="", template_folder="static")

GPU_information = {}

@app.route('/inuse')
def nvidia_smi():
    GPU_information = parsedNvidiaSmi()

    res = render_template("html/nvidiasmi.html",
                          toPass=GPU_information
                          )
    return res

def getNvidiaSmiXML():
    return subprocess.getoutput('nvidia-smi --xml-format -q')

def parsedNvidiaSmi():
    xml = getNvidiaSmiXML()
    gpu_information = xmltodict.parse(xml)
    gpus = gpu_information["nvidia_smi_log"]["gpu"]
    gpu_result = {}
    for gpu in gpus:
        id = int(gpu["minor_number"])
        fan_speed = gpu["fan_speed"]
        name = gpu["product_name"]
        gpu_temp = gpu["temperature"]["gpu_temp"]
        memory_percentage = round(float(gpu["fb_memory_usage"]["used"].split()[0]) / \
                            float(gpu["fb_memory_usage"]["total"].split()[0]) * 100, 2)
        GPU_load = gpu["utilization"]["gpu_util"]
        gpu_result[id] = (id, str(memory_percentage) + " %", GPU_load, fan_speed, gpu_temp, name)
    return gpu_result

@app.route("/")
def root():
    return redirect(url_for("nvidia_smi"))


@app.route('/html/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == "__main__":
    app.run()

