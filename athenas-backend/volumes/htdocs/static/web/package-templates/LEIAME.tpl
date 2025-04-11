#INSTALAÇÃO DE APLICATIVO WEB

ATENÇÃO: Para evitar problemas no momento da instalação (deploy) siga todas as instruções abaixo.

1.  No servidor web, no ambiente de homologação, em /home/web/homologa (cd /home/web/homologa), adicione a
    pasta {{app_name}} contida neste pacote zip.

2.  Em seguida, no arquivo settings.py do ambiente de homologação existe uma variável chamada INSTALLED_APPS
    que contém a lista de aplicativos habilitados. Adicione o trecho de código a seguir à lista de aplicativos
    habilitados para habilitar este aplicativo.

        '{{app_name}}',

    A variável INSTALLED_APPS estará semelhante ao código a seguir após a adição do trecho acima:

        INSTALLED_APPS = (
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'default',
            'concursos',
            'clipping',
            'caop_meio_ambiente',
            'caop_cidadania',
            'caop_patrimonio_publico',
            'caop_mulher',
            'obras',
            'cpl',
            'passeio_ciclistico',
            'portal',
            'cesaf',
            'south',
            'django_extensions',
            {{app_name}},
        )

3.  Ainda no ambiente de homologação, procure pelo arquivo urls.py. Na variável urlpatterns adicione o trecho a seguir
    na lista de rotas:

        (r'^{{app_slug}}/?', include('{{app_name}}.urls')),

    Após a adição do trecho acima, a variável urlpatterns se parecerá com isto:

        urlpatterns = patterns('',
            (r'^manutencao/?$', 'manutencao.views.index'),
            (r'^admin/', include(admin.site.urls)),
            (r'^clipping/?', include('clipping.urls')),
            (r'^concursos/?', include('concursos.urls')),
            (r'^obras/?', include('obras.urls')),
            (r'^passeio-ciclistico/?', include('passeio_ciclistico.urls')),
            (r'^caops/cidadania/?', include('caop_cidadania.urls')),
            (r'^caops/patrimonio-publico/?', include('caop_patrimonio_publico.urls')),
            (r'^caops/mulher/?', include('caop_mulher.urls')),
            (r'^caops/meio-ambiente/?', include('caop_meio_ambiente.urls')),
            (r'^cpl/?', include('cpl.urls')),
            (r'^portal/?', include('portal.urls')),
            (r'^cesaf/?', include('cesaf.urls')),
            (r'^site-manager/?', include('site_manager.urls')),
            (r'^{{app_slug}}/?', include('{{app_name}}.urls')),

            (r'', include('default.urls'))
            #(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': sets.MEDIA_ROOT, 'show_indexes': True})
        )

4.  Neste momento sua aplicação já estará instalada e pronta para ser testada, para realizar o teste execute o comando:

        sudo reload-web.sh

    E depois abra o navegador no endereço http://h-site.mp.to.gov.be/web/{{app_slug}}/ e navegue no
    no aplicativo para constatar se esta funcionando corretamente.

    Caso seja apresentado algum problema relate-o ao Webmaster através do email webmaster@mp.to.gov.br.
    Caso não apresente problema, prossiga este tutorial.

    ATENÇÃO: NUNCA, em hipótese alguma, prossiga este tutorial se ocorrer algum erro na aplicação.

5.  Em seguida, execute os seguintes comandos para colocar sob versionamento este aplicativo:

        hg add {{app_name}}/
        hg ci {{app_name}}/ urls.py -m 'Adicionando aplicativo {{app_name}} sob versionamento'
        hg pull
        hg up

    Caso tenha gerado mais de uma cabeça (heads) de versionamento execute:
        hg merge
        hg ci -m 'Auto merge'

    Certifique-se que as cabeças foram unificadas
        hg heads

    Você saberá se as cabeças foram unificadas se aparecer apenas um conjunto de modificaçoes (changeset),
    algo parecido com isso:

        changeset:   205:b3f861740719
        tag:         tip
        user:        tony
        date:        Mon May 16 08:48:25 2011 -0300
        summary:     Adicionando aplicativo {{app_name}} sob versionamento

    E por último, enviar as modificações para o servidor de versionamento:
        hg push

6.  No ambiente de produção, em /home/web/producao (cd /home/web/producao), excecute:
        hg pull
        hg up

7.  Acesse o gestor de conteúdo no ambiente de produção, crie um site com o mesmo nome e titulo do que foi criado no
    ambiente de homologação marque a opção "criar site base".

    ATENÇÃO: Não é necessário fazer download do pacote, pois os fontes do novo aplicativo já foram criados no passo 6.

7.  Repita o passo 2 no ambiente de produção.

8.  Execute:
    sudo reload-web.sh

9.  Acesse o novo aplicativo no ambiente de produção em http://www.mp.to.gov.br/web/{{app_slug}}/
    para constatar o normal funcionamento

