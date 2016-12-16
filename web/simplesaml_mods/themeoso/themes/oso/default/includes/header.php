<?php



/**
 * Support the htmlinject hook, which allows modules to change header, pre and post body on all pages.
 */
$this->data['htmlinject'] = array(
        'htmlContentPre' => array(),
        'htmlContentPost' => array(),
        'htmlContentHead' => array(),
);


$jquery = array();
if (array_key_exists('jquery', $this->data)) $jquery = $this->data['jquery'];

if (array_key_exists('pageid', $this->data)) {
        $hookinfo = array(
                'pre' => &$this->data['htmlinject']['htmlContentPre'],
                'post' => &$this->data['htmlinject']['htmlContentPost'],
                'head' => &$this->data['htmlinject']['htmlContentHead'],
                'jquery' => &$jquery,
                'page' => $this->data['pageid']
        );

        SimpleSAML_Module::callHooks('htmlinject', $hookinfo);
}
// - o - o - o - o - o - o - o - o - o - o - o - o -

/**
 * Do not allow to frame SimpleSAMLphp pages from another location.
 * This prevents clickjacking attacks in modern browsers.
 *
 * If you don't want any framing at all you can even change this to
 * 'DENY', or comment it out if you actually want to allow foreign
 * sites to put SimpleSAMLphp in a frame. The latter is however
 * probably not a good security practice.
 */
header('X-Frame-Options: DENY');

?><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0" />
<script type="text/javascript" src="/<?php echo $this->data['baseurlpath']; ?>resources/script.js"></script>
<title>Ops Single Sign-on</title>

        <link rel="stylesheet" type="text/css" href="/<?php echo $this->data['baseurlpath']; ?>resources/default.css" />
        <link rel="icon" type="image/icon" href="/<?php echo $this->data['baseurlpath']; ?>resources/icons/favicon.ico" />
    <link rel='stylesheet' href="<?php echo SimpleSAML_Module::getModuleURL('themeoso/oso.css'); ?>" type='text/css' />

<?php

        $version = '1.8';
        if (array_key_exists('version', $jquery))
                $version = $jquery['version'];

        if ($version == '1.8') {
                if (isset($jquery['core']) && $jquery['core'])
                        echo('<script type="text/javascript" src="/' . $this->data['baseurlpath'] . 'resources/jquery-1.8.js"></script>' . "\n");

                if (isset($jquery['ui']) && $jquery['ui'])
                        echo('<script type="text/javascript" src="/' . $this->data['baseurlpath'] . 'resources/jquery-ui-1.8.js"></script>' . "\n");

                if (isset($jquery['css']) && $jquery['css'])
                        echo('<link rel="stylesheet" media="screen" type="text/css" href="/' . $this->data['baseurlpath'] .
                                'resources/uitheme1.8/jquery-ui.css" />' . "\n");
        }

if (isset($this->data['clipboard.js'])) {
        echo '<script type="text/javascript" src="/'. $this->data['baseurlpath'] .
                 'resources/clipboard.min.js"></script>'."\n";
}

if(!empty($this->data['htmlinject']['htmlContentHead'])) {
        foreach($this->data['htmlinject']['htmlContentHead'] AS $c) {
                echo $c;
        }
}

?>

<meta name="robots" content="noindex, nofollow" />


<?php
if(array_key_exists('head', $this->data)) {
        echo '<!-- head -->' . $this->data['head'] . '<!-- /head -->';
}
?>
</head>
<?php
$onLoad = '';
if(array_key_exists('autofocus', $this->data)) {
        $onLoad .= 'SimpleSAML_focus(\'' . $this->data['autofocus'] . '\');';
}
if (isset($this->data['onLoad'])) {
        $onLoad .= $this->data['onLoad'];
}

if($onLoad !== '') {
        $onLoad = ' onload="' . $onLoad . '"';
}
?>
<body<?php echo $onLoad; ?>>

<div id="wrap">

        <div id="header">
    <img src="<?php echo SimpleSAML_Module::getModuleURL('themeoso/Logotype_RH_OpenShiftOnline_wLogo_RGB_White.svg'); ?>" width=300px alt="OpenShift Online logo" class="float_left theme_heading">
                <h1 class="theme_heading"><a class="theme_heading" href="/<?php echo $this->data['baseurlpath']; ?>">Ops Single Sign-on</a></h1>
        <div class="clear_left"></div>
        </div>

        <div id="content">



<?php

if(!empty($this->data['htmlinject']['htmlContentPre'])) {
        foreach($this->data['htmlinject']['htmlContentPre'] AS $c) {
                echo $c;
        }
}
