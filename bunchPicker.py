#!/usr/bin/env python

from omsapi import OMSAPI
import requests
from dotenv import load_dotenv

load_dotenv()


def get_injection_scheme_name(run_number):

    omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
    omsapi.auth_oidc(os.getenv("OMSAPI_CLIENT_ID"), os.getenv("OMSAPI_CLIENT_SECRET"))

    q = omsapi.query("runs")
    q.verbose = False
    q.filter("run_number", run_number)
    q.attrs(["fill_number"])

    response = q.data()
    data = response.json().get("data", [])

    if not data:
        print(f"No run found or no fill_number available for run_number {run_number}.")
        return None
    else:
        fill_number = data[0]["attributes"].get("fill_number")
        if fill_number is None:
            print("Run found, but no fill_number present.")
            return None
        else:
            print(f"Fill number: {fill_number}")

            lhc = omsapi.query("diplogger/dip/acc/LHC/RunControl/RunConfiguration")
            lhc.verbose = False
            lhc.filter("fill_no", fill_number)
            lhc.attrs(["fill_no", "active_injection_scheme"])

            response = lhc.data()
            data = response.json().get("data", [])

            if not data:
                print(
                    f"No fill found or injection scheme available for fill_number {fill_number}."
                )
                return None
            else:
                injection_scheme = data[0]["attributes"].get("active_injection_scheme")
                if injection_scheme is None:
                    print("Fill found, but no injection_scheme present.")
                    return None
                else:
                    print(f"Injection scheme: {injection_scheme}")
                    return injection_scheme


def get_injection_scheme(injection_scheme_name):
    url = f"https://gitlab.cern.ch/lhc-injection-scheme/injection-schemes/raw/master/{injection_scheme_name}.json"
    response = requests.get(url)
    data = response.json()
    return data


#  SHOULD TAKE THE RUN NUMBER AND THEN IF ITS OK THEN - FIND ITS FILLING SCHEME USING OMS API AND IF NOT PRESENT IN FOLDER
#  (sth like /eos/cms/store/group/dpg_cpps/……)  CALCULATE ALL THE USED
#  BUNCH NUMBERS (PUT IT IN A SINGLE JSON PER FILLING SCHEME, IT SHOULD BE DIVIDED INTO CATEGORIES)

import sys
import json
import os


def generate_leftmost_bunches(injection_scheme_name):
    data = get_injection_scheme(injection_scheme_name=injection_scheme_name)
    bx = list(
        map(lambda x: (x - 1) // 10 + 1, data["collsIP1/5"])
    )  # convert from rf bucket to CMS count
    leftmost_bx = [bx[0]] + [bx[i] for i in range(1, len(bx)) if bx[i - 1] + 1 < bx[i]]
    return leftmost_bx


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python bunch_picker.py <inj_schemes_directory> <run_number>")
        sys.exit(1)

    inj_schemes_directory = sys.argv[1]
    run_number = sys.argv[2]

    injection_scheme_name = get_injection_scheme_name(run_number=run_number)

    file_name = f"{injection_scheme_name}.json"
    file_path = os.path.join(inj_schemes_directory, file_name)

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    if "leftmost" not in data:
        data["leftmost"] = generate_leftmost_bunches(injection_scheme_name)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
