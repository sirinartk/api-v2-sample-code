import requests
import json
import config

# Where will the request be sent to
api_url = "https://api.whatismybrowser.com/api/v2/user_agent_parse"

# -- Set up HTTP Headers
headers = {
    'X-API-KEY': config.api_key,
}

# -- Set up the request data
post_data = {
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3282.167 Safari/537.36",
}

# -- Make the request
result = requests.post(api_url, data=json.dumps(post_data), headers=headers)

# -- Try to decode the api response as json
result_json = {}
try:
    result_json = result.json()
except Exception as e:
    print(result.text())
    print("Couldn't decode the response as JSON:", e)

# -- Check that the server responded with a "200/Success" code
if result.status_code != 200:
    print("ERROR: not a 200 result. instead got: %s." % result.status_code)
    print(json.dumps(result_json, indent=2))

# -- Check the API request was successful
if result_json.get('result', {}).get('code') != "success":
    print("The API did not return a 'success' response. It said: result code: %s, message_code: %s, message: %s" % (result_json.get('result', {}).get('code'), result_json.get('result', {}).get('message_code'), result_json.get('result', {}).get('message')))
    #print(json.dumps(result_json, indent=2))
    exit() 

# Now you have "result_json" and can store, display or process any part of the response.

# -- print the entire json dump for reference
print(json.dumps(result_json, indent=2))

# copy the `parse` data to a variable for easier use
parse = result_json.get('parse')
version_check = result_json.get('version_check')

# Now you can do whatever you need to do with the parse result
# Print it to the console, store it in a database, etc
# For example - printing to the console:

if parse.get('is_abusive') is True:
    print("BE CAREFUL - this user agent seems abusive")
    # This user agent contains one or more fragments which appear to
    # be an attempt to compromise the security of your system

if parse.get('simple_software_string'):
    print(parse.get('simple_software_string'))
else:
    print("Couldn't figure out what software they're using")

if parse.get('simple_sub_description_string'):
    print(parse.get('simple_software_string'))

if parse.get('simple_operating_platform_string'):
    print(parse.get('simple_operating_platform_string'))

if version_check:
    # Your API account has access to version checking information

    if version_check.get('is_checkable') is True:
        # This software will have information about whether it's up to date or not
        if version_check.get('is_up_to_date') is True:
            print("%s is up to date" % parse.get('software_name'))
        else:
            print("%s is out of date" % parse.get('software_name'))

            if version_check.get('latest_version'):
                print("The latest version is %s" % ".".join(version_check.get('latest_version')))

            if version_check.get('update_url'):
                print("You can update here: %s" % version_check.get('update_url'))

# Refer to:
# https://developers.whatismybrowser.com/api/docs/v2/integration-guide/#user-agent-parse-field-definitions
# for more fields you can use
