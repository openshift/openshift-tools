<?php

require_once __DIR__.'/../extlibinc/base_google.php';

/**
 * Handle linkback() response from Google.
 */

// If $_GET['code'] is set, that should mean that the redirect
// is coming from Google's API server, so we need to take that
// code and use it to authenticate.

$code = NULL;
if (array_key_exists('code', $_REQUEST))
{
    $code = $_REQUEST['code'];
}

if (!array_key_exists('state', $_REQUEST) || empty($_REQUEST['state'])) {
	throw new SimpleSAML_Error_BadRequest('Missing state parameter on google linkback endpoint.');
}
$stage = isset($code) ? sspmod_authgoogle_Auth_Source_Google::STAGE_INIT : sspmod_authgoogle_Auth_Source_Google::STAGE_REDIRECT;
$state = SimpleSAML_Auth_State::loadState(base64_decode($_REQUEST['state']), $stage);

if (!is_null($code) && !empty($code))
{
    // Find authentication source
    if (!array_key_exists(sspmod_authgoogle_Auth_Source_Google::AUTHID, $state))
    {
        throw new SimpleSAML_Error_BadRequest('No data in state for ' . sspmod_authgoogle_Auth_Source_Google::AUTHID);
    }
    $sourceId = $state[sspmod_authgoogle_Auth_Source_Google::AUTHID];
    $source = SimpleSAML_Auth_Source::getById($sourceId);
    if ($source === NULL) {
        throw new SimpleSAML_Error_BadRequest('Could not find authentication source with id ' . var_export($sourceId, TRUE));
    }

    SSPGoogleAuth::authenticate($state, $source->getAuthConfigFile(), $code);
}

SimpleSAML_Auth_Source::completeAuth($state);
