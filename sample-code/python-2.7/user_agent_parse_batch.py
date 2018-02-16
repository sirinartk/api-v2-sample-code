import requests
import json
import config

# Where will the request be sent to
api_url = "https://api.whatismybrowser.com/api/v2/user_agent_parse_batch"

# -- Set up HTTP Headers
headers = {
    'X-API-KEY': config.api_key,
}

# -- Set up the request data
# Two of these user agents are considered "abusive", to demonstrate this feature
user_agents = {
    "1": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "2": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",

    # two abusive user agents for example:
    "3": "Mozilla/5.0 (Linux; U; Android 2.3.6; sv-se; GT-S5660 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 Ubuntu/11.10  SELECT *",
    "4": "Mozilla/5.0 (Linux; U; Android 2.3.6; sv-se; GT-S5660 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 Ubuntu/11.10  \\..",

    "5": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    "6": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    
    #"ayy": []  # demonstrate an "invalid" user agent - it isn't a string/unicode
}
post_data = {
    "user_agents": user_agents,
}

# -- Make the request
result = requests.post(api_url, data=json.dumps(post_data), headers=headers)

# -- Try to decode the api response as json
result_json = {}
try:
    result_json = result.json()
except Exception, e:
    print result.text()
    print "Couldn't decode the response as JSON:", e
    exit()

# -- Check that the server responded with a "200/Success" code
if result.status_code != 200:
    print "ERROR: not a 200 result. instead got: %s." % result.status_code
    print json.dumps(result_json, indent=2)
    exit()

# -- Check the API request was successful
if result_json.get('result', {}).get('code') != "success":
    print "The API did not return a 'success' response. It said: result code: %s, message_code: %s, message: %s" % (result_json.get('result', {}).get('code'), result_json.get('result', {}).get('message_code'), result_json.get('result', {}).get('message'))
    #print json.dumps(result_json, indent=2)
    exit() 

# Now you have "result_json" and can store, display or process any part of the response.

# -- print the entire json dump for reference
print json.dumps(result_json, indent=2)

# -- Copy the `parses` data to a variable for easier use
parses = result_json.get('parses')

# -- Loop over each individual "parse" item in `parses`
for parse_key in parses:
    
    # remember, the JSON will probably not be in the same order as you sent it,
    # so you need to match each key in `parses` back to the key you sent through.
    print "User Agent Key: %s" % parse_key

    individual_parse = parses.get(parse_key)

    # At this point - inside the loop - it's basically the same as working with
    # an individual user agent parse (as is done in user_agent_parse.py). There
    # is a `result`, `parse` and possibly a `version_check`.

    # -- Copy the data to some variables for easier use
    result = individual_parse.get('result')
    parse = individual_parse.get('parse')
    version_check = individual_parse.get('version_check')

    if result.get('message_code') != "user_agent_parsed":
        print "There was a problem parsing the user agent with the key: %s" % parse_key
        print result.get('message')  # human readable
        continue  # to the next one in `parses`

    # Now you can do whatever you need to do with the parse result
    # Print it to the console, store it in a database, etc
    # For example - printing to the console:

    if parse.get('is_abusive') is True:
        print "BE CAREFUL - this user agent seems abusive"
        # This user agent contains one or more fragments which appear to
        # be an attempt to compromise the security of your system

    if parse.get('simple_software_string'):
        print parse.get('simple_software_string')
    else:
        print "Couldn't figure out what software they're using"

    if parse.get('simple_sub_description_string'):
        print parse.get('simple_software_string')

    if parse.get('simple_operating_platform_string'):
        print parse.get('simple_operating_platform_string')

    if version_check:
        # Your API account has access to version checking information

        if version_check.get('is_checkable') is True:
            # This software will have information about whether it's up to date or not
            if version_check.get('is_up_to_date') is True:
                print "%s is up to date" % parse.get('software_name')
            else:
                print "%s is out of date [%s]" % (parse.get('software_name'), ".".join(parse.get('software_version_full')))

                if version_check.get('latest_version'):
                    print "The latest version is %s" % ".".join(version_check.get('latest_version'))

                if version_check.get('update_url'):
                    print "You can update here: %s" % version_check.get('update_url')

    # Refer to:
    # https://developers.whatismybrowser.com/api/docs/v2/integration-guide/#user-agent-parse-field-definitions
    # for more fields you can use

    print "---------------------------------"

# -- check the batch statistics
parse_stats = result_json.get('parse_stats')

if len(user_agents) != parse_stats.get('total'):
    print "There was a mismatch in the number of user agents sent/returned."
    # Your request might have had duplicate keys in `user_agents`

if parse_stats.get('error') > 0:
    print "There was an error parsing %s of the user agents" % parse_stats.get('error')
    # Refer to the `result` key in the individual user agent parse results (inside `parses`) for more information
else:
    print "All %s user agents were parsed" % parse_stats.get('success')
