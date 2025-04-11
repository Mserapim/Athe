Ext.ns('toolkit.gep');

toolkit.gep.GestorEstagio = Ext.extend(
    toolkit.widget.TabPanel,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Gestor de Estágio Probatório',
                layout:'fit',
                items:this.getGrid()
            });

            toolkit.gep.GestorEstagio.superclass.constructor.call(this, cfg);

        },

        getGrid: function(){
            if(!this._grid){
                this._grid = new toolkit.plugins.JsonGridPanel({
                    scope:this,
                    store: this.getStore(),
                    bbar: this.getPagingToolbar(),
                    searchable: true,
                    columnLines: true,
                    sm: this.getSelModel(),
                    autoExpandColumn: 'col_servidor',
                    // autoExpandColumn: 'col_servidor',
                    toSearch:[
                    {
                        dataIndex: 'servidor', 
                        header: 'Servidor', 
                        sortable: false, 
                        width: 250
                    }
                    ],
                    columns:[
                    new Ext.grid.RowNumberer(),
                    this.getSelModel(),
                    {
                        header: "Status", 
                        sortable: false, 
                        dataIndex: "status", 
                        key: "status", 
                        // id: "status",
                        width: 150, 
                        renderer: toolkit.util.formatStatus
                    },
                    {
                        dataIndex:'nome_servidor', 
                        header:'Servidor', 
                        key: "posse_servidor",
                        id: "col_servidor",
                        width:300
                    },
                    {
                        dataIndex:'cargo', 
                        header:'Cargo', 
                        width:40
                    },
                    {
                        dataIndex:'data_exercicio', 
                        header:'Data Exercício', 
                        width:80
                    },
                    {
                        dataIndex:'etapa_atual', 
                        header:'Etapa Atual', 
                        width:70
                    },
                    {
                        dataIndex:'ultima_avaliacao', 
                        header:'Última Avaliação', 
                        width:100
                    },
                    {
                        dataIndex:'media', 
                        header:'Média', 
                        width:50
                    },
                    {
                        dataIndex:'proxima_avaliacao', 
                        header:'Próxima Prevista', 
                        width:100
                    },
                    {
                        dataIndex:'prazos', 
                        header:'Prazos', 
                        width:70
                    },
                    {
                        dataIndex:'fim_estagio',
                        header:'Fim do Estágio', 
                        width:85,
                    }
                    ],
                    listeners: {
                        scope: this,
                        render: function(grid) {
                            new Ext.LoadMask(grid.getEl(), {
                                'store': grid.getStore(),
                                'msg': 'Carregando dados...'
                            });
                        }
                    }
                });
                var tbar= this._grid.getToolbar();
                tbar.insertButton(0, this.getToolbar());

            }
            return this._grid;
        },

        getStore: function() {
           
            if(!this._store)
            {
                this._store = new Ext.data.JsonStore({
                    autoLoad:true,
                    root: 'collection',
                    totalProperty: 'totalRows',
                    fields: [
                    'pk',
                    'posse_servidor', 
                    'posse_servidor_pk',
                    'servidor_pk',
                    'nome_servidor',
                    'cargo',
                    'cargo_id',
                    'etapa_atual',
                    'periodo_anterior',
                    'data_exercicio',
                    'media',
                    'ultima_avaliacao',
                    'proxima_avaliacao',
                    'prazos',
                    'status',
                    'questionario_pk',
                    'questionario_manifestacao_pk',
                    'questionario',
                    'bloqueada',
                    'estado',
                    'fim_estagio'
                    ],
                    url: toolkit.util.Normalize.controller_action('GEPGestorEstagio','list'),
                    baseParams:{
                        start:0,
                        limit:50
                    },
                    scope:this
                });
            }
            return this._store;
        },

        verResposta: function(){
            var sel = this.getSelModel().getSelected();
            if(sel) {
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('questionario_pk'),sel.get('pk')]);
                new toolkit.questionario.VerResposta({
                    'title': 'Avaliações de Estágio Probatório Servidor: ' + sel.get('nome_servidor'),
                    'callback': {
                        'success': {
                            'scope': this,
                            'handler': function() {
                                this.getStore().reload()
                            }
                        }
                    }
                }, 
                sel.get('pk'), 
                url ).show();
            }
            else Ext.Msg.show({
                'title': 'Atenção',
                'msg': 'Selecione',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });

        },

        visualizarMedias: function(){
            var sel = this.getSelModel().getSelected();

            this._media = new toolkit.gep.Medias({}).show();

            this._media.getStore().load({
                params:{
                    'pk': sel.get('pk')
                }
            });
                
            return this.med;
        },

        visualizarManifestacao: function(){

            var sel = this.getSelModel().getSelected();
            if(sel) {
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('questionario_manifestacao_pk'),sel.get('pk')]);
                new toolkit.questionario.VerResposta({
                    'title': 'Manifestação de Estágio Probatório: ' + sel.get('nome_servidor'),
                    'callback': {
                        'success': {
                            'scope': this,
                            'handler': function() {
                                this.getStore().reload()
                            }
                        }
                    }
                }, sel.get('pk'), url ).show();
            }
            else Ext.Msg.show({
                'title': 'Atenção',
                'msg': 'Selecione',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        finalizarEtapa: function(){

            var sel = this.getSelModel().getSelected();

            if(sel){
                Ext.Msg.show({
                    'title': 'Atenção',
                    'msg': 'Tem certeza que deseja finalizar esta etapa.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;
                
                        Ext.Ajax.request({
                            'url': toolkit.util.Normalize.controller_action('GEPGestorEstagio', 'finalizar_etapa'),
                            'params':{
                                pk:sel.get('pk'),
                                etapa:sel.get('etapa_atual')
                            },
                            'scope': this,
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) {
                                    var icon = Ext.Msg.INFO;
                                }else{
                                    var icon = Ext.Msg.WARNING;
                                }
                                this.getStore().reload()
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': obj.message,
                                    'icon': icon,
                                    'buttons': Ext.Msg.OK
                                });

                            },
                            'failure': function(request) {
                                var obj = Ext.decode(request.responseText);
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    // 'msg': 'Ocorreu um erro ao tentar finalizar a etapa.',
                                    'msg': obj.message,
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                    });
                    
            }
            else Ext.Msg.show({
                'title': 'Gestor de Estágio',
                'msg': 'Primeiro selecione um item.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        montarComissao: function(){
            var sel = this.getSelModel().getSelected();
            var pks = this.getSelectionIds();
            
            if(sel){
                Ext.Msg.show({
                    'title': 'Atenção',
                    'msg': 'Tem certeza que deseja montar a comissão.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;
                
                        Ext.Ajax.request({
                            'url': toolkit.util.Normalize.controller_action('GEPGestorEstagio', 'montar_comissao'),
                            'params':{
                                pks:pks,
                            },
                            'scope': this,
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) {
                                    var icon = Ext.Msg.INFO;
                                }else{
                                    var icon = Ext.Msg.WARNING;
                                }
                                this.getStore().reload()
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': obj.message,
                                    'icon': icon,
                                    'buttons': Ext.Msg.OK
                                });

                            },
                            'failure': function(request) {
                                var obj = Ext.decode(request.responseText);
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    // 'msg': 'Ocorreu um erro ao montar a comisão.',
                                    'msg': obj.message,
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        })
                    }
                    });
                    
            }
            else Ext.Msg.show({
                'title': 'Gestor de Estágio',
                'msg': 'Primeiro selecione um item.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        bloquearEtapa: function(){
            var sel = this.getSelModel().getSelected();
            if(sel) {
                Ext.Msg.show({
                    'title': 'Atenção',
                    'msg': 'Tem certeza que deseja bloquear esta etapa.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;
                        Ext.Ajax.request({
                            'url': toolkit.util.Normalize.controller_action('GEPGestorEstagio', 'bloquear_etapa'),
                            'params':{
                                pk:sel.get('pk')
                            },
                            'scope': this,
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) {
                                    var icon = Ext.Msg.INFO;
                                }else{
                                    var icon = Ext.Msg.WARNING;
                                }
                                this.getStore().reload()
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': obj.message,
                                    'icon': icon,
                                    'buttons': Ext.Msg.OK
                                });

                            },
                            'failure': function(request) {
                                var obj = Ext.decode(request.responseText);
                                log.debug(obj.message)
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': 'Ocorreu um erro ao tentar bloquear a etapa.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        });
                    }
                });
            }
            else Ext.Msg.show({
                'title': 'Gestor de Estágio',
                'msg': 'Primeiro selecione um item.',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });

        },

        desbloquearEtapa: function(){
            var sel = this.getSelModel().getSelected();
                Ext.Msg.show({
                    'title': 'Atenção',
                    'msg': 'Tem certeza que deseja desbloquear esta etapa.',
                    'icon': Ext.Msg.QUESTION,
                    'buttons': Ext.Msg.YESNO,
                    'scope': this,
                    'fn': function(b) {
                        if(b == 'no') return;
                        Ext.Ajax.request({
                            'url': toolkit.util.Normalize.controller_action('GEPGestorEstagio', 'desbloquear_etapa'),
                            'params':{
                                pk:sel.get('pk')
                            },
                            'scope': this,
                            'success': function(request) {
                                var obj = Ext.decode(request.responseText);
                                if(obj.success) {
                                    var icon = Ext.Msg.INFO;
                                }else{
                                    var icon = Ext.Msg.WARNING;
                                }
                                this.getStore().reload()
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': obj.message,
                                    'icon': icon,
                                    'buttons': Ext.Msg.OK
                                });

                            },
                            'failure': function(request) {
                                var obj = Ext.decode(request.responseText);
                                log.debug(obj.message)
                                Ext.Msg.show({
                                    'title': 'Gestor de Estágio',
                                    'msg': 'Ocorreu um erro ao tentar desbloquear a etapa.',
                                    'icon': Ext.Msg.WARNING,
                                    'buttons': Ext.Msg.OK
                                });
                            }
                        });
                    }
                });
        },

        finalizaProcesso: function(){
            var sel = this.getSelModel().getSelected();
            var pks = this.getSelectionIds();
            console.log(pks);
            Ext.Msg.show({
                'title': 'Atenção',
                'msg': 'Tem certeza que deseja finalizar.',
                'icon': Ext.Msg.QUESTION,
                'buttons': Ext.Msg.YESNO,
                'scope': this,
                'fn': function(b) {
                    if(b == 'no') return;
                    Ext.Ajax.request({
                        'url': toolkit.util.Normalize.controller_action('GEPGestorEstagio', 'finalizar_processo'),
                        'params':{
                            pks:pks,
                        },
                        'scope': this,
                        'success': function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success) {
                                var icon = Ext.Msg.INFO;
                            }else{
                                var icon = Ext.Msg.WARNING;
                            }
                            this.getStore().reload()
                            Ext.Msg.show({
                                'title': 'Gestor de Estágio',
                                'msg': obj.message,
                                'icon': icon,
                                'buttons': Ext.Msg.OK
                            });

                        },
                        'failure': function(request) {
                            var obj = Ext.decode(request.responseText);
                            log.debug(obj.message)
                            Ext.Msg.show({
                                'title': 'Gestor de Estágio',
                                'msg': 'Ocorreu um erro ao tentar finalizar.',
                                'icon': Ext.Msg.WARNING,
                                'buttons': Ext.Msg.OK
                            });
                        }
                    });
                }
            });

        },

        _print: function(){
            var sel = this.getSelModel().getSelected();
            console.debug(sel.get('servidor_pk'));
            console.debug(sel.get('cargo_id'));
            console.debug(sel.get('nome_servidor'));
            new toolkit.widget.ExtReportBuild('GEPPrintAvaliacao', '/to/mpe/rh/estagio_probatorio/notas/rh_ep_main').runReport(
                '', {servidor: sel.get('servidor_pk'), cargo: sel.get('cargo_id')}
            );
        },

        _print_decisao_estagio: function(){
            var sel = this.getSelModel().getSelected();
            console.debug(sel.get('servidor_pk'));
            console.debug(sel.get('cargo_id'));
            new toolkit.widget.ExtReportBuild('GEPPrintDecisaoEstagio', '/to/mpe/rh/estagio_probatorio/especial/avaliacao/rh_ep_especial_avaliacao_main').runReport(
                '', {servidor: sel.get('servidor_pk'), cargo: sel.get('cargo_id')}
            );
        },  

        getWindowReport: function(){
            var sel = this.getSelModel().getSelected();
            new toolkit.gep.ReportForm({
                'action': 'get_reports',
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                }
            }, sel.get('servidor_pk')).show();
        },

        notificarDivergencia: function(){
            var sel = this.getSelModel().getSelected();
            new toolkit.gep.Notificacao(
                {
                    servidor_id: sel.get('pk'),
                    servidor_nome: sel.get('nome_servidor'),
                    etapa_atual: sel.get('etapa_atual'),
                    callback: {
                        success: {
                            scope: this,
                            handler: function() {
                                this.getStore().reload()
                            }
                        }
                    }
                }
                
            ).show();
        },

        lancaNotaComissao: function(){
            var sel = this.getSelModel().getSelected();
            new toolkit.gep.NotaComissao(
                {
                    estagioprob_id: sel.get('pk'),
                    callback: {
                        success: {
                            scope: this,
                            handler: function() {
                                this.getStore().reload()
                            }
                        }
                    }
                }
            ).show();
        },

        getToolbar: function(){
            if(!this.ToolBar) {
                this.act_gerenciamento = new Ext.Action({
                        text: 'Gerenciamento',
                        scope: this,
                        // disabled: true,
                        iconCls: 'icon-progressoes icon-progressoes-config', 
                        menu:this.getSubGerenciamento()
                });
                this.act_view = new Ext.Action({
                        text: 'Visualizar',
                        scope: this,
                        disabled: true,
                        icon: '/' + global.Context + '/static/images/document-validate.png',
                        menu:this.getSubMenu()
                });
                this.act_filtro = new Ext.Action({
                        text: 'Filtros',
                        scope: this,
                        iconCls: 'icon-progressoes icon-progressoes-filter',
                        menu:this.getFilter()
                });
                this.act_order = new Ext.Action({
                        text: 'Ordenar por',
                        scope: this,
                        iconCls: 'icon-progressoes icon-progressoes-filter',
                        menu:this.getOrder()
                });

                this.act_print = new Ext.Action({
                        text: 'Relatórios',
                        scope: this,
                        disabled: true,
                        icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                        menu:this.getSubReports()
                });

                var buttons = [
                new Ext.Button(this.act_gerenciamento),
                '-',
                new Ext.Button(this.act_view),
                '-',
                new Ext.Button(this.act_print),
                '-',
                new Ext.Button(this.act_filtro),
                '-',
                 new Ext.Button(this.act_order),
      
                ];

                this.ToolBar = new Ext.Toolbar({
                    items: buttons,
                    scope:this
                });
            }
            return this.ToolBar;

        },

        getSubGerenciamento: function(){
            return [
                {
                    text: 'Finalizar Etapa',
                    scope: this,
                    group: 'tipo',
                    filter: 'todos',
                    iconCls: 'icon-progressoes icon-progressoes-update',
                    handler: this.finalizarEtapa
                },
                {
                    text: 'Bloquear',
                    scope: this,
                    group: 'tipo',
                    filter: 'bloquear',
                    icon: '/' + global.Context + '/static/rh/images/folha-fechada.png',
                    handler: this.bloquearEtapa
                },
                {
                    text: 'Desbloquear',
                    scope: this,
                    group: 'tipo',
                    filter: 'desbloquear',
                    icon: '/' + global.Context + '/static/rh/images/folha-aberta.png',
                    handler: this.desbloquearEtapa
                },
                {
                    text: 'Finalizar Processo',
                    scope: this,
                    group: 'tipo',
                    filter: 'finalizar_processo',
                    icon: '/' + global.Context + '/static/rh/images/liberar_ferias.png',
                    handler: this.finalizaProcesso
                },
                {
                    text: 'Montar Comissão',
                    scope: this,
                    group: 'tipo',
                    filter: 'montar_comissao',
                    icon: '/' + global.Context + '/static/rh/images/user_group.png',
                    handler: this.montarComissao
                },
                {
                    text: 'Notificar Discordância',
                    scope: this,
                    group: 'tipo',
                    filter: 'notificar_chefe',
                    icon: '/' + global.Context + '/static/rh/images/athenas-0197.png',
                    handler: this.notificarDivergencia
                },
                {
                    text: 'Nota da Comissão',
                    scope: this,
                    group: 'tipo',
                    filter: 'nota_comissao',
                    icon: '/' + global.Context + '/static/images/icons/calendar-plus.png',
                    handler: this.lancaNotaComissao
                }
            ]

        },

        getSubReports: function(){
            return [
                {
                    text: 'Relatório Notas de Avaliação',
                    scope: this,
                    group: 'tipo',
                    filter: 'todos',
                    icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                    handler: this._print
                },
                {
                    text: 'Relatório de Avaliação',
                    scope: this,
                    group: 'tipo',
                    filter: 'bloquear',
                    icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                    handler: this.getWindowReport
                },
                {
                    text: 'Relatório Decisão Estágio',
                    scope: this,
                    icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                    handler: this._print_decisao_estagio
                },
                /*{
                    text: 'Relatório de Manifestação Servidor',
                    scope: this,
                    group: 'tipo',
                    filter: 'desbloquear',
                    icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                    handler: this._print_manifestacao
                }*/
            ]

        },

        onStatusCheck: function(item, checked){
            // console.info(checked);
            if(checked){
                st = this.getStore();
                st.setBaseParam(item.group, item.filter);
                st.load();
                // st.reload();
            }
        },
                
        getSubMenu: function(){
            return [
            {
                text: 'Avaliações',
                scope: this,
                group: 'tipo',
                filter: 'todos',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.verResposta
            },
            {
                text: 'Médias',
                scope: this,
                group: 'tipo',
                filter: 'andamento',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarMedias
            },
            {
                text: 'Manifestações',
                scope: this,
                group: 'tipo',
                filter: 'andamento',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarManifestacao
            },
            {
                text: 'Informações do Servidor',
                scope: this,
                group: 'tipo',
                filter: 'andamento',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this._info
            }
            ]
        },

        getFilter: function(){
            return [
            {
                text: 'Todos',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'todos',
                handler: this.onStatusCheck
            },
            {
                text: 'Em Andamento',
                scope: this,
                checked: true,
                group: 'tipo',
                filter: 'andamento',
                handler: this.onStatusCheck
            },
            {
                text: 'Bloqueados',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'bloqueado',
                handler: this.onStatusCheck
            },
            {
                text: 'Finalizados',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'finalizado',
                handler: this.onStatusCheck
            },
            {
                text: 'Aguardando Finalização de Etapa',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'aguardando_finalizacao',
                handler: this.onStatusCheck
            },
            {
                text: 'Aguardando Comissão',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'aguardando_comissao',
                handler: this.onStatusCheck
            }
            ]
        },

        getOrder: function(){
            return [
            {
                text: 'Nome',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'order_name',
                handler: this.onStatusCheck
            },
            {
                text: 'Data da Estabilização',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'estabilizacao',
                handler: this.onStatusCheck
            },
            {
                text: 'Data da Avaliação',
                scope: this,
                checked: false,
                group: 'tipo',
                filter: 'andamento',
                handler: this.onStatusCheck
            },
            ]
        },

        _info: function(){
            var sel = this.getSelModel().getSelected();
            var scope= this;
            scope.getStoreInfo(sel.get('pk'));

        },
        
        getWindowInfo: function(record){
            return new Ext.Window({
                'title':'Servidor(a): '+record.data.nome_servidor,
                'width':450,
                'height':200,
                'modal': true,
                'autoScroll':true,
                'items':this.getInformation(record)
            });
        },

        getInformation: function(record){
            return [
            {
                xtype: 'fieldset',
                title: 'Informações do Servidor',
                layout: 'form',
                id: 'info_fieldset',
                // animCollapse: true,
                // collapsible: true,
                // labelWidth: 120,
                items: [
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Lotação</b>',
                    value: record.get('lotacao') || '',
                    // anchor: '45%',
                    name: 'lotacao'
                },
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Cargo</b>',
                    value: record.get('cargo') || '',
                    // anchor: '45%',
                    name: 'cargo'
                },
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Chefe Imediato</b>',
                    value: record.get('chefe_atual') || '',
                    // anchor: '45%',
                    name: 'chefe'
                },
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Período do Estágio</b>',
                    value: record.get('periodo_estagio') || '',
                    // anchor: '45%',
                    name: 'periodo_estagio'
                }
                ]
            }]
        },

        getStoreInfo: function(pk) {
            // if(!this._gStore){
            this._gStore = new Ext.data.JsonStore({
                autoLoad:true,
                root: 'collection',
                totalProperty: 'totalRows',
                fields: [
                'pk', 
                'posse_servidor', 
                'nome_servidor', 
                'lotacao', 
                'cargo',
                'chefe_atual',
                'periodo_estagio',
                ],
                url: toolkit.util.Normalize.controller_action('GEPGestorEstagio','get_information'),
                scope:this,
                baseParams:{
                    servidor:pk
                },
                listeners:{
                    load: function(cmp,records){
                        // console.log(records)
                        this.getWindowInfo(records[0]).show();
                    },
                    scope: this
                }
            });
            // }
            return this._gStore;
        },

        getSelectionIds: function(){
            var sm = this.getSelModel();
            var selecteds = []
            Ext.each(
                sm.getSelections(), 
                function(item, idx, all){
                    selecteds.push(item.data['pk']);
                },
                this
                )                    
            // console.debug(selecteds);
            return selecteds;
        },

        getSelModel: function(){
            if(!this.selModel){
                var scope= this;
                this.selModel = new Ext.grid.CheckboxSelectionModel({
                    listeners:{
                        selectionchange: function(sm) {
                            scope.getSelectionIds();

                            if (sm.getCount() && sm.getCount()==1) {
                                // scope.act_gerenciamento.enable();
                                scope.act_view.enable(); 
                                scope.act_print.enable();
                            } else {
                                // scope.act_gerenciamento.disable();
                                scope.act_view.disable();
                                scope.act_print.disable();
                            }
                        }
                    },
                });
            }
            return this.selModel;
        },

        reload: function(){
            this.getStore().reload();
        },

        getPagingToolbar: function() {
            if(!this._pagingToolbar)
            {
                this._pagingToolbar = new Ext.PagingToolbar({
                    style: 'border-right:none',
                    store: this.getStore(),
                    displayInformation: true,
                    pageSize: 50,
                    prependButtons: true
                });
            }
        
            return this._pagingToolbar;
        },

    }
    );
