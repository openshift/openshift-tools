<?php
/**
 * Template which is shows the resources the user has access to with links to each SSO for the service
 *
 * @package SimpleSAMLphp
 */


$this->includeAtTemplateBase('includes/header.php');
if (isset($this->data['LogoutURL'])) {
?>
<p class='float_right'><a href="<?php echo htmlspecialchars($this->data['LogoutURL']); ?>"><?php echo $this->t('{status:logout}'); ?></a></p>
<?php
}
?>
<h1>Services Available via Single Sign-on</h1>
<?php

if (isset($this->data['resources']) && is_array($this->data['resources']) && count($this->data['resources']) > 0)
{
?>
<ul class="resource_list">
<?php foreach ($this->data['resources'] as $resource) { ?>
    <li><a href='/<?php echo $this->data['baseurlpath']; ?>saml2/idp/SSOService.php?spentityid=<?php echo urlencode($resource['resource_id']);?>'><?php echo htmlspecialchars($resource['name'])?></a>
<?php } ?>
</ul>

<?PHP
if ($this->data['extra_non_sso_resources'])
{
?>
<h1>Non-SSO Resources</h1>

<ul class="resource_list">
<?php foreach ($this->data['extra_non_sso_resources'] as $resource) { ?>
    <li><a href='<?php echo $resource['url'];?>'><?php echo htmlspecialchars($resource['name'])?></a>
<?php } ?>
</ul>

<?php
}
}
else
{
?>
You appear to be logged in as a user with no rights to any resources. Are you sure you authenticated with the right account?

<?php
}
$this->includeAtTemplateBase('includes/footer.php');
