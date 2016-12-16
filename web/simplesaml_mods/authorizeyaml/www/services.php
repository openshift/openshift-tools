<?php

require_once __DIR__.'/../extlibinc/authdata.php';

if (!array_key_exists('StateId', $_REQUEST)) {
    throw new SimpleSAML_Error_BadRequest('Missing required StateId query parameter.');
}
$state = SimpleSAML_Auth_State::loadState($_REQUEST['StateId'], 'authorizeyaml:Services');

$globalConfig = SimpleSAML_Configuration::getInstance();
$t = new SimpleSAML_XHTML_Template($globalConfig, 'authorizeyaml:services.php');
if (isset($state['Source']['auth'])) {
    $t->data['LogoutURL'] = SimpleSAML_Module::getModuleURL('core/authenticate.php', array('as' => $state['Source']['auth']))."&logout";
}

// Find authentication source
assert('array_key_exists("sspmod_authorizeyaml_Auth_Process_Services.yaml_authdata_path", $state)');
$yaml_authdata_path = $state['sspmod_authorizeyaml_Auth_Process_Services.yaml_authdata_path'];
$extra_non_sso_resources = null;
if (array_key_exists('sspmod_authorizeyaml_Auth_Process_Services.yaml_extra_data_path', $state))
{
    $tmp = yaml_parse_file($state['sspmod_authorizeyaml_Auth_Process_Services.yaml_extra_data_path']);
    if (array_key_exists('extra_non_sso_resources', $tmp))
    {
        $extra_non_sso_resources = $tmp['extra_non_sso_resources'];
    }
}


$authdata = new AuthData($yaml_authdata_path);
$user = $state['Attributes']['mail'][0];
$groups = $authdata->getGroups($user);
$resource_ids = $authdata->getResourceIds();
$resources = array();
foreach ($resource_ids as $rid)
{
    $resource = $authdata->getResource($rid);
    if (count($authdata->getRoles($resource, $user, $groups)) != 0)
    {
        array_push($resources, array('resource_id' => $rid, 'name' => $resource['name']));
    }
}
$t->data['resources'] = $resources;
$t->data['extra_non_sso_resources'] = $extra_non_sso_resources;
$t->show();
