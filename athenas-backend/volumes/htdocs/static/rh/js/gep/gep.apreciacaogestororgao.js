Ext.ns('toolkit.gep');

toolkit.gep.ApreciacaoGestorOrgao = Ext.extend(
    toolkit.widget.TabPanel,
    {
        constructor: function(cfg){
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title:'Apreciação do Gestor',
                layout:'fit',
                items:this.getGrid(),
            });

            toolkit.gep.ApreciacaoGestorOrgao.superclass.constructor.call(this, cfg);

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
                        width: 100, 
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
                        width:60
                    },
                    {
                        dataIndex:'data_exercicio', 
                        header:'Data Exercicio', 
                        width:100
                    },
                    {
                        dataIndex:'ultima_avaliacao', 
                        header:'Última Avaliação', 
                        width:100
                    },
                    {
                        dataIndex:'media', 
                        header:'Média', 
                        width:100
                    },
                    {
                        dataIndex:'fim_estagio', 
                        header:'Fim do Estágio', 
                        width:100
                    },
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
                    'pk_estagio_servidor',
                    'pk_comissao',
                    'pk_questionario_manifestacao',
                    'pk_questionario',
                    'pk_cargo',
                    'pk_servidor',
                    'nome_servidor',
                    'cargo',
                    'data_exercicio',
                    'fim_estagio',
                    'ultima_avaliacao',
                    'media',
                    'status',
                    ],
                    url: toolkit.util.Normalize.controller_action('GEPDecisaoChefeOrgao','list'),
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
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('pk_questionario'),sel.get('pk_estagio_servidor')]);
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
                sel.get('pk_estagio_servidor'), 
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
                    'pk': sel.get('pk_estagio_servidor')
                }
            });
                
            return this.med;
        },

        visualizarManifestacao: function(){

            var sel = this.getSelModel().getSelected();
            if(sel) {
                var url = toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio','get_resposta_avaliacao',[sel.get('pk_questionario_manifestacao'),sel.get('pk_estagio_servidor')]);
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
                }, sel.get('pk_estagio_servidor'), url ).show();
            }
            else Ext.Msg.show({
                'title': 'Atenção',
                'msg': 'Selecione',
                'icon': Ext.Msg.WARNING,
                'buttons': Ext.Msg.OK
            });
        },

        _decisao_gestor: function() {
            var sel = this.getSelModel().getSelected();
            new toolkit.gep.DecisaoGestorForm({
                'action': 'decisao_gestor_orgao',
                'params': {
                    'pk_comissao_servidor': sel.get('pk')
                }, 
                'callback': {
                    'success': {
                        'scope': this,
                        'handler': function() {
                            this.getStore().reload()
                        }
                    }
                }
            }).show();
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
            }, sel.get('pk_servidor')).show();
        },

        getWindowApreciacao: function(){
            var sel = this.getSelModel().getSelected();
            this._apreciacao =  new toolkit.gep.Apreciacoes({ }).show();

            this._apreciacao.getStore().load(
                {
                    params:{
                        'pk_comissao': sel.get('pk_comissao'), 
                        'pk_estagio_servidor': sel.get('pk_estagio_servidor')
                    }
                }
            );
            
        },

        _print: function(){
            var sel = this.getSelModel().getSelected();
            new toolkit.widget.ExtReportBuild('GEPPrintAvaliacao', '/to/mpe/rh/estagio_probatorio/notas/rh_ep_main').runReport(
                '', {servidor: sel.get('pk_servidor'), cargo: sel.get('pk_cargo')}
            );
        },
       
        getToolbar: function(){
            if(!this.ToolBar) {
                this.act_decisao = new Ext.Action({
                        text: 'Decisão',
                        scope: this,
                        disabled: true,
                        iconCls: 'icon-gep-decisao', 
                        handler: this._decisao_gestor
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
                        menu:this.getSubReports()
                });

                var buttons = [
                new Ext.Button(this.act_decisao),
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
            ]

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
                    text: 'Apreciações da Comissão',
                    scope: this,
                    group: 'tipo',
                    filter: 'apreciacao',
                    icon: '/' + global.Context + '/static/images/edit.png',
                    handler: this.getWindowApreciacao
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

        _info: function(){
            var sel = this.getSelModel().getSelected();
            var scope= this;
            scope.getStoreInfo(sel.get('pk_estagio_servidor'));

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
                items: [
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Lotação</b>',
                    value: record.get('lotacao') || '',
                    name: 'lotacao'
                },
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Cargo</b>',
                    value: record.get('cargo') || '',
                    name: 'cargo'
                },
                {
                    xtype: 'displayfield',
                    labelAlign: 'top',
                    fieldLabel: '<b>Chefe Imediato</b>',
                    value: record.get('chefe_atual') || '',
                    name: 'chefe'
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
                'chefe_atual'
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
                    selecteds.push(item.data['pk_estagio_servidor']);
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
                                scope.act_decisao.enable(); 
                                scope.act_view.enable(); 
                                scope.act_print.enable();
                            } else {
                                scope.act_decisao.disable();
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
