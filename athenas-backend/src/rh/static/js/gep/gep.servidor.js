Ext.ns('toolkit.gep');

toolkit.gep.Servidor = Ext.extend(
    toolkit.widget.TabPanel,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Manifestação de Estágio Probatório',
                layout:'fit',
                items:this.getGrid(),
            });

            toolkit.gep.Servidor.superclass.constructor.call(this, cfg);
        },

        getStore: function() {
            if(!this._store)
            {
                this._store = new Ext.data.JsonStore({
                    autoLoad:true,
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                    'pk',
                    'pk_avaliacao', 
                    'questionario_pk', 
                    'questionario_manifestacao_pk', 
                    'questionario_manifestacao_servidor_pk',
                    'questionario_manifestacao',
                    'questionario_resposta_pk',
                    'cargo_id',
                    'questionario', 
                    'periodo_avaliado', 
                    'data_avaliacao', 
                    'status',
                    'situacao',
                    'avaliador', 
                    'servidor',
                    'servidor_pk',
                    'periodo_anterior'
                    ],
                    url: toolkit.util.Normalize.controller_action('GEPManifestacaoServidor','list'),
                    baseParams:{
                        start:0,
                        limit:50
                    },
                    scope:this
                });
            }
            return this._store;
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
                    autoExpandColumn: 'avaliador',
                    columns:[
                    this.getSelModel(),
                    {
                        header: "Status", 
                        sortable: false, 
                        dataIndex: "status", 
                        key: "status", 
                        width: 80, 
                        renderer: toolkit.util.formatStatus
                    },
                    {
                        dataIndex:'periodo_avaliado', 
                        header:'Período Avaliado', 
                        width:150
                    },
                    {
                        dataIndex:'data_avaliacao', 
                        header:'Data da Avaliação', 
                        width:200
                    },
                    {
                        dataIndex:'avaliador', 
                        header:'Avaliador', 
                        key:'avaliador',
                        id:'avaliador',
                        width:350
                    },
                    {
                        dataIndex:'situacao',
                        header:'Situação', 
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

        visualizarResposta: function(){
            var sel = this.getSelModel().getSelected();
            if(sel) {
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('questionario_pk'),sel.get('pk')]);
                new toolkit.questionario.VerResposta({
                    'title':'Avaliações de Estágio Probatório: ' + sel.get('servidor'),
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

        montarQuestionario: function() {
            var loading = new Ext.LoadMask(this.getGrid().getGridEl(), {
                msg:'Por favor aguarde...'
            });
            loading.show();
            var sel = this.getSelModel().getSelected();
            
            Ext.Ajax.request({
                'url': toolkit.util.Normalize.controller_action('GEPManifestacaoServidor', 'get_list_questionario', [sel.get('questionario_manifestacao_servidor_pk'),sel.get('pk')]),
                'params':{periodo:sel.get('periodo_avaliado')},
                'scope': this,
                'success': function(request) {
                    var obj = Ext.decode(request.responseText);
                    console.log(obj)
                    if(obj.collection.length>0) 
                    {
                        var montaQuestionario = new toolkit.questionario.MontaQuestionario({
                            'title': sel.get('questionario_manifestacao') + ': ' +  sel.get('servidor'),
                            'action': 'create',
                            'values':obj.collection,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { 
                                        this.getStore().reload(), 
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action('GEPManifestacaoServidor','save_manifestacao_estagio'),
                                            scope:this,
                                            params:{
                                                pk_gestor_estagio:sel.get('pk'),
                                                pk_questionario_resposta:montaQuestionario.retorno,
                                                pk_avaliacao_estagio: sel.get('pk_avaliacao')
                                            },
                                            success: function(request) {
                                                loading.hide();
                                                this.getStore().reload()
                                                var obj = Ext.decode(request.responseText);
                                                Ext.Msg.show({
                                                    'title': 'Estágio Probatório',
                                                    'icon': Ext.Msg.INFO,
                                                    'buttons': Ext.Msg.OK,
                                                    'msg': obj.message
                                                });
                                            },
                                            failure: function(response, opts) {
                                                console.log(opts.result.message)
                                                Ext.Msg.show({
                                                    'title': 'Questionário',
                                                    'msg': 'Erro!.',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                })
                                            }
                                        });
                                    }
                                }
                            }
                        }, obj.collection, sel.get('questionario_manifestacao'));
                        loading.hide();
                        montaQuestionario.show();
                    }else{
                        loading.hide();
                        console.log(obj.message);
                        Ext.Msg.show({
                            'title': 'Atenção!',
                            'msg': obj.message,
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                },
                'failure': function(request) {
                    // console.log(opts)
                    var obj = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        'title': 'Atenção!',
                        'msg': 'Erro ao exibir o questionário.',
                        'icon': Ext.Msg.WARNING,
                        'buttons': Ext.Msg.OK
                    });
                }
            })
           
        },

        montarQuestionarioAlteracao: function() {
            var loading = new Ext.LoadMask(this.getGrid().getGridEl(), {
                msg:'Por favor aguarde...'
            });
            loading.show();
            var sel = this.getSelModel().getSelected();
            
            Ext.Ajax.request({
                'url': toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'get_questionario_alteracao', [sel.get('questionario_manifestacao_servidor_pk'),sel.get('pk')]),
                'params':{tipo:2},
                'scope': this,
                'success': function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.collection.length>0) 
                    {
                        var montaQuestionarioAlteracao = new toolkit.gep.MontaQuestionarioAlteracao({
                            'title': sel.get('questionario_manifestacao') + ': ' +  sel.get('servidor'),
                            'action': 'update',
                            'values':obj.collection,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { 
                                        this.getStore().reload(), 
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action('GEPManifestacaoServidor','save_alteracao_manifestacao_estagio'),
                                            scope:this,
                                            params:{
                                                pk_gestor_estagio:sel.get('pk'),
                                                pk_questionario_resposta:montaQuestionarioAlteracao.retorno,
                                                pk_avaliacao_estagio: sel.get('pk_avaliacao')
                                            },
                                            success: function(response, opts) {
                                                loading.hide();
                                                this.getStore().reload()
                                                var obj = Ext.decode(response.responseText);
                                                Ext.Msg.show({
                                                    'title': 'Atenção!',
                                                    'msg': 'Alteração realizada com sucesso!',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                });
                                            },
                                            failure: function(response, opts) {
                                                console.log(opts.result.message)
                                                Ext.Msg.show({
                                                    'title': 'Questionário',
                                                    'message': 'Erro!.',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                })
                                            }
                                        });
                                    }
                                }
                            }
                        }, obj.collection, sel.get('questionario_manifestacao'));
                        loading.hide();
                        montaQuestionarioAlteracao.show();
                    }else{
                        loading.hide();
                        Ext.Msg.show({
                            'title': 'Atenção!',
                            'msg': obj.message,
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                },
                'failure': function(request) {
                    var obj = Ext.decode(request.responseText);
                    // console.log(obj)
                    Ext.Msg.show({
                        'title': 'Atenção!',
                        'msg': 'Erro ao exibir o questionário',
                        'icon': Ext.Msg.WARNING,
                        'buttons': Ext.Msg.OK
                    });
                }
            })
           
        },

        visualizarManifestacao: function(){

            var sel = this.getSelModel().getSelected();
            this._media = new toolkit.questionario.VerResposta({});

            if(sel.get('questionario_manifestacao_pk')!=null)
            {
                var visualizarResposta = new Ext.Window({
                    'title':sel.get('questionario_manifestacao'),
                    'width':500,
                    'height':500,
                    'modal': true,
                    'autoScroll':true,
                    'items':this._media.getTpl(),
                    'listeners': {
                        show:function(){
                            this._media.getStore().load({
                                params:{
                                    pk_questionario_resposta:sel.get('questionario_manifestacao_pk'), 
                                    pk_param: this.param
                                }
                            });
                        },
                        scope:this
                    }
                });
                visualizarResposta.show();
            }
            else{
                 Ext.Msg.show({
                    'title': 'Atenção!',
                    'msg': 'Não existe manifestação para esta avaliação.',
                    'icon': Ext.Msg.WARNING,
                    'buttons': Ext.Msg.OK
                });
            }

            return this.med;
        },

        _ciencia_decisao: function(){
            var sel = this.getSelModel().getSelected();
            if (sel){
                Ext.Ajax.request({
                    'url': toolkit.util.Normalize.controller_action('GEPManifestacaoServidor', 'ciencia_decisao_estagio'),
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
                            'title': 'Manifestação de Estágio',
                            'msg': obj.message,
                            'icon': icon,
                            'buttons': Ext.Msg.OK
                        });

                    },
                    'failure': function(request) {
                        var obj = Ext.decode(request.responseText);
                        log.debug(obj.message)
                        Ext.Msg.show({
                            'title': 'Manifestação de Estágio',
                            'msg': 'Ocorreu um erro ao tentar bloquear a etapa.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                });

            }else{
                Ext.Msg.show({
                    'title': 'Manifestação de Estágio',
                    'msg': 'Primeiro selecione um item.',
                    'icon': Ext.Msg.WARNING,
                    'buttons': Ext.Msg.OK
                });

            }
        },

        _print: function(){
            var sel = this.getSelModel().getSelected();
            console.debug(sel.get('servidor_pk'));
            console.debug(sel.get('cargo_id'));
            new toolkit.widget.ExtReportBuild('GEPPrintAvaliacao', '/to/mpe/rh/estagio_probatorio/notas/rh_ep_main').runReport(
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

        getSelModel: function(){
            if(!this.selModel){
                var scope= this;
                this.selModel = new Ext.grid.CheckboxSelectionModel({
                    listeners:{
                        selectionchange: function(sm) {
                            if (sm.getCount() && sm.getCount()==1) {
                                scope.act_view.enable();
                                scope.act_alter.enable();
                                scope.act_manifestacao.enable();
                                scope.act_print.enable();
                                scope.act_ciencia.enable();
                            } else {
                                scope.act_view.disable();
                                scope.act_alter.disable();
                                scope.act_manifestacao.disable();
                                scope.act_print.disable();
                                scope.act_ciencia.disable();
                            }
                        }
                    },
                });
            }
            return this.selModel;
        },

        getToolbar: function(){
            if(!this.ToolBar) {
                this.act_manifestacao = new Ext.Action({
                    text: 'Fazer Manifestação',
                    scope: this,
                    handler: this.montarQuestionario,
                    iconCls: true,
                    itemId: 'act_manifestacao',
                    icon: '/' + global.Context + '/static/images/accept.png',
                    disabled: true
                });
                this.act_alter = new Ext.Action({
                    text: 'Alterar Manifestação',
                    scope: this,
                    // handler: this.montarQuestionario,
                    handler: this.montarQuestionarioAlteracao,
                    iconCls: true,
                    itemId: 'act_alter',
                    icon: '/' + global.Context + '/static/images/document-sing.png',
                    disabled: true
                });
                this.act_visualizar = new Ext.Action({
                    text: 'Ver Avaliações',
                    scope: this,
                    handler: this.visualizarResposta,
                    iconCls: true,
                    itemId: 'act_visualizar',
                    icon: '/' + global.Context + '/static/images/document-validate.png',
                    disabled: true
                });
                this.act_visualizar_medias = new Ext.Action({
                    text: 'Ver Médias',
                    scope: this,
                    handler: this.visualizarMedias,
                    iconCls: true,
                    itemId: 'act_visualizar_medias',
                    icon: '/' + global.Context + '/static/images/document-validate.png',
                    disabled: true
                });
                this.act_view = new Ext.Action({
                        text: 'Visualizar',
                        scope: this,
                        disabled: true,
                        icon: '/' + global.Context + '/static/images/document-validate.png',
                        menu:this.getSubMenu()
                });

                this.act_print = new Ext.Action({
                        text: 'Relatórios',
                        scope: this,
                        disabled: true,
                        icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                        menu:this.getReports()
                });

                this.act_ciencia = new Ext.Action({
                        text: 'Ciência da decisão',
                        scope: this,
                        disabled: true,
                        icon: '/' + global.Context + '/static/rh/images/autorizado.png',
                        handler: this._ciencia_decisao
                });

                var buttons = [
                new Ext.Button(this.act_manifestacao),
                '-',
                new Ext.Button(this.act_alter),
                '-',
                new Ext.Button(this.act_ciencia),
                '-',
                new Ext.Button(this.act_view),
                '-',
                new Ext.Button(this.act_print),
                ];

                this.ToolBar = new Ext.Toolbar({
                    items: buttons,
                    scope:this
                });
            }
            return this.ToolBar;

        },

        getSubMenu: function(){
            return [
            {
                text: 'Avaliações',
                scope: this,
                group: 'tipo',
                filter: 'todos',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarResposta
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
                text: 'Manifestação',
                scope: this,
                group: 'tipo',
                filter: 'andamento',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarManifestacao
            }
            ]
        },

        getReports: function(){
            return [
            {
                text: 'Relatório Notas de Avaliação',
                scope: this,
                icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                handler: this._print
            },
             {
                text: 'Relatório de Avaliação',
                scope: this,
                icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                handler: this.getWindowReport
            },
            {
                text: 'Relatório Decisão Estágio',
                scope: this,
                icon: '/' + global.Context + '/static/rh/images/relatorios.png',
                handler: this._print_decisao_estagio
            },
            ]
        },

        _print_decisao_estagio: function(){
            var sel = this.getSelModel().getSelected();
            console.debug(sel.get('servidor_pk'));
            console.debug(sel.get('cargo_id'));
            new toolkit.widget.ExtReportBuild('GEPPrintDecisaoEstagio', '/to/mpe/rh/estagio_probatorio/especial/avaliacao/rh_ep_especial_avaliacao_main').runReport(
                '', {servidor: sel.get('servidor_pk'), cargo: sel.get('cargo_id')}
            );
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