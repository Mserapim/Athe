<!DOCTYPE html>
<html lang="pt-br">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1, maximum-scale=1">

        <title>eGov para {{ APPLICATION_TITLE }}</title>

        <link rel="stylesheet" href="/{{CONTEXT}}/static/css/ez-styles.css" media="all">
        {% block css %}{% endblock %}

        <link rel="shortcut icon" href="/{{CONTEXT}}/static/images/{{ imgs_name_default.favicon_name_default }}">
    </head>
    <body>
        {% block content %}
        {% endblock %}

        {% block js %}
        {% endblock %}
    </body>
</html>