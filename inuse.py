from flask import Flask, render_template, send_from_directory, redirect, url_for
import subprocess
import xmltodict
app = Flask(__name__, static_url_path="", template_folder="static")

GPU_information = {}

@app.route('/inuse')
def nvidia_smi():
    GPU_information = xmlnvidiasmi()

    res = render_template("html/nvidiasmi.html",
                          toPass=GPU_information
                          )
    return res

def xmlnvidiasmi():
    r = subprocess.getoutput('nvidia-smi --xml-format -q')
    #print(r)
    newdict = xmltodict.parse(r)
    gpus = newdict["nvidia_smi_log"]["gpu"]
    gpu_result = {}
    for gpu in gpus:
        id = int(gpus["minor_number"])
        fanspeed = gpus["fan_speed"]
        name = gpus["product_name"]
        gpu_temp = gpus["temperature"]["gpu_temp"]
        memory_percentage = round(float(gpus["fb_memory_usage"]["used"].split()[0]) / \
                            float(gpus["fb_memory_usage"]["total"].split()[0]) * 100, 2)
        GPU_load = gpus["utilization"]["gpu_util"]
        gpu_result[id] = (id, str(memory_percentage) + " %", GPU_load, fanspeed, gpu_temp, name)
    return gpu_result

@app.route("/")
def root():
    return redirect(url_for("nvidia_smi"))


@app.route('/html/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == "__main__":
    app.run()

