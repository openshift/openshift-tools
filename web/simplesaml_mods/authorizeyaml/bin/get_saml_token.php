#!/usr/bin/php
<?PHP
// This is the base directory of the SimpleSAMLphp installation
$baseDir = dirname(dirname(dirname(dirname(__FILE__))));

// Add library autoloader.
require_once($baseDir . '/lib/_autoload.php');

// Initialize the configuration.
$configdir = SimpleSAML\Utils\Config::getConfigDir();
SimpleSAML_Configuration::setConfigDir($configdir);
$globalConfig = SimpleSAML_Configuration::getInstance();

// Figure out which SP the user wants a token for
$_REQUEST['spentityid']=getenv('SSH_ORIGINAL_COMMAND');

// these are to fake out simpleSAMLphp to make it think this is
// a web request so that it'll spit back an HTML post redirect
// page that includes a SAML token in the form data.
$_SERVER['REQUEST_URI']='/';
$_SERVER['HTTPS']='on';
$_SERVER['SERVER_PORT']='443';
$_SERVER['SERVER_NAME']=$globalConfig->getValue('server.hostname');
$_SERVER['SERVER_PROTOCOL'] = 'HTTP/1.0';
$_SERVER['REQUEST_METHOD'] = 'GET';

chdir("$baseDir/www/saml2/idp");

// No need to try to create a real session here.
SimpleSAML_Session::useTransientSession();

// Now that the stage is set, call SSOService.php so that it will
// generate an HTML page with a SAML token in the form data
require 'SSOService.php';
