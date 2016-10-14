<?php

/**
 * Authenticate using Google
 *
 * @author Joel Smith, Red Hat, Inc.
 * @package SimpleSAMLphp
 */

require_once __DIR__.'/../../../extlibinc/base_google.php';

class sspmod_authgoogle_Auth_Source_Google extends SimpleSAML_Auth_Source
{

    /**
     * The strings used to identify our states.
     */
    const STAGE_INIT = 'authgoogle:init';
    const STAGE_REDIRECT = 'authgoogle:redirect';

    /**
     * The key of the AuthId field in the state.
     */
    const AUTHID = 'authgoogle:AuthId';

    private $auth_config_file;

    /**
     * Constructor
     *
     * @param array $info  Information about this authentication source.
     * @param array $config  Configuration.
     */
    public function __construct($info, $config) {
        assert('is_array($info)');
        assert('is_array($config)');

        // Call the parent constructor first, as required by the interface
        parent::__construct($info, $config);

        $configObject = SimpleSAML_Configuration::loadFromArray($config, 'authsources[' . var_export($this->authId, TRUE) . ']');

        $this->auth_config_file = $configObject->getString('AuthConfigFile');
    }

    /**
     * Log-in using Google
     *
     * @param array &$state  Information about the current authentication.
     */
    public function authenticate(&$state)
    {
        assert('is_array($state)');

        // We are going to need the authId in order to retrieve this authentication source later
        $state[self::AUTHID] = $this->authId;

        if (isset($_SERVER['argc']) && $_SERVER['argc'] > 1)
        {
            $user = $_SERVER['argv'][1];
            $attributes = array();
            $attributes['uid'] = array(preg_replace('/@.*$/', '', $user));
            $attributes['mail'] = array($user);
            $state['Attributes'] = $attributes;
        }
        else
        {
            SSPGoogleAuth::authenticate($state, $this->auth_config_file);
        }
    }

    public function getAuthConfigFile()
    {
        return $this->auth_config_file;
    }
}
