<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
{%block head %}
<head> 
  {%block title %}
  <title>{{ title }}</title>
  {%endblock%}

  {%block page-meta %}
  <meta http-equiv="Content-ID" content="{{ content_id }}" />
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  {%endblock%}

  <link rel="stylesheet" href="/{{ rc.PATH }}.css" type="text/css" />

  <script type="text/javascript" src="/{{ rc.PATH }}.jquery-bundle.js"></script>
  <script type="text/javascript" src="/{{ rc.PATH }}.js"></script>

  <link ref="admin" href="/_ah/admin/" type="application/html+xml" />
  <meta name="Generator" content="Permascroll/{{ permascroll_version }}, Django/{{ django_version }}" />
</head>
{%endblock%}
<body> 
  <div class="page" id="{{ content_id }}">
  {%block header %}<div class="header"> {{ header }} <hr class="header" /> </div> {%endblock%}
  {%block contents %} 
      <h1 class="title">{{ title }}</h1>

      {{ contents }}

  {%endblock%}
  {%block footer %}<div class="footer"><hr class="footer" /> {{ footer }} </div> {%endblock%}
  {%block closure %}<div class="closure">{{ closure }} </div> {%endblock%}
  </div>
</body>
</html>
