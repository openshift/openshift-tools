<?PHP

require_once 'Google/autoload.php';

class SSPGoogleAuth
{
    public static function authenticate(&$ssp_state, $secrets_file, $auth_code = NULL)
    {
        $client = new Google_Client();
        $client->setAuthConfigFile($secrets_file);

        // we're only using this for authentication, so we only need to see the email address
        $client->setScopes('email');

        if (isset($ssp_state['SSPGoogleAuth_access_token_expiration']) && $ssp_state['SSPGoogleAuth_access_token_expiration'] < time())
        {
            unset($ssp_state['SSPGoogleAuth_access_token']);
        }

        if (!is_null($auth_code))
        {
            $client->authenticate($auth_code);

            $token_data = $client->verifyIdToken()->getAttributes();

            $attributes = array();
            $attributes['uid'] = array(preg_replace('/@.*$/', '', $token_data['payload']['email']));
            $attributes['mail'] = array($token_data['payload']['email']);
            $ssp_state['Attributes'] = $attributes;

            $ssp_state['SSPGoogleAuth_access_token'] = $client->getAccessToken();
            $ssp_state['SSPGoogleAuth_access_token_expiration'] = $client->verifyIdToken()->getAttributes()['payload']['exp'];
            $stateID = SimpleSAML_Auth_State::saveState($ssp_state, sspmod_authgoogle_Auth_Source_Google::STAGE_REDIRECT);
            $linkback = SimpleSAML_Module::getModuleURL('authgoogle/linkback.php', array('state' => base64_encode($stateID)));
            header('Location: ' . filter_var($linkback, FILTER_SANITIZE_URL));
            exit;
        }

        if (isset($ssp_state['SSPGoogleAuth_access_token']) && $ssp_state['SSPGoogleAuth_access_token'])
        {
            $client->setAccessToken($ssp_state['SSPGoogleAuth_access_token']);
        }
        else
        {
            $stateID = SimpleSAML_Auth_State::saveState($ssp_state, sspmod_authgoogle_Auth_Source_Google::STAGE_INIT);
            $client->setState(base64_encode($stateID));
            $linkback = SimpleSAML_Module::getModuleURL('authgoogle/linkback.php', array());
            $client->setRedirectUri($linkback);
            header('Location: '.filter_var($client->createAuthUrl(), FILTER_SANITIZE_URL));
            exit;
        }

        if ($client->getAccessToken())
        {
            $ssp_state['SSPGoogleAuth_access_token'] = $client->getAccessToken();
        }
    }
}
