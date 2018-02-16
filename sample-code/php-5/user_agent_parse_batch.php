<?php
require ("config.php");

# Where will the request be sent to
$url = 'https://api.whatismybrowser.com/api/v2/user_agent_parse_batch';

# -- Set up HTTP Headers
$headers = [
    'X-API-KEY: '.$api_key,
];

# -- Set up the request data
# Two of these user agents are considered "abusive", to demonstrate this feature
$user_agents = array(
    "1" => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36",
    "2" => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",

    # two abusive user agents for example:
    "3" => "Mozilla/5.0 (Linux; U; Android 2.3.6; sv-se; GT-S5660 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 Ubuntu/11.10  SELECT *",
    "4" => "Mozilla/5.0 (Linux; U; Android 2.3.6; sv-se; GT-S5660 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1 Ubuntu/11.10  \\..",

    "5" => "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
    "6" => "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
    
    #"ayy" => []  # demonstrate an "invalid" user agent - it isn't a string/unicode
);
$post_data = array("user_agents" => $user_agents);

# -- create a CURL handle containing the settings & data
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL, $url);
curl_setopt($ch,CURLOPT_POST, true);
curl_setopt($ch,CURLOPT_POSTFIELDS, json_encode($post_data));
curl_setopt($ch,CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

# -- Make the request
$result = curl_exec($ch);
$curl_info = curl_getinfo($ch);
curl_close($ch);

# -- Try to decode the api response as json
$result_json = json_decode($result);
if ($result_json === null) {
    echo "Couldn't decode the response as JSON\n";
    exit();
}

# -- Check that the server responded with a "200/Success" code
if ($curl_info['http_code'] != 200) {
    echo "Didn't receive a 200 Success response from the API\n";
    echo "Instead, there was a ".$curl_info['http_code']." code\n";
    echo "The message was: ".$result_json->result->message."\n";
    exit();
}

# -- Check the API request was successful
if ($result_json->result->code != "success") {
    throw new Exception("The API did not return a 'success' response. It said: result: ".$result_json->result.", message_code: ".$result_json->message_code.", message: ".$result_json->message_code);
    exit();
}

# Now you have "$result_json" and can store, display or process any part of the response.

# -- print the entire json dump for reference
var_dump($result_json);

# -- Copy the data to some variables for easier use
$parses = $result_json->parses;

# -- Loop over each individual "parse" item in `parses`
foreach ($parses as $parse_key => $individual_parse) {
    # remember, the JSON will probably not be in the same order as you sent it,
    # so you need to match each key in `parses` back to the key you sent through.

    echo "User Agent Key: ".$parse_key."\n";

    # At this point - inside the loop - it's basically the same as working with
    # an individual user agent parse (as is done in user_agent_parse.php). There
    # is a `result`, `parse` and possibly a `version_check`.

    # -- Copy the data to some variables for easier use
    $result = $individual_parse->result;
    $parse = $individual_parse->parse;
    $version_check = $individual_parse->version_check;

    if ($result->message_code != "user_agent_parsed") {
        echo "There was a problem parsing the user agent with the key: ".$parse_key."\n";
        echo $result->message."\n";
        continue;
    }

    # Now you can do whatever you need to do with the parse result
    # Print it to the console, store it in a database, etc
    # For example - printing to the console:

    if ($parse->is_abusive === True) {
        echo "BE CAREFUL - this user agent seems abusive\n";
        # This user agent contains one or more fragments which appear to
        # be an attempt to compromise the security of your system
    }

    if ($parse->simple_software_string) {
        echo $parse->simple_software_string."\n";
    }
    else {
        echo "Couldn't figure out what software they're using\n";
    }

    if ($parse->simple_sub_description_string) {
        echo $parse->simple_sub_description_string."\n";
    }

    if ($parse->simple_operating_platform_string) {
        echo $parse->simple_operating_platform_string."\n";
    }

    if ($version_check) {
        # Your API account has access to version checking information

        if ($version_check->is_checkable === True) {
            if ($version_check->is_up_to_date === True) {
                echo $parse->software_name." is up to date\n";
            }
            else {
                echo $parse->software_name." is out of date [".join(".", $parse->software_version_full)."]\n";

                if ($version_check->latest_version) {
                    echo "The latest version is ".join(".", $version_check->latest_version)."\n";
                }

                if ($version_check->update_url) {
                    echo "You can update here: ".$version_check->update_url."\n";
                }
            }
        }
    }

    # Refer to:
    # https://developers.whatismybrowser.com/api/docs/v2/integration-guide/#user-agent-parse-field-definitions
    # for more fields you can use

    echo "---------------------------------\n";
}

# -- check the batch statistics
$parse_stats = $result_json->parse_stats;

if (count($user_agents) != $parse_stats->total) {
    echo "There was a mismatch in the number of user agents sent/returned.\n";
    # your request might have had duplicate keys in `user_agents`
}

if ($parse_stats->errors > 0) {
    echo "There was an error parsing ".$parse_stats->errors." of the user agents\n";
}
else {
    echo "All ".$parse_stats->success." user agents were parsed\n";
}
