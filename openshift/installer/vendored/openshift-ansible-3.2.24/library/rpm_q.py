



<!DOCTYPE html>
<html lang="en" class="">
  <head prefix="og: http://ogp.me/ns# fb: http://ogp.me/ns/fb# object: http://ogp.me/ns/object# article: http://ogp.me/ns/article# profile: http://ogp.me/ns/profile#">
    <meta charset='utf-8'>
    

    <link crossorigin="anonymous" href="https://assets-cdn.github.com/assets/frameworks-98550932b9f11a849da143d2dbc9dfaa977a17656514d323ae9ce0d6fa688b60.css" media="all" rel="stylesheet" />
    <link crossorigin="anonymous" href="https://assets-cdn.github.com/assets/github-b55c6a2db8c337849a80d2520fa0b213d8486d35ace9b6b15d84c381ea8bb696.css" media="all" rel="stylesheet" />
    
    
    <link crossorigin="anonymous" href="https://assets-cdn.github.com/assets/site-becbb68a5e0ae3f94214b9e9edea2c49974f6d60b9eae715b70e5d017ff1b935.css" media="all" rel="stylesheet" />
    

    <link as="script" href="https://assets-cdn.github.com/assets/frameworks-88471af1fec40ff9418efbe2ddd15b6896af8d772f8179004c254dffc25ea490.js" rel="preload" />
    
    <link as="script" href="https://assets-cdn.github.com/assets/github-c4177fc28385bc04fc26a831fe1f9d69d5d7a3242566683a9daac147e1280847.js" rel="preload" />

    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta http-equiv="Content-Language" content="en">
    <meta name="viewport" content="width=device-width">
    
    <title>openshift-ansible/rpm_q.py at master · openshift/openshift-ansible · GitHub</title>
    <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="GitHub">
    <link rel="fluid-icon" href="https://github.com/fluidicon.png" title="GitHub">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="apple-touch-icon" sizes="57x57" href="/apple-touch-icon-57x57.png">
    <link rel="apple-touch-icon" sizes="60x60" href="/apple-touch-icon-60x60.png">
    <link rel="apple-touch-icon" sizes="72x72" href="/apple-touch-icon-72x72.png">
    <link rel="apple-touch-icon" sizes="76x76" href="/apple-touch-icon-76x76.png">
    <link rel="apple-touch-icon" sizes="114x114" href="/apple-touch-icon-114x114.png">
    <link rel="apple-touch-icon" sizes="120x120" href="/apple-touch-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="144x144" href="/apple-touch-icon-144x144.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/apple-touch-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon-180x180.png">
    <meta property="fb:app_id" content="1401488693436528">

      <meta content="https://avatars0.githubusercontent.com/u/792337?v=3&amp;s=400" name="twitter:image:src" /><meta content="@github" name="twitter:site" /><meta content="summary" name="twitter:card" /><meta content="openshift/openshift-ansible" name="twitter:title" /><meta content="openshift-ansible - OpenShift Ansible Code" name="twitter:description" />
      <meta content="https://avatars0.githubusercontent.com/u/792337?v=3&amp;s=400" property="og:image" /><meta content="GitHub" property="og:site_name" /><meta content="object" property="og:type" /><meta content="openshift/openshift-ansible" property="og:title" /><meta content="https://github.com/openshift/openshift-ansible" property="og:url" /><meta content="openshift-ansible - OpenShift Ansible Code" property="og:description" />
      <meta name="browser-stats-url" content="https://api.github.com/_private/browser/stats">
    <meta name="browser-errors-url" content="https://api.github.com/_private/browser/errors">
    <link rel="assets" href="https://assets-cdn.github.com/">
    
    <meta name="pjax-timeout" content="1000">
    
    <meta name="request-id" content="340600F0:40E4:5C0C495:57CED387" data-pjax-transient>

    <meta name="msapplication-TileImage" content="/windows-tile.png">
    <meta name="msapplication-TileColor" content="#ffffff">
    <meta name="selected-link" value="repo_source" data-pjax-transient>

    <meta name="google-site-verification" content="KT5gs8h0wvaagLKAVWq8bbeNwnZZK1r1XQysX3xurLU">
<meta name="google-site-verification" content="ZzhVyEFwb7w3e0-uOTltm8Jsck2F5StVihD0exw2fsA">
    <meta name="google-analytics" content="UA-3769691-2">

<meta content="collector.githubapp.com" name="octolytics-host" /><meta content="github" name="octolytics-app-id" /><meta content="340600F0:40E4:5C0C495:57CED387" name="octolytics-dimension-request_id" />
<meta content="/&lt;user-name&gt;/&lt;repo-name&gt;/blob/show" data-pjax-transient="true" name="analytics-location" />



  <meta class="js-ga-set" name="dimension1" content="Logged Out">



        <meta name="hostname" content="github.com">
    <meta name="user-login" content="">

        <meta name="expected-hostname" content="github.com">
      <meta name="js-proxy-site-detection-payload" content="ZWNhYmZkYzE3OWM4MTE1ZTY3ZTBhMGEyZjYwYjU2MDRhMDQzY2JkZmRlZTFhODRhZWQ5ZDk3MTE3YjI3M2NlYnx7InJlbW90ZV9hZGRyZXNzIjoiNTIuNi4wLjI0MCIsInJlcXVlc3RfaWQiOiIzNDA2MDBGMDo0MEU0OjVDMEM0OTU6NTdDRUQzODciLCJ0aW1lc3RhbXAiOjE0NzMxNzIzNTl9">


      <link rel="mask-icon" href="https://assets-cdn.github.com/pinned-octocat.svg" color="#4078c0">
      <link rel="icon" type="image/x-icon" href="https://assets-cdn.github.com/favicon.ico">

    <meta name="html-safe-nonce" content="def7b9de2f8fef27920459ee4b3cc9f5a6843a34">
    <meta content="3701de654fec0d4d220a3412ad1bc6ef2e8258de" name="form-nonce" />

    <meta http-equiv="x-pjax-version" content="13cab7f77477644fc72f582220d901c4">
    

      
  <meta name="description" content="openshift-ansible - OpenShift Ansible Code">
  <meta name="go-import" content="github.com/openshift/openshift-ansible git https://github.com/openshift/openshift-ansible.git">

  <meta content="792337" name="octolytics-dimension-user_id" /><meta content="openshift" name="octolytics-dimension-user_login" /><meta content="24109199" name="octolytics-dimension-repository_id" /><meta content="openshift/openshift-ansible" name="octolytics-dimension-repository_nwo" /><meta content="true" name="octolytics-dimension-repository_public" /><meta content="false" name="octolytics-dimension-repository_is_fork" /><meta content="24109199" name="octolytics-dimension-repository_network_root_id" /><meta content="openshift/openshift-ansible" name="octolytics-dimension-repository_network_root_nwo" />
  <link href="https://github.com/openshift/openshift-ansible/commits/master.atom" rel="alternate" title="Recent Commits to openshift-ansible:master" type="application/atom+xml">


      <link rel="canonical" href="https://github.com/openshift/openshift-ansible/blob/master/library/rpm_q.py" data-pjax-transient>
  </head>


  <body class="logged-out  env-production  vis-public page-blob">
    <div id="js-pjax-loader-bar" class="pjax-loader-bar"><div class="progress"></div></div>
    <a href="#start-of-content" tabindex="1" class="accessibility-aid js-skip-to-content">Skip to content</a>

    
    
    



          <header class="site-header js-details-container" role="banner">
  <div class="container-responsive">
    <a class="header-logo-invertocat" href="https://github.com/" aria-label="Homepage" data-ga-click="(Logged out) Header, go to homepage, icon:logo-wordmark">
      <svg aria-hidden="true" class="octicon octicon-mark-github" height="32" version="1.1" viewBox="0 0 16 16" width="32"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>
    </a>

    <button class="btn-link float-right site-header-toggle js-details-target" type="button" aria-label="Toggle navigation">
      <svg aria-hidden="true" class="octicon octicon-three-bars" height="24" version="1.1" viewBox="0 0 12 16" width="18"><path d="M11.41 9H.59C0 9 0 8.59 0 8c0-.59 0-1 .59-1H11.4c.59 0 .59.41.59 1 0 .59 0 1-.59 1h.01zm0-4H.59C0 5 0 4.59 0 4c0-.59 0-1 .59-1H11.4c.59 0 .59.41.59 1 0 .59 0 1-.59 1h.01zM.59 11H11.4c.59 0 .59.41.59 1 0 .59 0 1-.59 1H.59C0 13 0 12.59 0 12c0-.59 0-1 .59-1z"></path></svg>
    </button>

    <div class="site-header-menu">
      <nav class="site-header-nav site-header-nav-main">
        <a href="/personal" class="js-selected-navigation-item nav-item nav-item-personal" data-ga-click="Header, click, Nav menu - item:personal" data-selected-links="/personal /personal">
          Personal
</a>        <a href="/open-source" class="js-selected-navigation-item nav-item nav-item-opensource" data-ga-click="Header, click, Nav menu - item:opensource" data-selected-links="/open-source /open-source">
          Open source
</a>        <a href="/business" class="js-selected-navigation-item nav-item nav-item-business" data-ga-click="Header, click, Nav menu - item:business" data-selected-links="/business /business/partners /business/features /business/customers /business">
          Business
</a>        <a href="/explore" class="js-selected-navigation-item nav-item nav-item-explore" data-ga-click="Header, click, Nav menu - item:explore" data-selected-links="/explore /trending /trending/developers /integrations /integrations/feature/code /integrations/feature/collaborate /integrations/feature/ship /explore">
          Explore
</a>      </nav>

      <div class="site-header-actions">
            <a class="btn btn-primary site-header-actions-btn" href="/join?source=header-repo" data-ga-click="(Logged out) Header, clicked Sign up, text:sign-up">Sign up</a>
          <a class="btn site-header-actions-btn mr-2" href="/login?return_to=%2Fopenshift%2Fopenshift-ansible%2Fblob%2Fmaster%2Flibrary%2Frpm_q.py" data-ga-click="(Logged out) Header, clicked Sign in, text:sign-in">Sign in</a>
      </div>

        <nav class="site-header-nav site-header-nav-secondary">
          <a class="nav-item" href="/pricing">Pricing</a>
          <a class="nav-item" href="/blog">Blog</a>
          <a class="nav-item" href="https://help.github.com">Support</a>
          <a class="nav-item header-search-link" href="https://github.com/search">Search GitHub</a>
              <div class="header-search scoped-search site-scoped-search js-site-search" role="search">
  <!-- </textarea> --><!-- '"` --><form accept-charset="UTF-8" action="/openshift/openshift-ansible/search" class="js-site-search-form" data-scoped-search-url="/openshift/openshift-ansible/search" data-unscoped-search-url="/search" method="get"><div style="margin:0;padding:0;display:inline"><input name="utf8" type="hidden" value="&#x2713;" /></div>
    <label class="form-control header-search-wrapper js-chromeless-input-container">
      <div class="header-search-scope">This repository</div>
      <input type="text"
        class="form-control header-search-input js-site-search-focus js-site-search-field is-clearable"
        data-hotkey="s"
        name="q"
        placeholder="Search"
        aria-label="Search this repository"
        data-unscoped-placeholder="Search GitHub"
        data-scoped-placeholder="Search"
        autocapitalize="off">
    </label>
</form></div>

        </nav>
    </div>
  </div>
</header>



    <div id="start-of-content" class="accessibility-aid"></div>

      <div id="js-flash-container">
</div>


    <div role="main">
        <div itemscope itemtype="http://schema.org/SoftwareSourceCode">
    <div id="js-repo-pjax-container" data-pjax-container>
      
<div class="pagehead repohead instapaper_ignore readability-menu experiment-repo-nav">
  <div class="container repohead-details-container">

    

<ul class="pagehead-actions">

  <li>
      <a href="/login?return_to=%2Fopenshift%2Fopenshift-ansible"
    class="btn btn-sm btn-with-count tooltipped tooltipped-n"
    aria-label="You must be signed in to watch a repository" rel="nofollow">
    <svg aria-hidden="true" class="octicon octicon-eye" height="16" version="1.1" viewBox="0 0 16 16" width="16"><path d="M8.06 2C3 2 0 8 0 8s3 6 8.06 6C13 14 16 8 16 8s-3-6-7.94-6zM8 12c-2.2 0-4-1.78-4-4 0-2.2 1.8-4 4-4 2.22 0 4 1.8 4 4 0 2.22-1.78 4-4 4zm2-4c0 1.11-.89 2-2 2-1.11 0-2-.89-2-2 0-1.11.89-2 2-2 1.11 0 2 .89 2 2z"></path></svg>
    Watch
  </a>
  <a class="social-count" href="/openshift/openshift-ansible/watchers"
     aria-label="66 users are watching this repository">
    66
  </a>

  </li>

  <li>
      <a href="/login?return_to=%2Fopenshift%2Fopenshift-ansible"
    class="btn btn-sm btn-with-count tooltipped tooltipped-n"
    aria-label="You must be signed in to star a repository" rel="nofollow">
    <svg aria-hidden="true" class="octicon octicon-star" height="16" version="1.1" viewBox="0 0 14 16" width="14"><path d="M14 6l-4.9-.64L7 1 4.9 5.36 0 6l3.6 3.26L2.67 14 7 11.67 11.33 14l-.93-4.74z"></path></svg>
    Star
  </a>

    <a class="social-count js-social-count" href="/openshift/openshift-ansible/stargazers"
      aria-label="236 users starred this repository">
      236
    </a>

  </li>

  <li>
      <a href="/login?return_to=%2Fopenshift%2Fopenshift-ansible"
        class="btn btn-sm btn-with-count tooltipped tooltipped-n"
        aria-label="You must be signed in to fork a repository" rel="nofollow">
        <svg aria-hidden="true" class="octicon octicon-repo-forked" height="16" version="1.1" viewBox="0 0 10 16" width="10"><path d="M8 1a1.993 1.993 0 0 0-1 3.72V6L5 8 3 6V4.72A1.993 1.993 0 0 0 2 1a1.993 1.993 0 0 0-1 3.72V6.5l3 3v1.78A1.993 1.993 0 0 0 5 15a1.993 1.993 0 0 0 1-3.72V9.5l3-3V4.72A1.993 1.993 0 0 0 8 1zM2 4.2C1.34 4.2.8 3.65.8 3c0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zm3 10c-.66 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zm3-10c-.66 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2z"></path></svg>
        Fork
      </a>

    <a href="/openshift/openshift-ansible/network" class="social-count"
       aria-label="378 users are forked this repository">
      378
    </a>
  </li>
</ul>

    <h1 class="public ">
  <svg aria-hidden="true" class="octicon octicon-repo" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M4 9H3V8h1v1zm0-3H3v1h1V6zm0-2H3v1h1V4zm0-2H3v1h1V2zm8-1v12c0 .55-.45 1-1 1H6v2l-1.5-1.5L3 16v-2H1c-.55 0-1-.45-1-1V1c0-.55.45-1 1-1h10c.55 0 1 .45 1 1zm-1 10H1v2h2v-1h3v1h5v-2zm0-10H2v9h9V1z"></path></svg>
  <span class="author" itemprop="author"><a href="/openshift" class="url fn" rel="author">openshift</a></span><!--
--><span class="path-divider">/</span><!--
--><strong itemprop="name"><a href="/openshift/openshift-ansible" data-pjax="#js-repo-pjax-container">openshift-ansible</a></strong>

</h1>

  </div>
  <div class="container">
    
<nav class="reponav js-repo-nav js-sidenav-container-pjax"
     itemscope
     itemtype="http://schema.org/BreadcrumbList"
     role="navigation"
     data-pjax="#js-repo-pjax-container">

  <span itemscope itemtype="http://schema.org/ListItem" itemprop="itemListElement">
    <a href="/openshift/openshift-ansible" aria-selected="true" class="js-selected-navigation-item selected reponav-item" data-hotkey="g c" data-selected-links="repo_source repo_downloads repo_commits repo_releases repo_tags repo_branches /openshift/openshift-ansible" itemprop="url">
      <svg aria-hidden="true" class="octicon octicon-code" height="16" version="1.1" viewBox="0 0 14 16" width="14"><path d="M9.5 3L8 4.5 11.5 8 8 11.5 9.5 13 14 8 9.5 3zm-5 0L0 8l4.5 5L6 11.5 2.5 8 6 4.5 4.5 3z"></path></svg>
      <span itemprop="name">Code</span>
      <meta itemprop="position" content="1">
</a>  </span>

    <span itemscope itemtype="http://schema.org/ListItem" itemprop="itemListElement">
      <a href="/openshift/openshift-ansible/issues" class="js-selected-navigation-item reponav-item" data-hotkey="g i" data-selected-links="repo_issues repo_labels repo_milestones /openshift/openshift-ansible/issues" itemprop="url">
        <svg aria-hidden="true" class="octicon octicon-issue-opened" height="16" version="1.1" viewBox="0 0 14 16" width="14"><path d="M7 2.3c3.14 0 5.7 2.56 5.7 5.7s-2.56 5.7-5.7 5.7A5.71 5.71 0 0 1 1.3 8c0-3.14 2.56-5.7 5.7-5.7zM7 1C3.14 1 0 4.14 0 8s3.14 7 7 7 7-3.14 7-7-3.14-7-7-7zm1 3H6v5h2V4zm0 6H6v2h2v-2z"></path></svg>
        <span itemprop="name">Issues</span>
        <span class="counter">268</span>
        <meta itemprop="position" content="2">
</a>    </span>

  <span itemscope itemtype="http://schema.org/ListItem" itemprop="itemListElement">
    <a href="/openshift/openshift-ansible/pulls" class="js-selected-navigation-item reponav-item" data-hotkey="g p" data-selected-links="repo_pulls /openshift/openshift-ansible/pulls" itemprop="url">
      <svg aria-hidden="true" class="octicon octicon-git-pull-request" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M11 11.28V5c-.03-.78-.34-1.47-.94-2.06C9.46 2.35 8.78 2.03 8 2H7V0L4 3l3 3V4h1c.27.02.48.11.69.31.21.2.3.42.31.69v6.28A1.993 1.993 0 0 0 10 15a1.993 1.993 0 0 0 1-3.72zm-1 2.92c-.66 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2zM4 3c0-1.11-.89-2-2-2a1.993 1.993 0 0 0-1 3.72v6.56A1.993 1.993 0 0 0 2 15a1.993 1.993 0 0 0 1-3.72V4.72c.59-.34 1-.98 1-1.72zm-.8 10c0 .66-.55 1.2-1.2 1.2-.65 0-1.2-.55-1.2-1.2 0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2zM2 4.2C1.34 4.2.8 3.65.8 3c0-.65.55-1.2 1.2-1.2.65 0 1.2.55 1.2 1.2 0 .65-.55 1.2-1.2 1.2z"></path></svg>
      <span itemprop="name">Pull requests</span>
      <span class="counter">60</span>
      <meta itemprop="position" content="3">
</a>  </span>




  <a href="/openshift/openshift-ansible/pulse" class="js-selected-navigation-item reponav-item" data-selected-links="pulse /openshift/openshift-ansible/pulse">
    <svg aria-hidden="true" class="octicon octicon-pulse" height="16" version="1.1" viewBox="0 0 14 16" width="14"><path d="M11.5 8L8.8 5.4 6.6 8.5 5.5 1.6 2.38 8H0v2h3.6l.9-1.8.9 5.4L9 8.5l1.6 1.5H14V8z"></path></svg>
    Pulse
</a>
  <a href="/openshift/openshift-ansible/graphs" class="js-selected-navigation-item reponav-item" data-selected-links="repo_graphs repo_contributors /openshift/openshift-ansible/graphs">
    <svg aria-hidden="true" class="octicon octicon-graph" height="16" version="1.1" viewBox="0 0 16 16" width="16"><path d="M16 14v1H0V0h1v14h15zM5 13H3V8h2v5zm4 0H7V3h2v10zm4 0h-2V6h2v7z"></path></svg>
    Graphs
</a>

</nav>

  </div>
</div>

<div class="container new-discussion-timeline experiment-repo-nav">
  <div class="repository-content">

    

<a href="/openshift/openshift-ansible/blob/5ca0a74fb271678708268c940fd52ccd15d207ca/library/rpm_q.py" class="d-none js-permalink-shortcut" data-hotkey="y">Permalink</a>

<!-- blob contrib key: blob_contributors:v21:a7fe4f4023a6b59519e9c7599bf3f9f5 -->

<div class="file-navigation js-zeroclipboard-container">
  
<div class="select-menu branch-select-menu js-menu-container js-select-menu float-left">
  <button class="btn btn-sm select-menu-button js-menu-target css-truncate" data-hotkey="w"
    
    type="button" aria-label="Switch branches or tags" tabindex="0" aria-haspopup="true">
    <i>Branch:</i>
    <span class="js-select-button css-truncate-target">master</span>
  </button>

  <div class="select-menu-modal-holder js-menu-content js-navigation-container" data-pjax aria-hidden="true">

    <div class="select-menu-modal">
      <div class="select-menu-header">
        <svg aria-label="Close" class="octicon octicon-x js-menu-close" height="16" role="img" version="1.1" viewBox="0 0 12 16" width="12"><path d="M7.48 8l3.75 3.75-1.48 1.48L6 9.48l-3.75 3.75-1.48-1.48L4.52 8 .77 4.25l1.48-1.48L6 6.52l3.75-3.75 1.48 1.48z"></path></svg>
        <span class="select-menu-title">Switch branches/tags</span>
      </div>

      <div class="select-menu-filters">
        <div class="select-menu-text-filter">
          <input type="text" aria-label="Filter branches/tags" id="context-commitish-filter-field" class="form-control js-filterable-field js-navigation-enable" placeholder="Filter branches/tags">
        </div>
        <div class="select-menu-tabs">
          <ul>
            <li class="select-menu-tab">
              <a href="#" data-tab-filter="branches" data-filter-placeholder="Filter branches/tags" class="js-select-menu-tab" role="tab">Branches</a>
            </li>
            <li class="select-menu-tab">
              <a href="#" data-tab-filter="tags" data-filter-placeholder="Find a tag…" class="js-select-menu-tab" role="tab">Tags</a>
            </li>
          </ul>
        </div>
      </div>

      <div class="select-menu-list select-menu-tab-bucket js-select-menu-tab-bucket" data-tab-filter="branches" role="menu">

        <div data-filterable-for="context-commitish-filter-field" data-filterable-type="substring">


            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/README-updates/library/rpm_q.py"
               data-name="README-updates"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                README-updates
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/enterprise-3.0/library/rpm_q.py"
               data-name="enterprise-3.0"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                enterprise-3.0
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/enterprise-3.1/library/rpm_q.py"
               data-name="enterprise-3.1"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                enterprise-3.1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/enterprise-3.2/library/rpm_q.py"
               data-name="enterprise-3.2"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                enterprise-3.2
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/enterprise-3.3/library/rpm_q.py"
               data-name="enterprise-3.3"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                enterprise-3.3
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/hotfix/library/rpm_q.py"
               data-name="hotfix"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                hotfix
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/logging_fix/library/rpm_q.py"
               data-name="logging_fix"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                logging_fix
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open selected"
               href="/openshift/openshift-ansible/blob/master/library/rpm_q.py"
               data-name="master"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                master
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/next/library/rpm_q.py"
               data-name="next"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                next
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/revert-2238-no-network-plugin/library/rpm_q.py"
               data-name="revert-2238-no-network-plugin"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                revert-2238-no-network-plugin
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/revert-2325-fileglobglob/library/rpm_q.py"
               data-name="revert-2325-fileglobglob"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                revert-2325-fileglobglob
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/sdodson-patch-1/library/rpm_q.py"
               data-name="sdodson-patch-1"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                sdodson-patch-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
               href="/openshift/openshift-ansible/blob/sdodson-patch-2/library/rpm_q.py"
               data-name="sdodson-patch-2"
               data-skip-pjax="true"
               rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target js-select-menu-filter-text">
                sdodson-patch-2
              </span>
            </a>
        </div>

          <div class="select-menu-no-results">Nothing to show</div>
      </div>

      <div class="select-menu-list select-menu-tab-bucket js-select-menu-tab-bucket" data-tab-filter="tags">
        <div data-filterable-for="context-commitish-filter-field" data-filterable-type="substring">


            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.2-2/library/rpm_q.py"
              data-name="v3.0.2-2"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.2-2">
                v3.0.2-2
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.2-1/library/rpm_q.py"
              data-name="v3.0.2-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.2-1">
                v3.0.2-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.1-1/library/rpm_q.py"
              data-name="v3.0.1-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.1-1">
                v3.0.1-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0/library/rpm_q.py"
              data-name="v3.0.0"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0">
                v3.0.0
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-rc/library/rpm_q.py"
              data-name="v3.0.0-rc"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-rc">
                v3.0.0-rc
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-8/library/rpm_q.py"
              data-name="v3.0.0-8"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-8">
                v3.0.0-8
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-7/library/rpm_q.py"
              data-name="v3.0.0-7"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-7">
                v3.0.0-7
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-6/library/rpm_q.py"
              data-name="v3.0.0-6"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-6">
                v3.0.0-6
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-5/library/rpm_q.py"
              data-name="v3.0.0-5"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-5">
                v3.0.0-5
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-4/library/rpm_q.py"
              data-name="v3.0.0-4"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-4">
                v3.0.0-4
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-3/library/rpm_q.py"
              data-name="v3.0.0-3"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-3">
                v3.0.0-3
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-2/library/rpm_q.py"
              data-name="v3.0.0-2"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-2">
                v3.0.0-2
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/v3.0.0-1/library/rpm_q.py"
              data-name="v3.0.0-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="v3.0.0-1">
                v3.0.0-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.4.1-1/library/rpm_q.py"
              data-name="openshift-ansible-3.4.1-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.4.1-1">
                openshift-ansible-3.4.1-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.22-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.22-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.22-1">
                openshift-ansible-3.3.22-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.21-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.21-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.21-1">
                openshift-ansible-3.3.21-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.20-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.20-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.20-1">
                openshift-ansible-3.3.20-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.19-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.19-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.19-1">
                openshift-ansible-3.3.19-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.18-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.18-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.18-1">
                openshift-ansible-3.3.18-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.17-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.17-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.17-1">
                openshift-ansible-3.3.17-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.16-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.16-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.16-1">
                openshift-ansible-3.3.16-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.15-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.15-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.15-1">
                openshift-ansible-3.3.15-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.14-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.14-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.14-1">
                openshift-ansible-3.3.14-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.13-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.13-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.13-1">
                openshift-ansible-3.3.13-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.12-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.12-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.12-1">
                openshift-ansible-3.3.12-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.11-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.11-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.11-1">
                openshift-ansible-3.3.11-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.10-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.10-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.10-1">
                openshift-ansible-3.3.10-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.9-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.9-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.9-1">
                openshift-ansible-3.3.9-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.8-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.8-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.8-1">
                openshift-ansible-3.3.8-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.7-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.7-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.7-1">
                openshift-ansible-3.3.7-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.6-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.6-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.6-1">
                openshift-ansible-3.3.6-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.5-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.5-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.5-1">
                openshift-ansible-3.3.5-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.4-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.4-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.4-1">
                openshift-ansible-3.3.4-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.3-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.3-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.3-1">
                openshift-ansible-3.3.3-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.2-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.2-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.2-1">
                openshift-ansible-3.3.2-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.1-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.1-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.1-1">
                openshift-ansible-3.3.1-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.3.0-1/library/rpm_q.py"
              data-name="openshift-ansible-3.3.0-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.3.0-1">
                openshift-ansible-3.3.0-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.28-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.28-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.28-1">
                openshift-ansible-3.2.28-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.27-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.27-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.27-1">
                openshift-ansible-3.2.27-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.26-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.26-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.26-1">
                openshift-ansible-3.2.26-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.25-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.25-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.25-1">
                openshift-ansible-3.2.25-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.24-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.24-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.24-1">
                openshift-ansible-3.2.24-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.23-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.23-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.23-1">
                openshift-ansible-3.2.23-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.22-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.22-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.22-1">
                openshift-ansible-3.2.22-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.21-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.21-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.21-1">
                openshift-ansible-3.2.21-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.20-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.20-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.20-1">
                openshift-ansible-3.2.20-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.19-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.19-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.19-1">
                openshift-ansible-3.2.19-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.18-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.18-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.18-1">
                openshift-ansible-3.2.18-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.17-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.17-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.17-1">
                openshift-ansible-3.2.17-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.15-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.15-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.15-1">
                openshift-ansible-3.2.15-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.14-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.14-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.14-1">
                openshift-ansible-3.2.14-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.13-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.13-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.13-1">
                openshift-ansible-3.2.13-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.12-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.12-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.12-1">
                openshift-ansible-3.2.12-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.11-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.11-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.11-1">
                openshift-ansible-3.2.11-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.9-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.9-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.9-1">
                openshift-ansible-3.2.9-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.8-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.8-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.8-1">
                openshift-ansible-3.2.8-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.7-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.7-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.7-1">
                openshift-ansible-3.2.7-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.6-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.6-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.6-1">
                openshift-ansible-3.2.6-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.5-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.5-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.5-1">
                openshift-ansible-3.2.5-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.4-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.4-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.4-1">
                openshift-ansible-3.2.4-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.3-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.3-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.3-1">
                openshift-ansible-3.2.3-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.2-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.2-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.2-1">
                openshift-ansible-3.2.2-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.1-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.1-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.1-1">
                openshift-ansible-3.2.1-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.2.0-1/library/rpm_q.py"
              data-name="openshift-ansible-3.2.0-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.2.0-1">
                openshift-ansible-3.2.0-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.97-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.97-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.97-1">
                openshift-ansible-3.0.97-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.96-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.96-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.96-1">
                openshift-ansible-3.0.96-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.95-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.95-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.95-1">
                openshift-ansible-3.0.95-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.94-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.94-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.94-1">
                openshift-ansible-3.0.94-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.93-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.93-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.93-1">
                openshift-ansible-3.0.93-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.92-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.92-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.92-1">
                openshift-ansible-3.0.92-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.90-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.90-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.90-1">
                openshift-ansible-3.0.90-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.89-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.89-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.89-1">
                openshift-ansible-3.0.89-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.88-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.88-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.88-1">
                openshift-ansible-3.0.88-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.87-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.87-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.87-1">
                openshift-ansible-3.0.87-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.86-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.86-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.86-1">
                openshift-ansible-3.0.86-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.85-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.85-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.85-1">
                openshift-ansible-3.0.85-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.84-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.84-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.84-1">
                openshift-ansible-3.0.84-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.83-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.83-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.83-1">
                openshift-ansible-3.0.83-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.82-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.82-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.82-1">
                openshift-ansible-3.0.82-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.81-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.81-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.81-1">
                openshift-ansible-3.0.81-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.80-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.80-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.80-1">
                openshift-ansible-3.0.80-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.79-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.79-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.79-1">
                openshift-ansible-3.0.79-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.78-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.78-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.78-1">
                openshift-ansible-3.0.78-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.77-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.77-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.77-1">
                openshift-ansible-3.0.77-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.76-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.76-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.76-1">
                openshift-ansible-3.0.76-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.75-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.75-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.75-1">
                openshift-ansible-3.0.75-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.74-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.74-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.74-1">
                openshift-ansible-3.0.74-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.73-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.73-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.73-1">
                openshift-ansible-3.0.73-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.72-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.72-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.72-1">
                openshift-ansible-3.0.72-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.71-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.71-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.71-1">
                openshift-ansible-3.0.71-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.70-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.70-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.70-1">
                openshift-ansible-3.0.70-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.69-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.69-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.69-1">
                openshift-ansible-3.0.69-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.68-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.68-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.68-1">
                openshift-ansible-3.0.68-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.67-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.67-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.67-1">
                openshift-ansible-3.0.67-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.66-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.66-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.66-1">
                openshift-ansible-3.0.66-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.65-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.65-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.65-1">
                openshift-ansible-3.0.65-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.64-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.64-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.64-1">
                openshift-ansible-3.0.64-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.63-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.63-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.63-1">
                openshift-ansible-3.0.63-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.62-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.62-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.62-1">
                openshift-ansible-3.0.62-1
              </span>
            </a>
            <a class="select-menu-item js-navigation-item js-navigation-open "
              href="/openshift/openshift-ansible/tree/openshift-ansible-3.0.61-1/library/rpm_q.py"
              data-name="openshift-ansible-3.0.61-1"
              data-skip-pjax="true"
              rel="nofollow">
              <svg aria-hidden="true" class="octicon octicon-check select-menu-item-icon" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M12 5l-8 8-4-4 1.5-1.5L4 10l6.5-6.5z"></path></svg>
              <span class="select-menu-item-text css-truncate-target" title="openshift-ansible-3.0.61-1">
                openshift-ansible-3.0.61-1
              </span>
            </a>
        </div>

        <div class="select-menu-no-results">Nothing to show</div>
      </div>

    </div>
  </div>
</div>

  <div class="btn-group float-right">
    <a href="/openshift/openshift-ansible/find/master"
          class="js-pjax-capture-input btn btn-sm"
          data-pjax
          data-hotkey="t">
      Find file
    </a>
    <button aria-label="Copy file path to clipboard" class="js-zeroclipboard btn btn-sm zeroclipboard-button tooltipped tooltipped-s" data-copied-hint="Copied!" type="button">Copy path</button>
  </div>
  <div class="breadcrumb js-zeroclipboard-target">
    <span class="repo-root js-repo-root"><span class="js-path-segment"><a href="/openshift/openshift-ansible"><span>openshift-ansible</span></a></span></span><span class="separator">/</span><span class="js-path-segment"><a href="/openshift/openshift-ansible/tree/master/library"><span>library</span></a></span><span class="separator">/</span><strong class="final-path">rpm_q.py</strong>
  </div>
</div>


  <div class="commit-tease">
      <span class="float-right">
        <a class="commit-tease-sha" href="/openshift/openshift-ansible/commit/f834279d5010f5a8b1a1cd7c75adaa7b0dce7fed" data-pjax>
          f834279
        </a>
        <relative-time datetime="2016-07-18T08:10:52Z">Jul 18, 2016</relative-time>
      </span>
      <div>
        <img alt="" class="avatar" data-canonical-src="https://1.gravatar.com/avatar/6616a4a17cf9ab34e284f83936103c9b?d=https%3A%2F%2Fassets-cdn.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png&amp;r=x&amp;s=140" height="20" src="https://camo.githubusercontent.com/98706179b01273be3b6e5b8a411a6cab07e382b8/68747470733a2f2f312e67726176617461722e636f6d2f6176617461722f36363136613461313763663961623334653238346638333933363130336339623f643d68747470732533412532462532466173736574732d63646e2e6769746875622e636f6d253246696d6167657325324667726176617461727325324667726176617461722d757365722d3432302e706e6726723d7826733d313430" width="20" />
        <span class="user-mention">Tobias Florek</span>
          <a href="/openshift/openshift-ansible/commit/f834279d5010f5a8b1a1cd7c75adaa7b0dce7fed" class="message" data-pjax="true" title="make rpm-q module pylint warning-free">make rpm-q module pylint warning-free</a>
      </div>

    <div class="commit-tease-contributors">
      <button type="button" class="btn-link muted-link contributors-toggle" data-facebox="#blob_contributors_box">
        <strong>0</strong>
         contributors
      </button>
      
    </div>

    <div id="blob_contributors_box" style="display:none">
      <h2 class="facebox-header" data-facebox-id="facebox-header">Users who have contributed to this file</h2>
      <ul class="facebox-user-list" data-facebox-id="facebox-description">
      </ul>
    </div>
  </div>

<div class="file">
  <div class="file-header">
  <div class="file-actions">

    <div class="btn-group">
      <a href="/openshift/openshift-ansible/raw/master/library/rpm_q.py" class="btn btn-sm " id="raw-url">Raw</a>
        <a href="/openshift/openshift-ansible/blame/master/library/rpm_q.py" class="btn btn-sm js-update-url-with-hash">Blame</a>
      <a href="/openshift/openshift-ansible/commits/master/library/rpm_q.py" class="btn btn-sm " rel="nofollow">History</a>
    </div>


        <button type="button" class="btn-octicon disabled tooltipped tooltipped-nw"
          aria-label="You must be signed in to make or propose changes">
          <svg aria-hidden="true" class="octicon octicon-pencil" height="16" version="1.1" viewBox="0 0 14 16" width="14"><path d="M0 12v3h3l8-8-3-3-8 8zm3 2H1v-2h1v1h1v1zm10.3-9.3L12 6 9 3l1.3-1.3a.996.996 0 0 1 1.41 0l1.59 1.59c.39.39.39 1.02 0 1.41z"></path></svg>
        </button>
        <button type="button" class="btn-octicon btn-octicon-danger disabled tooltipped tooltipped-nw"
          aria-label="You must be signed in to make or propose changes">
          <svg aria-hidden="true" class="octicon octicon-trashcan" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M11 2H9c0-.55-.45-1-1-1H5c-.55 0-1 .45-1 1H2c-.55 0-1 .45-1 1v1c0 .55.45 1 1 1v9c0 .55.45 1 1 1h7c.55 0 1-.45 1-1V5c.55 0 1-.45 1-1V3c0-.55-.45-1-1-1zm-1 12H3V5h1v8h1V5h1v8h1V5h1v8h1V5h1v9zm1-10H2V3h9v1z"></path></svg>
        </button>
  </div>

  <div class="file-info">
      71 lines (59 sloc)
      <span class="file-info-divider"></span>
    1.75 KB
  </div>
</div>

  

  <div itemprop="text" class="blob-wrapper data type-python">
      <table class="highlight tab-size js-file-line-container" data-tab-size="8">
      <tr>
        <td id="L1" class="blob-num js-line-number" data-line-number="1"></td>
        <td id="LC1" class="blob-code blob-code-inner js-file-line"><span class="pl-c">#!/usr/bin/python</span></td>
      </tr>
      <tr>
        <td id="L2" class="blob-num js-line-number" data-line-number="2"></td>
        <td id="LC2" class="blob-code blob-code-inner js-file-line"><span class="pl-c"># -*- coding: utf-8 -*-</span></td>
      </tr>
      <tr>
        <td id="L3" class="blob-num js-line-number" data-line-number="3"></td>
        <td id="LC3" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L4" class="blob-num js-line-number" data-line-number="4"></td>
        <td id="LC4" class="blob-code blob-code-inner js-file-line"><span class="pl-c"># (c) 2015, Tobias Florek &lt;tob@butter.sh&gt;</span></td>
      </tr>
      <tr>
        <td id="L5" class="blob-num js-line-number" data-line-number="5"></td>
        <td id="LC5" class="blob-code blob-code-inner js-file-line"><span class="pl-c"># Licensed under the terms of the MIT License</span></td>
      </tr>
      <tr>
        <td id="L6" class="blob-num js-line-number" data-line-number="6"></td>
        <td id="LC6" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L7" class="blob-num js-line-number" data-line-number="7"></td>
        <td id="LC7" class="blob-code blob-code-inner js-file-line"><span class="pl-s">An ansible module to query the RPM database. For use, when yum/dnf are not</span></td>
      </tr>
      <tr>
        <td id="L8" class="blob-num js-line-number" data-line-number="8"></td>
        <td id="LC8" class="blob-code blob-code-inner js-file-line"><span class="pl-s">available.</span></td>
      </tr>
      <tr>
        <td id="L9" class="blob-num js-line-number" data-line-number="9"></td>
        <td id="LC9" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L10" class="blob-num js-line-number" data-line-number="10"></td>
        <td id="LC10" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L11" class="blob-num js-line-number" data-line-number="11"></td>
        <td id="LC11" class="blob-code blob-code-inner js-file-line"><span class="pl-c"># pylint: disable=redefined-builtin,wildcard-import,unused-wildcard-import</span></td>
      </tr>
      <tr>
        <td id="L12" class="blob-num js-line-number" data-line-number="12"></td>
        <td id="LC12" class="blob-code blob-code-inner js-file-line"><span class="pl-k">from</span> ansible.module_utils.basic <span class="pl-k">import</span> <span class="pl-k">*</span></td>
      </tr>
      <tr>
        <td id="L13" class="blob-num js-line-number" data-line-number="13"></td>
        <td id="LC13" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L14" class="blob-num js-line-number" data-line-number="14"></td>
        <td id="LC14" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">DOCUMENTATION</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L15" class="blob-num js-line-number" data-line-number="15"></td>
        <td id="LC15" class="blob-code blob-code-inner js-file-line"><span class="pl-s">---</span></td>
      </tr>
      <tr>
        <td id="L16" class="blob-num js-line-number" data-line-number="16"></td>
        <td id="LC16" class="blob-code blob-code-inner js-file-line"><span class="pl-s">module: rpm_q</span></td>
      </tr>
      <tr>
        <td id="L17" class="blob-num js-line-number" data-line-number="17"></td>
        <td id="LC17" class="blob-code blob-code-inner js-file-line"><span class="pl-s">short_description: Query the RPM database</span></td>
      </tr>
      <tr>
        <td id="L18" class="blob-num js-line-number" data-line-number="18"></td>
        <td id="LC18" class="blob-code blob-code-inner js-file-line"><span class="pl-s">author: Tobias Florek</span></td>
      </tr>
      <tr>
        <td id="L19" class="blob-num js-line-number" data-line-number="19"></td>
        <td id="LC19" class="blob-code blob-code-inner js-file-line"><span class="pl-s">options:</span></td>
      </tr>
      <tr>
        <td id="L20" class="blob-num js-line-number" data-line-number="20"></td>
        <td id="LC20" class="blob-code blob-code-inner js-file-line"><span class="pl-s">  name:</span></td>
      </tr>
      <tr>
        <td id="L21" class="blob-num js-line-number" data-line-number="21"></td>
        <td id="LC21" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    description:</span></td>
      </tr>
      <tr>
        <td id="L22" class="blob-num js-line-number" data-line-number="22"></td>
        <td id="LC22" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    - The name of the package to query</span></td>
      </tr>
      <tr>
        <td id="L23" class="blob-num js-line-number" data-line-number="23"></td>
        <td id="LC23" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    required: true</span></td>
      </tr>
      <tr>
        <td id="L24" class="blob-num js-line-number" data-line-number="24"></td>
        <td id="LC24" class="blob-code blob-code-inner js-file-line"><span class="pl-s">  state:</span></td>
      </tr>
      <tr>
        <td id="L25" class="blob-num js-line-number" data-line-number="25"></td>
        <td id="LC25" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    description:</span></td>
      </tr>
      <tr>
        <td id="L26" class="blob-num js-line-number" data-line-number="26"></td>
        <td id="LC26" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    - Whether the package is supposed to be installed or not</span></td>
      </tr>
      <tr>
        <td id="L27" class="blob-num js-line-number" data-line-number="27"></td>
        <td id="LC27" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    choices: [present, absent]</span></td>
      </tr>
      <tr>
        <td id="L28" class="blob-num js-line-number" data-line-number="28"></td>
        <td id="LC28" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    default: present</span></td>
      </tr>
      <tr>
        <td id="L29" class="blob-num js-line-number" data-line-number="29"></td>
        <td id="LC29" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L30" class="blob-num js-line-number" data-line-number="30"></td>
        <td id="LC30" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L31" class="blob-num js-line-number" data-line-number="31"></td>
        <td id="LC31" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">EXAMPLES</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L32" class="blob-num js-line-number" data-line-number="32"></td>
        <td id="LC32" class="blob-code blob-code-inner js-file-line"><span class="pl-s">- rpm_q: name=ansible state=present</span></td>
      </tr>
      <tr>
        <td id="L33" class="blob-num js-line-number" data-line-number="33"></td>
        <td id="LC33" class="blob-code blob-code-inner js-file-line"><span class="pl-s">- rpm_q: name=ansible state=absent</span></td>
      </tr>
      <tr>
        <td id="L34" class="blob-num js-line-number" data-line-number="34"></td>
        <td id="LC34" class="blob-code blob-code-inner js-file-line"><span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L35" class="blob-num js-line-number" data-line-number="35"></td>
        <td id="LC35" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L36" class="blob-num js-line-number" data-line-number="36"></td>
        <td id="LC36" class="blob-code blob-code-inner js-file-line"><span class="pl-c1">RPM_BINARY</span> <span class="pl-k">=</span> <span class="pl-s"><span class="pl-pds">&#39;</span>/bin/rpm<span class="pl-pds">&#39;</span></span></td>
      </tr>
      <tr>
        <td id="L37" class="blob-num js-line-number" data-line-number="37"></td>
        <td id="LC37" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L38" class="blob-num js-line-number" data-line-number="38"></td>
        <td id="LC38" class="blob-code blob-code-inner js-file-line"><span class="pl-k">def</span> <span class="pl-en">main</span>():</td>
      </tr>
      <tr>
        <td id="L39" class="blob-num js-line-number" data-line-number="39"></td>
        <td id="LC39" class="blob-code blob-code-inner js-file-line">    <span class="pl-s"><span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L40" class="blob-num js-line-number" data-line-number="40"></td>
        <td id="LC40" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    Checks rpm -q for the named package and returns the installed packages</span></td>
      </tr>
      <tr>
        <td id="L41" class="blob-num js-line-number" data-line-number="41"></td>
        <td id="LC41" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    or None if not installed.</span></td>
      </tr>
      <tr>
        <td id="L42" class="blob-num js-line-number" data-line-number="42"></td>
        <td id="LC42" class="blob-code blob-code-inner js-file-line"><span class="pl-s">    <span class="pl-pds">&quot;&quot;&quot;</span></span></td>
      </tr>
      <tr>
        <td id="L43" class="blob-num js-line-number" data-line-number="43"></td>
        <td id="LC43" class="blob-code blob-code-inner js-file-line">    module <span class="pl-k">=</span> AnsibleModule(</td>
      </tr>
      <tr>
        <td id="L44" class="blob-num js-line-number" data-line-number="44"></td>
        <td id="LC44" class="blob-code blob-code-inner js-file-line">        <span class="pl-v">argument_spec</span><span class="pl-k">=</span><span class="pl-c1">dict</span>(</td>
      </tr>
      <tr>
        <td id="L45" class="blob-num js-line-number" data-line-number="45"></td>
        <td id="LC45" class="blob-code blob-code-inner js-file-line">            <span class="pl-v">name</span><span class="pl-k">=</span><span class="pl-c1">dict</span>(<span class="pl-v">required</span><span class="pl-k">=</span><span class="pl-c1">True</span>),</td>
      </tr>
      <tr>
        <td id="L46" class="blob-num js-line-number" data-line-number="46"></td>
        <td id="LC46" class="blob-code blob-code-inner js-file-line">            <span class="pl-v">state</span><span class="pl-k">=</span><span class="pl-c1">dict</span>(<span class="pl-v">default</span><span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&#39;</span>present<span class="pl-pds">&#39;</span></span>, <span class="pl-v">choices</span><span class="pl-k">=</span>[<span class="pl-s"><span class="pl-pds">&#39;</span>present<span class="pl-pds">&#39;</span></span>, <span class="pl-s"><span class="pl-pds">&#39;</span>absent<span class="pl-pds">&#39;</span></span>])</td>
      </tr>
      <tr>
        <td id="L47" class="blob-num js-line-number" data-line-number="47"></td>
        <td id="LC47" class="blob-code blob-code-inner js-file-line">            ),</td>
      </tr>
      <tr>
        <td id="L48" class="blob-num js-line-number" data-line-number="48"></td>
        <td id="LC48" class="blob-code blob-code-inner js-file-line">        <span class="pl-v">supports_check_mode</span><span class="pl-k">=</span><span class="pl-c1">True</span></td>
      </tr>
      <tr>
        <td id="L49" class="blob-num js-line-number" data-line-number="49"></td>
        <td id="LC49" class="blob-code blob-code-inner js-file-line">    )</td>
      </tr>
      <tr>
        <td id="L50" class="blob-num js-line-number" data-line-number="50"></td>
        <td id="LC50" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L51" class="blob-num js-line-number" data-line-number="51"></td>
        <td id="LC51" class="blob-code blob-code-inner js-file-line">    name <span class="pl-k">=</span> module.params[<span class="pl-s"><span class="pl-pds">&#39;</span>name<span class="pl-pds">&#39;</span></span>]</td>
      </tr>
      <tr>
        <td id="L52" class="blob-num js-line-number" data-line-number="52"></td>
        <td id="LC52" class="blob-code blob-code-inner js-file-line">    state <span class="pl-k">=</span> module.params[<span class="pl-s"><span class="pl-pds">&#39;</span>state<span class="pl-pds">&#39;</span></span>]</td>
      </tr>
      <tr>
        <td id="L53" class="blob-num js-line-number" data-line-number="53"></td>
        <td id="LC53" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L54" class="blob-num js-line-number" data-line-number="54"></td>
        <td id="LC54" class="blob-code blob-code-inner js-file-line">    <span class="pl-c"># pylint: disable=invalid-name</span></td>
      </tr>
      <tr>
        <td id="L55" class="blob-num js-line-number" data-line-number="55"></td>
        <td id="LC55" class="blob-code blob-code-inner js-file-line">    rc, out, err <span class="pl-k">=</span> module.run_command([<span class="pl-c1">RPM_BINARY</span>, <span class="pl-s"><span class="pl-pds">&#39;</span>-q<span class="pl-pds">&#39;</span></span>, name])</td>
      </tr>
      <tr>
        <td id="L56" class="blob-num js-line-number" data-line-number="56"></td>
        <td id="LC56" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L57" class="blob-num js-line-number" data-line-number="57"></td>
        <td id="LC57" class="blob-code blob-code-inner js-file-line">    installed <span class="pl-k">=</span> out.rstrip(<span class="pl-s"><span class="pl-pds">&#39;</span><span class="pl-cce">\n</span><span class="pl-pds">&#39;</span></span>).split(<span class="pl-s"><span class="pl-pds">&#39;</span><span class="pl-cce">\n</span><span class="pl-pds">&#39;</span></span>)</td>
      </tr>
      <tr>
        <td id="L58" class="blob-num js-line-number" data-line-number="58"></td>
        <td id="LC58" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L59" class="blob-num js-line-number" data-line-number="59"></td>
        <td id="LC59" class="blob-code blob-code-inner js-file-line">    <span class="pl-k">if</span> rc <span class="pl-k">!=</span> <span class="pl-c1">0</span>:</td>
      </tr>
      <tr>
        <td id="L60" class="blob-num js-line-number" data-line-number="60"></td>
        <td id="LC60" class="blob-code blob-code-inner js-file-line">        <span class="pl-k">if</span> state <span class="pl-k">==</span> <span class="pl-s"><span class="pl-pds">&#39;</span>present<span class="pl-pds">&#39;</span></span>:</td>
      </tr>
      <tr>
        <td id="L61" class="blob-num js-line-number" data-line-number="61"></td>
        <td id="LC61" class="blob-code blob-code-inner js-file-line">            module.fail_json(<span class="pl-v">msg</span><span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&quot;</span><span class="pl-c1">%s</span> is not installed<span class="pl-pds">&quot;</span></span> <span class="pl-k">%</span> name, <span class="pl-v">stdout</span><span class="pl-k">=</span>out, <span class="pl-v">stderr</span><span class="pl-k">=</span>err, <span class="pl-v">rc</span><span class="pl-k">=</span>rc)</td>
      </tr>
      <tr>
        <td id="L62" class="blob-num js-line-number" data-line-number="62"></td>
        <td id="LC62" class="blob-code blob-code-inner js-file-line">        <span class="pl-k">else</span>:</td>
      </tr>
      <tr>
        <td id="L63" class="blob-num js-line-number" data-line-number="63"></td>
        <td id="LC63" class="blob-code blob-code-inner js-file-line">            module.exit_json(<span class="pl-v">changed</span><span class="pl-k">=</span><span class="pl-c1">False</span>)</td>
      </tr>
      <tr>
        <td id="L64" class="blob-num js-line-number" data-line-number="64"></td>
        <td id="LC64" class="blob-code blob-code-inner js-file-line">    <span class="pl-k">elif</span> state <span class="pl-k">==</span> <span class="pl-s"><span class="pl-pds">&#39;</span>present<span class="pl-pds">&#39;</span></span>:</td>
      </tr>
      <tr>
        <td id="L65" class="blob-num js-line-number" data-line-number="65"></td>
        <td id="LC65" class="blob-code blob-code-inner js-file-line">        module.exit_json(<span class="pl-v">changed</span><span class="pl-k">=</span><span class="pl-c1">False</span>, <span class="pl-v">installed_versions</span><span class="pl-k">=</span>installed)</td>
      </tr>
      <tr>
        <td id="L66" class="blob-num js-line-number" data-line-number="66"></td>
        <td id="LC66" class="blob-code blob-code-inner js-file-line">    <span class="pl-k">else</span>:</td>
      </tr>
      <tr>
        <td id="L67" class="blob-num js-line-number" data-line-number="67"></td>
        <td id="LC67" class="blob-code blob-code-inner js-file-line">        module.fail_json(<span class="pl-v">msg</span><span class="pl-k">=</span><span class="pl-s"><span class="pl-pds">&quot;</span><span class="pl-c1">%s</span> is installed<span class="pl-pds">&quot;</span></span>, <span class="pl-v">installed_versions</span><span class="pl-k">=</span>installed)</td>
      </tr>
      <tr>
        <td id="L68" class="blob-num js-line-number" data-line-number="68"></td>
        <td id="LC68" class="blob-code blob-code-inner js-file-line">
</td>
      </tr>
      <tr>
        <td id="L69" class="blob-num js-line-number" data-line-number="69"></td>
        <td id="LC69" class="blob-code blob-code-inner js-file-line"><span class="pl-k">if</span> <span class="pl-c1">__name__</span> <span class="pl-k">==</span> <span class="pl-s"><span class="pl-pds">&#39;</span>__main__<span class="pl-pds">&#39;</span></span>:</td>
      </tr>
      <tr>
        <td id="L70" class="blob-num js-line-number" data-line-number="70"></td>
        <td id="LC70" class="blob-code blob-code-inner js-file-line">    main()</td>
      </tr>
</table>

  </div>

</div>

<button type="button" data-facebox="#jump-to-line" data-facebox-class="linejump" data-hotkey="l" class="d-none">Jump to Line</button>
<div id="jump-to-line" style="display:none">
  <!-- </textarea> --><!-- '"` --><form accept-charset="UTF-8" action="" class="js-jump-to-line-form" method="get"><div style="margin:0;padding:0;display:inline"><input name="utf8" type="hidden" value="&#x2713;" /></div>
    <input class="form-control linejump-input js-jump-to-line-field" type="text" placeholder="Jump to line&hellip;" aria-label="Jump to line" autofocus>
    <button type="submit" class="btn">Go</button>
</form></div>

  </div>
  <div class="modal-backdrop js-touch-events"></div>
</div>


    </div>
  </div>

    </div>

        <div class="container site-footer-container">
  <div class="site-footer" role="contentinfo">
    <ul class="site-footer-links float-right">
        <li><a href="https://github.com/contact" data-ga-click="Footer, go to contact, text:contact">Contact GitHub</a></li>
      <li><a href="https://developer.github.com" data-ga-click="Footer, go to api, text:api">API</a></li>
      <li><a href="https://training.github.com" data-ga-click="Footer, go to training, text:training">Training</a></li>
      <li><a href="https://shop.github.com" data-ga-click="Footer, go to shop, text:shop">Shop</a></li>
        <li><a href="https://github.com/blog" data-ga-click="Footer, go to blog, text:blog">Blog</a></li>
        <li><a href="https://github.com/about" data-ga-click="Footer, go to about, text:about">About</a></li>

    </ul>

    <a href="https://github.com" aria-label="Homepage" class="site-footer-mark" title="GitHub">
      <svg aria-hidden="true" class="octicon octicon-mark-github" height="24" version="1.1" viewBox="0 0 16 16" width="24"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path></svg>
</a>
    <ul class="site-footer-links">
      <li>&copy; 2016 <span title="0.05330s from github-fe164-cp1-prd.iad.github.net">GitHub</span>, Inc.</li>
        <li><a href="https://github.com/site/terms" data-ga-click="Footer, go to terms, text:terms">Terms</a></li>
        <li><a href="https://github.com/site/privacy" data-ga-click="Footer, go to privacy, text:privacy">Privacy</a></li>
        <li><a href="https://github.com/security" data-ga-click="Footer, go to security, text:security">Security</a></li>
        <li><a href="https://status.github.com/" data-ga-click="Footer, go to status, text:status">Status</a></li>
        <li><a href="https://help.github.com" data-ga-click="Footer, go to help, text:help">Help</a></li>
    </ul>
  </div>
</div>



    

    <div id="ajax-error-message" class="ajax-error-message flash flash-error">
      <svg aria-hidden="true" class="octicon octicon-alert" height="16" version="1.1" viewBox="0 0 16 16" width="16"><path d="M8.865 1.52c-.18-.31-.51-.5-.87-.5s-.69.19-.87.5L.275 13.5c-.18.31-.18.69 0 1 .19.31.52.5.87.5h13.7c.36 0 .69-.19.86-.5.17-.31.18-.69.01-1L8.865 1.52zM8.995 13h-2v-2h2v2zm0-3h-2V6h2v4z"></path></svg>
      <button type="button" class="flash-close js-flash-close js-ajax-error-dismiss" aria-label="Dismiss error">
        <svg aria-hidden="true" class="octicon octicon-x" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M7.48 8l3.75 3.75-1.48 1.48L6 9.48l-3.75 3.75-1.48-1.48L4.52 8 .77 4.25l1.48-1.48L6 6.52l3.75-3.75 1.48 1.48z"></path></svg>
      </button>
      You can't perform that action at this time.
    </div>


      <script crossorigin="anonymous" src="https://assets-cdn.github.com/assets/compat-40e365359d1c4db1e36a55be458e60f2b7c24d58b5a00ae13398480e7ba768e0.js"></script>
      <script crossorigin="anonymous" src="https://assets-cdn.github.com/assets/frameworks-88471af1fec40ff9418efbe2ddd15b6896af8d772f8179004c254dffc25ea490.js"></script>
      <script async="async" crossorigin="anonymous" src="https://assets-cdn.github.com/assets/github-c4177fc28385bc04fc26a831fe1f9d69d5d7a3242566683a9daac147e1280847.js"></script>
      
      
      
      
      
      
    <div class="js-stale-session-flash stale-session-flash flash flash-warn flash-banner d-none">
      <svg aria-hidden="true" class="octicon octicon-alert" height="16" version="1.1" viewBox="0 0 16 16" width="16"><path d="M8.865 1.52c-.18-.31-.51-.5-.87-.5s-.69.19-.87.5L.275 13.5c-.18.31-.18.69 0 1 .19.31.52.5.87.5h13.7c.36 0 .69-.19.86-.5.17-.31.18-.69.01-1L8.865 1.52zM8.995 13h-2v-2h2v2zm0-3h-2V6h2v4z"></path></svg>
      <span class="signed-in-tab-flash">You signed in with another tab or window. <a href="">Reload</a> to refresh your session.</span>
      <span class="signed-out-tab-flash">You signed out in another tab or window. <a href="">Reload</a> to refresh your session.</span>
    </div>
    <div class="facebox" id="facebox" style="display:none;">
  <div class="facebox-popup">
    <div class="facebox-content" role="dialog" aria-labelledby="facebox-header" aria-describedby="facebox-description">
    </div>
    <button type="button" class="facebox-close js-facebox-close" aria-label="Close modal">
      <svg aria-hidden="true" class="octicon octicon-x" height="16" version="1.1" viewBox="0 0 12 16" width="12"><path d="M7.48 8l3.75 3.75-1.48 1.48L6 9.48l-3.75 3.75-1.48-1.48L4.52 8 .77 4.25l1.48-1.48L6 6.52l3.75-3.75 1.48 1.48z"></path></svg>
    </button>
  </div>
</div>

  </body>
</html>

