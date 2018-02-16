import requests
import json
import config

# Where will the request be sent to
api_url = "https://api.whatismybrowser.com/api/v2/software_version_numbers/all"

# -- Set up HTTP Headers
headers = {
    'X-API-KEY': config.api_key,
}

# -- Make the request
result = requests.get(api_url, headers=headers)

# -- Try to decode the api response as json
result_json = {}
try:
    result_json = result.json()
except Exception as e:
    print(result.text())
    print("Couldn't decode the response as JSON:", e)
    exit()

# -- Check that the server responded with a "200/Success" code
if result.status_code != 200:
    print("ERROR: not a 200 result. instead got: %s." % result.status_code)
    print(json.dumps(result_json, indent=2))
    exit()

# -- Check the API request was successful
if result_json.get('result', {}).get('code') != "success":
    print("The API did not return a 'success' response. It said: result code: %s, message_code: %s, message: %s" % (result_json.get('result', {}).get('code'), result_json.get('result', {}).get('message_code'), result_json.get('result', {}).get('message')))
    #print(json.dumps(result_json, indent=2))
    exit() 

# Now you have "result_json" and can store, display or process any part of the response.

# -- Print the entire json dump for reference
print(json.dumps(result_json, indent=2))

# -- Copy the `version_data` data to a variable for easier use
version_data = result_json.get('version_data')

# -- Loop over all the different software version data elements
for software_key in version_data:

    print("Version data for %s" % software_key)

    software_version_data = version_data.get(software_key)

    for stream_code_key in software_version_data:

        #print(software_version_data.get(stream_code_key))

        print("  Stream: %s" % stream_code_key)

        print("\tThe latest version number for %s [%s] is %s" % (software_key, stream_code_key, ".".join(software_version_data.get(stream_code_key).get("latest_version"))))
        
        if software_version_data.get(stream_code_key).get("update"):
            print("\tUpdate no: %s" % software_version_data.get(stream_code_key).get("update"))

        if software_version_data.get(stream_code_key).get("update_url"):
            print("\tUpdate URL: %s" % software_version_data.get(stream_code_key).get("update_url"))

        if software_version_data.get(stream_code_key).get("download_url"):
            print("\tDownload URL: %s" % software_version_data.get(stream_code_key).get("download_url"))

    print("---------------------------------")
