<?php
require ("config.php");

# Where will the request be sent to
$url = 'https://api.whatismybrowser.com/api/v2/software_version_numbers/all';

# -- Set up HTTP Headers
$headers = [
    'X-API-KEY: '.$api_key,
];

# -- create a CURL handle containing the settings & data
$ch = curl_init();
curl_setopt($ch,CURLOPT_URL, $url);
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

$version_data = $result_json->version_data;

foreach ($version_data as $software_key => $software_version_data) {

    echo "Version data for ".$software_key."\n";

    foreach ($software_version_data as $stream_code_key => $stream_version_data) {

        #var_dump($stream_version_data);

        echo "  Stream: ".$stream_code_key."\n";

        echo "\tThe latest version number for ".$software_key." [".$stream_code_key."] is ".join(".", $stream_version_data->latest_version)."\n";

        if ($stream_version_data->update) {
            echo "\tUpdate no: ".$stream_version_data->update."\n";
        }

        if ($stream_version_data->update_url) {
            echo "\tUpdate URL: ".$stream_version_data->update_url."\n";
        }

        if ($stream_version_data->download_url) {
            echo "\tDownload URL: ".$stream_version_data->download_url."\n";
        }
    }

    echo "---------------------------------\n";
}