Ext.ns('toolkit.gep');

toolkit.gep.GestorEstagioAdmin = Ext.extend(
    toolkit.widget.TabPanel,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Avaliação de Estágio Probatório',
                layout:'fit',
                items:this.getGrid(),
            });

            toolkit.gep.GestorEstagioAdmin.superclass.constructor.call(this, cfg);

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
                    'data_exercicio',
                    'media',
                    'ultima_avaliacao',
                    'proxima_avaliacao',
                    'questionario_pk',
                    'questionario_manifestacao_pk',
                    'questionario',
                    'prazos',
                    'status',
                    'bloqueada',
                    'periodo_anterior',
                    'estado'
                    ],
                    url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','list'),
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
                    autoExpandColumn: 'col_servidor',
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
                        width: 85, 
                        renderer: toolkit.util.formatStatus
                    },
                    {
                        dataIndex:'nome_servidor', 
                        header:'Servidor', 
                        key: "posse_servidor",
                        id: "col_servidor",
                        width:285
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
                        width:45
                    },
                    {
                        dataIndex:'proxima_avaliacao', 
                        header:'Próxima Prevista', 
                        width:100
                    },
                    {
                        dataIndex:'prazos', 
                        header:'Prazos', 
                        width:60
                    },
                    {
                        dataIndex:'estado',
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

        montarQuestionario: function() {
            var loading = new Ext.LoadMask(this.getGrid().getGridEl(), {
                msg:'Por favor aguarde...'
            });
            loading.show();
            var sel = this.getSelModel().getSelected();
            
            Ext.Ajax.request({
                'url': toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'get_list_questionario', [sel.get('questionario_pk'),sel.get('pk')]),
                'params':{periodo:sel.get('periodo_avaliado')},
                'scope': this,
                'success': function(request) {
                    var obj = Ext.decode(request.responseText);
                    console.log(obj.collection);
                    if(obj.collection.length>0) 
                    {
                        var montaQuestionario = new toolkit.questionario.MontaQuestionario({
                            'title':sel.get('questionario'),
                            'action': 'create',
                            'values':obj.collection,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { 
                                        // this.getStore().reload(); 
                                        Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','save_avaliacao_estagio'),
                                            scope:this,
                                            params:{
                                                pk_gestor_estagio: sel.get('pk'),
                                                pk_questionario_resposta:montaQuestionario.retorno
                                            },
                                            'success': function(request) {
                                                var obj = Ext.decode(request.responseText);
                                                // if(obj.success) 
                                                //     this.getGridCidades().getStore().reload();
                                                // else
                                                loading.hide();
                                                this.getStore().reload();
                                                Ext.Msg.show({
                                                    'title': 'Estágio Probatório',
                                                    'icon': Ext.Msg.INFO,
                                                    'buttons': Ext.Msg.OK,
                                                    'msg': obj.message
                                                });
                                            },
                                            failure: function(response, opts) {
                                                console.log(opts.result.message)
                                                // console.log('server-side failure with status code ' + response.status);

                                                Ext.Msg.show({
                                                    'title': 'Atenção!',
                                                    'msg': 'Erro ao salvar os dados',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                });
                                            }
                                        });
                                        this.getStore().reload();
                                    }
                                }
                            }
                        }, obj.collection, sel.get('questionario'));
                        loading.hide();
                        montaQuestionario.show();
                    }else{
                        loading.hide();
                        Ext.Msg.show({
                            'title': 'Atenção!',
                            'msg': obj.message,
                            // 'msg': 'Ocorreu um erro ao exibir o formulário.',
                            'icon': Ext.Msg.WARNING,
                            'buttons': Ext.Msg.OK
                        });
                    }
                },
                'failure': function(request) {
                    // console.log(opts)
                    var obj = Ext.decode(request.responseText);
                    console.log(obj)
                    Ext.Msg.show({
                        'title': 'Atenção!',
                        'msg': 'Erro ao exibir o questionário',
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
                'url': toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'get_questionario_alteracao', [sel.get('questionario_pk'),sel.get('pk')]),
                'params':{tipo:1},
                'scope': this,
                'success': function(request) {
                    var obj = Ext.decode(request.responseText);
                    if(obj.collection.length>0) 
                    {
                        var montaQuestionarioAlteracao = new toolkit.gep.MontaQuestionarioAlteracao({
                            'title':sel.get('questionario'),
                            'action': 'update',
                            'values':obj.collection,
                            'callback': {
                                'success': {
                                    'scope': this,
                                    'handler': function() { 
                                        this.getStore().reload(), 
                                         Ext.Ajax.request({
                                            url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','save_alteracao_avaliacao_estagio'),
                                            scope:this,
                                            params:{
                                                pk_gestor_estagio: sel.get('pk'),
                                                pk_questionario_resposta:montaQuestionarioAlteracao.retorno
                                            },
                                            success: function(response, opts) {
                                                loading.hide();
                                                this.getStore().reload();
                                                var obj = Ext.decode(response.responseText);
                                                Ext.Msg.show({
                                                    'title': 'Atenção!',
                                                    'msg': 'Alteração realizada com sucesso!',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                });
                                            },
                                            failure: function(response, opts) {
                                                // console.log(opts.result.message)
                                                // console.log('server-side failure with status code ' + response.status);
                                                Ext.Msg.show({
                                                    'title': 'Atenção!',
                                                    'msg': 'Erro ao exibir o questionário',
                                                    'icon': Ext.Msg.WARNING,
                                                    'buttons': Ext.Msg.OK
                                                });
                                            }
                                        });
                                    }
                                }
                            }
                        }, obj.collection, sel.get('questionario'));
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
                    // console.log(opts)
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

        visualizarResposta: function(){
            var sel = this.getSelModel().getSelected();
            if(sel) {
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('questionario_pk'),sel.get('pk')]);
                new toolkit.questionario.VerResposta({
                    'title':'Avaliações de Estágio Probatório: ' + sel.get('nome_servidor'),
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

        _print: function(){
            var sel = this.getSelModel().getSelected();
            console.debug(sel.get('servidor_pk'));
            console.debug(sel.get('cargo_id'));
            new toolkit.widget.ExtReportBuild('GEPPrintAvaliacao', '/to/mpe/rh/estagio_probatorio/notas/rh_ep_main').runReport(
                '', {servidor: sel.get('servidor_pk'), cargo: sel.get('cargo_id')}
            );
        },


        getToolbar: function(){
            if(!this.ToolBar) {
                this.act_novo = new Ext.Action({
                    text: 'Avaliar',
                    scope: this,
                    handler: this.montarQuestionario,
                    // handler: this.montarQuestionarioAlteracao,
                    iconCls: true,
                    itemId: 'act_novo',
                    icon: '/' + global.Context + '/static/images/accept.png',
                    disabled: true
                });
                this.act_alter = new Ext.Action({
                    text: 'Alterar Avaliação',
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
                        // handler: this._print
                });
            
                var buttons = [
                new Ext.Button(this.act_novo),
                '-',
                new Ext.Button(this.act_alter),
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
                text: 'Manifestação',
                scope: this,
                group: 'tipo',
                filter: 'todos',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarManifestacao
            },
            {
                text: 'Médias',
                scope: this,
                group: 'tipo',
                filter: 'andamento',
                icon: '/' + global.Context + '/static/images/edit.png',
                handler: this.visualizarMedias
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
 
            ]
        },

         getSelModel: function(){
            if(!this.selModel){
                var scope= this;
                this.selModel = new Ext.grid.CheckboxSelectionModel({
                    listeners:{
                        selectionchange: function(sm) {
                            if (sm.getCount() && sm.getCount()==1) {
                                scope.act_view.enable();
                                scope.act_novo.enable();
                                scope.act_alter.enable();
                                scope.act_print.enable();
                            } else {
                                scope.act_view.disable();
                                scope.act_novo.disable();
                                scope.act_alter.disable();
                                scope.act_print.disable();
                            }
                        }
                    },
                });
            }
            return this.selModel;
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
