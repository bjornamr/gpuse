from flask import Flask, render_template, send_from_directory

import GPUtil
app = Flask(__name__, static_url_path="", template_folder="static")

GPU_information = {}

@app.route('/inuse')
def nvidia_smi():
    for x in GPUtil.getGPUs():
        id = x.id
        memory_percentage = round(x.memoryUsed / x.memoryTotal * 100, 2)
        CPU_load = x.load
        GPU_information[id] = (id, memory_percentage, CPU_load)

    res = render_template("html/nvidiasmi.html",
                          toPass = GPU_information
    )

    return res

@app.route('/html/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


if __name__ == "__main__":
    app.run()


