<?php

require_once __DIR__.'/../../../extlibinc/authdata.php';

/**
 * Authorize using YAML data
 *
 * @author Joel Smith, Red Hat, Inc.
 * @package SimpleSAMLphp
 */

class sspmod_authorizeyaml_Auth_Process_Authorize extends SimpleSAML_Auth_ProcessingFilter
{
    private $yaml_authdata_path;

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
    }

    /**
     * Check to see if this user has rights to access
     * the destination resource, and if so, add the
     * roles to the attribute list.
     *
     * @param array &$request  The current request
     */
    public function process(&$request)
    {
        assert('is_array($request)');
        assert('array_key_exists("Attributes", $request)');

        $authdata = new AuthData($this->yaml_authdata_path);
        $entityid = $request['Destination']['entityid'];

        $user = $request['Attributes']['mail'][0];
        $groups = $authdata->getGroups($user);

        $resource = $authdata->getResource($entityid);
        $role = $authdata->getRoles($resource, $user, $groups);
        if (!is_null($role) && !empty($role))
        {
            $request['Attributes']['role'] = array($role);
        }
        else
        {
            $this->unauthorized($request);
        }
    }


    /**
     * When the process logic determines that the user is not
     * authorized for this service, then forward the user to
     * an 403 unauthorized page.
     *
     * Separated this code into its own method so that child
     * classes can override it and change the action. Forward
     * thinking in case a "chained" ACL is needed, more complex
     * permission logic.
     *
     * @param array $request
     */
    protected function unauthorized(&$request)
    {
        // Save state and redirect to 403 page
        $id = SimpleSAML_Auth_State::saveState($request, 'authorizeyaml:Authorize');
        $url = SimpleSAML_Module::getModuleURL('authorizeyaml/authorizeyaml_403.php');
        \SimpleSAML\Utils\HTTP::redirectTrustedURL($url, array('StateId' => $id));
    }
}
