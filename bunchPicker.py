
# example
# from omsapi import OMSAPI

# #fill your values
# my_app_id='omsapi_test_id'
# my_app_secret='2398938-30389039-33'

# omsapi = OMSAPI("https://cmsoms.cern.ch/agg/api", "v1", cert_verify=False)
# omsapi.auth_oidc(my_app_id,my_app_secret)

# # Create a query.
# q = omsapi.query("eras")

# # Execute query & fetch data
# response = q.data()

# # Display JSON data
# print(response.json())


#  SHOULD TAKE THE RUN NUMBER AND THEN IF ITS OK THEN - FIND ITS FILLING SCHEME USING OMS API AND IF NOT PRESENT IN FOLDER 
#  (sth like /eos/cms/store/group/dpg_cpps/……)  CALCULATE ALL THE USED 
#  BUNCH NUMBERS (PUT IT IN A SINGLE JSON PER FILLING SCHEME, IT SHOULD BE DIVIDED INTO CATEGORIES)

import sys
import json
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python bunch_picker.py <filename.json>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            print("Successfully parsed JSON:")

            bx = list(map(lambda x: (x - 1) // 10 + 1, data["collsIP1/5"])) # convert from rf bucket to CMS count
            leftmost_bx = [bx[0]] + [bx[i] for i in range(1, len(bx)) if bx[i-1] + 1 < bx[i]]
            #print(leftmost_bx)


        base = os.path.splitext(os.path.basename(filename))[0]
        output_filename = f"leftmost_bx_{base}.txt"

        with open(output_filename, "w", encoding="utf-8") as out_file:
            for value in leftmost_bx:
                out_file.write(f"{value}\n")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON. {e}")
