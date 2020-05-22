"""
    PLO-Ciwaruga

    Main Program
    20/04/2020
"""

from flask import Flask, request
from Scrapper import ScrapperDetik, ScrapperKompas, ScrapperRepublika
from Scrapper import ScrapperWrapper
from Params import Params
app = Flask(__name__)

# Getting params for the app
params = Params()
params.getEnvSettings()


@app.route('/')
def home():
    return "Not Yet, bruh.", 404


@app.route('/update')
def updateQuery():
    try:
        # Getting arguments for each site
        nKompas = request.args.get('kompas')
        nDetik = request.args.get('detik')
        nRepublika = request.args.get('republika')

        # Sanitizing inputs
        if nKompas:
            nKompas = int(nKompas)
        else:
            nKompas = params.n_kompas

        if nDetik:
            nDetik = int(nDetik)
        else:
            nDetik = params.n_detik

        if nRepublika:
            nRepublika = int(nRepublika)
        else:
            nRepublika = params.n_republika

        # Getting the NEWS!
        kompasScrap = ScrapperKompas(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # kompasScrap.get(nKompas)
        # kompasScrap.toLabel(params.label_studio_url)
        kompasWrapper = ScrapperWrapper(
            kompasScrap, 'kompas', nKompas, params.label_studio_url)

        detikScrap = ScrapperDetik(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # detikScrap.get(nDetik)
        # detikScrap.toLabel(params.label_studio_url)
        detikWrapper = ScrapperWrapper(
            detikScrap, 'detik', nDetik, params.label_studio_url)

        republikaScrap = ScrapperRepublika(
            chromeExecPath=params.chrome_driver_path,
            chromeBinPath=params.chrome_bin_path)
        # republikaScrap.get(nRepublika)
        # republikaScrap.toLabel(params.label_studio_url)
        republikaWrapper = ScrapperWrapper(
            republikaScrap, 'republika', nRepublika, params.label_studio_url)

        kompasWrapper.start()
        detikWrapper.start()
        republikaWrapper.start()

        return "Success", 200

    except TypeError as TE:
        print("[ERROR] : Type error on update query")
        print("[ERROR INFO] : ", TE)

        return "Error", 400


@app.route('/set/<paramType>', methods=['POST'])
def setParams(paramType):
    if paramType == 'labelurl':
        url = request.form.get('url')
        print('[INFO] Got request label change to %s' % (url))

        if url != None or len(url) == 0:
            params.label_studio_url = url
            params.update()

            return "Success", 200

        else:
            return "Error", 400

    else:
        return "Error", 400


if __name__ == "__main__":
    app.run(debug=True)
