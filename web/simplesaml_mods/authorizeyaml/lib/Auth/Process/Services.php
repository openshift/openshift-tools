<?php

/**
 * List available SP services using YAML authorization data
 *
 * @author Joel Smith, Red Hat, Inc.
 * @package SimpleSAMLphp
 */

class sspmod_authorizeyaml_Auth_Process_Services extends SimpleSAML_Auth_ProcessingFilter
{
    /**
     * The key of the yaml file path fields in the state.
     */
    const YAML_AUTHDATA_PATH = 'sspmod_authorizeyaml_Auth_Process_Services.yaml_authdata_path';
    const YAML_EXTRA_DATA_PATH = 'sspmod_authorizeyaml_Auth_Process_Services.yaml_extra_data_path';

    private $yaml_authdata_path;
    private $yaml_extra_data_path;

    /**
     * Initialize this filter.
     *
     * @param array $config  Configuration information about this filter.
     * @param mixed $reserved  For future use.
     * @throws SimpleSAML_Error_Exception In case of invalid configuration.
     */
    public function __construct($config, $reserved)
    {
        parent::__construct($config, $reserved);

        assert('is_array($config)');

        $this->yaml_authdata_path = $config['yaml_authdata_path'];
        $this->yaml_extra_data_path = $config['yaml_extra_data_path'];
    }

    /**
     * Send the user to a list of services that s/he has
     * access to with links to the SSO for all those
     * services.
     *
     * @param array &$request  The current request
     */
    public function process(&$request)
    {
        assert('is_array($request)');
        assert('array_key_exists("Attributes", $request)');

        // save the yaml file paths
        $request[self::YAML_AUTHDATA_PATH] = $this->yaml_authdata_path;
        $request[self::YAML_EXTRA_DATA_PATH] = $this->yaml_extra_data_path;

        // Save state and redirect to the services page
        $id = SimpleSAML_Auth_State::saveState($request, 'authorizeyaml:Services');
        $url = SimpleSAML_Module::getModuleURL('authorizeyaml/services.php');
        \SimpleSAML\Utils\HTTP::redirectTrustedURL($url, array('StateId' => $id));
    }
}
