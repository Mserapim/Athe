{% extends  'template.tpl' %}

{% block css %}
<style>
    *
    { font-family: Helvetica; }

    body
    { background: #f6f6f6; }

    .default-link {
        font-weight: bold;
        color: #1974a8;
    }

    .login-box
    {
        max-width: 350px;
        display: table;
        position: absolute;
        left: 50%;
        top: 50%;
        transform: translate(-50%, -50%);
        border: 1px solid #dfdfdf;
        padding: 3px;
        background: #fff;
        box-shadow: 0px 0px 5px 0px #ccc;
    }

    .errorlist li
    { font-size: 13px; color: #cc5252; margin: 0 0 2px 1px; font-weight: bold; }

    header
    { background: #1974a8 url(/athenas/static/images/top.png) repeat-x ; }

    header h1
    {
        background: url("/athenas/static/images/{{ imgs_name_default.logomarca_name_default }}") no-repeat center;
        color: #fff;
        display: block;
        float: left;
        font-family: 'Default' !important;
        text-indent: -9999px;
    }

    form *
    { color: #777; }

    form p
    { margin-bottom: 10px; }

    form label
    { display: block; }

    form input:not([type=submit])
    { width: 96.5%; }

    footer
    { background: #1974a8; }

    footer small
    { color: #fff; font-size: 11px; }

    .button-place
    { border-top: 1px solid #ddd; }

    .button
    { height: auto; }

</style>
{% endblock %}

{% block content %}
    <div class="login-box">
        <header class="table stretch">
            <h1 class="stretch">Portal do servidor</h1>
        </header>

        <form class="pad" action="/{{CONTEXT}}/Application/login/" method="POST" onSubmit="storeTheme()">
            {{form.as_p}}

            <div class="button-place pad-top text-center">
                <input type="submit" value="Logar" class="standard quarter">
            </div>
        </form>
        <footer class="pad text-center">
            <small class="">Seja bem vindo(a) ao Novo Sistema de Gestão de Pessoas e Vida Funcional do MPMT. Em caso de dúvidas entre em contato com o suporte através do telefone (65) 3613-5158 ou pelo e-mail dgp@mpmt.mp.br</small>
        </footer>
    </div>

{% endblock %}

{% block js %}

    <script>
        var themeField = document.querySelector('#id_theme')

        function center(width, height)
        {
            let left = (parseInt(getComputedStyle(document.body).width) / 2) - (width / 2),
                top = (document.firstElementChild.clientHeight / 2) - (height / 2);

            return [left, top];
        }

        function storeTheme() {
            localStorage.setItem('selectedTheme', themeField.value)
        }

        themeField.value = localStorage.getItem('selectedTheme') || 0;

        document.querySelectorAll('#change-pwd,#recovery-pwd')
            .forEach(function(el) {
                el.addEventListener('click', (event) => {
                    event.preventDefault();

                    let width = Number.parseInt((el.attributes['data-width'] || {}).value || '500'),
                        height = Number.parseInt((el.attributes['data-height'] || {}).value || '500'),
                        xy = center(width, height),
                        specs = 'width=' + width + ',height=' + height + ',left=' + xy[0] + ',top=' + xy[1];

                    open(event.target.href, '_blank', specs);
                });
            });
    </script>

    {% for module in js %}
        <script src="{{module}}" async></script>
    {% endfor %}
{% endblock %}
