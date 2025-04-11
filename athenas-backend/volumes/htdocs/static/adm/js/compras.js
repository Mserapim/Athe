
if(typeof(toolkit.adm.compras) == 'undefined') {

    Ext.ns('toolkit.adm.compras');

    toolkit.adm.compras.NotaDotacao = Ext.extend(
        Ext.Window,
        {
            getGridPanel: function() {
                if(!this.gridPanel) {
                    this.gridPanel = new toolkit.plugins.JsonGridPanel({
                        region: 'center',
                        border: false,
                        cm: new Ext.grid.ColumnModel([
                            {dataIndex: 'id',header: 'Chave',sortable: true,width: 75},
                            {dataIndex: 'numero',header: 'Número',sortable: true,width: 100, toSearch: true},
                            {dataIndex: 'programa_trabalho',header: 'Programa',sortable: true,width: 80, toSearch: true},
                            {dataIndex: 'fonte_recurso',header: 'Fonte',sortable: true,width: 80, toSearch: true},
                            {dataIndex: 'natureza_despesa',header: 'Nat. Despesa',sortable: true,width: 100, toSearch: true},
                            {dataIndex: 'valor',header: 'Valor',sortable: true,width: 80,renderer: toolkit.util.formatCurrency}
                        ]),
                        searchable: true,
                        toSearch: [
                            {dataIndex: 'numero', header: 'Número'},
                            {dataIndex: 'programa_trabalho', header: 'Programa'},
                            {dataIndex: 'fonte_recurso', header: 'Fonte'},
                            {dataIndex: 'natureza_despesa', header: 'Nat. Despesa'}
                        ],
                        store: new Ext.data.JsonStore({
                            url: toolkit.util.Normalize.controller_action(
                                'COMPRASNotaDotacao',
                                'query'
                            ),
                            fields: [
                                'id', 'numero', 'programa_trabalho',
                                'fonte_recurso', 'natureza_despesa', 'valor'
                            ],
                            baseParams: {limit: 50,start: 0},
                            root: 'result',
                            totalProperty: 'totalRows',
                            autoLoad: true
                        })
                    });
                }
                return this.gridPanel;
            },

            createND: function()  {
                var obj = this;
                var father = {
                    reload_grid: function() { obj.getGridPanel().getStore().reload() },
                    controller: 'COMPRASNotaDotacao'
                }
                new toolkit.widget.ExtCrudForm(father,1).show();
            },

            editND: function() {
                var selection = this.getGridPanel().getSelectionModel().getSelected();
                if(selection) {
                    var obj = this;
                    var father = {
                        reload_grid: function() { obj.getGridPanel().getStore().reload() },
                        controller: 'COMPRASNotaDotacao'
                    };
                    new toolkit.widget.ExtCrudForm(father,2,selection.get('id')).show();
                }
                else alert('Primeiro selecione um item para edição.');
            },

            removeND: function()  {
                var selection = this.getGridPanel().getSelectionModel().getSelected();
                if(selection) {
                    Ext.Msg.show({
                        title: 'Remover ND',
                        msg: 'Tem certeza que deseja remover a ND selecionada?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(button) {
                            button == 'yes' && Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'COMPRASNotaDotacao',
                                    'commit',
                                    ['DELETE', selection.get('id')]
                                ),
                                success: function() {
                                    this.getGridPanel().getStore().reload();
                                    this.destroy();
                                },
                                failure: function() {alert('Ocorreu um problema tentando remover a ND.');},
                                scope: true
                            });
                        }
                    })
                }
                else alert('Primeiro selecione um item para remoção.');
            },

            select: function()  {
                var selection = this.getGridPanel().getSelectionModel().getSelections();
                var nds = [];

                if(selection) {
                    Ext.each(selection, function(nd) { nds.push(nd.json.pk) });
                    Ext.Ajax.request({
                        url: toolkit.util.Normalize.controller_action(
                            'COMPRASProcessoAquisicao',
                            'set_nd'
                        ),
                        params: {items: this.conf.produtos,nd: nds},
                        success: function(request) {
                            var obj = Ext.decode(request.responseText);
                            if(obj.success) {
                                if(this.conf.scope) {
                                    this.conf.scope.__swap__ = this.conf.trigger;
                                    this.conf.scope.__swap__();
                                    this.conf.scope.__swap__ = null;
                                }
                                else if(this.conf.trigger) this.conf.trigger();
                                this.destroy();
                            }
                            else alert('Ocorreram erros tentando associar a ND aos produtos.');
                        },
                        failure: function() {alert('Ocorreu um erro tenando associar os produtos a ND.')},
                        scope: this
                    });
                }
                else alert('Primeiro selecione uma ND para ser aplicada aos itens.')
            },

            constructor: function(conf) {
                var cf = {
                    layout: 'border',
                    title: 'Gestor de ND\'s',
                    modal: true,
                    closable: true,
                    resizable: false,
                    width: 550,
                    height: 425,
                    conf: conf,
                    buttonAlign: 'center',
                    buttons: [
                        {text: 'Selecionar',scope: this,handler: this.select},
                        {text: 'Novo',handler: this.createND,scope: this},
                        {text: 'Editar',handler: this.editND,scope: this},
                        {text: 'Remover',handler: this.removeND,scope: this},
                        {text: 'Cancelar',scope: this,handler: this.destroy}
                    ],
                    items: this.getGridPanel()
                };

                toolkit.adm.compras.NotaDotacao.superclass.constructor.call(this, cf);
            }
        }
    );

    toolkit.adm.compras.ProdutoProcessoAquisicao = Ext.extend(
        Ext.Window,
        {
            getFormPanel: function() {
                if(!this.formPanel) {
                    this.formPanel = new Ext.form.FormPanel({
                        frame: true,
                        border: false,
                        labelWidth: 150,
                        defaults: {width: 360},
                        items: [
                            {
                                xtype: 'rest-autocompletefield',
                                fieldLabel: "Produto",
                                allowBlank: false,
                                rest: "adm.accounting.product.Restful",
                                name: "produto",
                                value: this.conf.values ? this.conf.values.produto_pk : undefined
                            },
                            {
                                xtype: 'numberfield',
                                fieldLabel: 'Quantidade',
                                allowNegative: false,
                                allowDecimals: true,
                                decimalPrecision: 3,
                                decimalSeparator: ',',
                                name: 'quantidade',
                                value: this.conf.values ? this.conf.values.qnt : undefined
                            },
                            {
                                xtype: 'numberfield',
                                fieldLabel: 'Valor unitário estimado',
                                allowNegative: false,
                                allowDecimals: true,
                                decimalPrecision: 2,
                                decimalSeparator: ',',
                                name: 'valor_unitario_estimado',
                                value: this.conf.values ? this.conf.values.valor_estimado_unitario : undefined
                            },
                            {
                                xtype: 'xhtmleditor',
                                fieldLabel: 'Descrição',
                                name: 'descricao',
                                value: this.conf.values ? this.conf.values.descricao : undefined
                            }
                        ]
                    });
                }

                return this.formPanel
            },

            commit: function() {
                var form = this.getFormPanel().getForm();
                form.waitMsgTarget = this.getEl();

                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        'COMPRASProcessoAquisicao',
                        this.conf.values.pk ? 'update_item' : 'add_item'
                    ),
                    params: {
                        processo_aquisicao: this.conf.processo,
                        pk: this.conf.values.pk
                    },
                    method: 'POST',
                    success: function(form, action) {
                        if(this.conf.scope) {
                            this.conf.scope.__swap__ = this.conf.trigger;
                            this.conf.scope.__swap__();
                            this.conf.scope.__swap__ = undefined;
                        }
                        else this.conf.trigger();
                        this.destroy();
                    },
                    failure: function(form, action) { alert(action.result.message); },
                    scope: this,
                    waitMsg: 'Adicionando item ao Processo.'
                });
            },

            constructor: function(conf) {

                if(!conf) conf = {values: {}};
                else if(!conf.values) conf.values = {};

                var cf = {
                    title: (conf.values.pk ? 'Editar item de um Processo' : 'Adicionar item ao Processo'),
                    closable: true,
                    border: false,
                    modal: true,
                    resizable: false,
                    width: 550,
                    height: 355,
                    conf: conf,
                    buttons: [
                        {text: 'Salvar',scope: this,handler: this.commit},
                        {text: 'Cancelar',scope: this,handler: this.destroy}
                    ]
                };

                toolkit.adm.compras.ProdutoProcessoAquisicao.superclass.constructor.call(this, cf);
                this.add(this.getFormPanel());
            }
        }
    );

    toolkit.adm.compras.ProcessoAquisicao = Ext.extend(
        toolkit.adm.eproc.Processo,
        {
            controller: 'COMPRASProcessoAquisicao',

            refreshProcessoItems: function() {
                this.getSecondTab().getStore().reload();
            },

            addItem: function() {
                new toolkit.adm.compras.ProdutoProcessoAquisicao({
                    processo: this.conf.values.pk,
                    trigger: this.refreshProcessoItems,
                    scope: this,
                    values: {}
                }).show();
            },

            editItem: function() {
                var selection = this.getSecondTab().getSelectionModel().getSelected();
                if(selection) {
                    new toolkit.adm.compras.ProdutoProcessoAquisicao({
                        processo: this.conf.values.pk,
                        trigger: this.refreshProcessoItems,
                        scope: this,
                        values: selection.json
                    }).show();
                }
                else alert('Primeiro selecione um item para edição.');
            },

            deleteItems: function() {
                var selection = this.getSecondTab().getSelectionModel().getSelections();

                if(selection.length > 0) {
                    var pps = [];
                    Ext.each(selection,function(item) {pps.push(item.get('pk'));});
                    Ext.Msg.show({
                        title: 'Removendo itens do processo',
                        msg: 'Tem certeza que deseja remover os itens do processo?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(action) {
                            if(action != 'yes') return;
                            Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'COMPRASProcessoAquisicao',
                                    'delete_items'
                                ),
                                params: {pks: pps},
                                success: this.refreshProcessoItems,
                                scope: this
                            });
                        },
                        scope: this
                    });

                }
                else alert('Primeiro selecione os itens que serão removidos.');
            },

            setNd: function() {
                var selection = this.getSecondTab().getSelectionModel().getSelections();
                if(selection.length > 0) {
                    var pps = [];
                    Ext.each(selection,function(item) {pps.push(item.get('pk'));});
                    new toolkit.adm.compras.NotaDotacao({
                        produtos: pps,
                        scope: this,
                        trigger: this.refreshProcessoItems
                    }).show();

                }
                else alert('Primeiro selecione os itens para selecionar a ND.');
            },

            unSetNd: function() {
                var selection = this.getSecondTab().getSelectionModel().getSelections();
                if(selection.length > 0) {
                    var pps = [];
                    Ext.each(selection,function(item) {pps.push(item.get('pk'));});

                    Ext.Msg.show({
                        title: 'Remover seleção de ND',
                        msg: 'Tem certeza que deseja limpar a seleção da ND para os itens selecionados?',
                        icon: Ext.Msg.QUESTION,
                        buttons: Ext.Msg.YESNO,
                        fn: function(button) {
                            button == 'yes' && Ext.Ajax.request({
                                url: toolkit.util.Normalize.controller_action(
                                    'COMPRASProcessoAquisicao',
                                    'unset_nd'
                                ),
                                params: {items: pps},
                                success: function(request) {
                                    var obj = Ext.decode(request.responseText);

                                    if(obj.success) {
                                        this.getSecondTab().getStore().reload();
                                    }
                                    else alert('Não foi possivel remover a seleção da ND dos itens selecionados.');
                                },
                                failure: function() {
                                    alert('Não foi possivel remover a seleção da ND dos itens selecionados.');
                                },
                                scope: this
                            });
                        },
                        scope: this
                    })

                }
                else alert('Primeiro selecione os itens para limpar a seleção da ND.');
            },

            getFirstTab: function(){
                if(!this.firstTab){
                    this.firstTab = toolkit.adm.compras.ProcessoAquisicao.superclass.getFirstTab.call(this);
                    this.firstTab.insert(4,{
                        hiddenName: 'orcamento',
                        name: 'orcamento',
                        fieldLabel: 'Orçamento',
                        xtype: 'combo',
                        store: [['1', 'ND'],['2','IDENTIFICAÇÃO ORÇAMENTÁRIA']],
                        value: this.conf.values.orcamento ? this.conf.values.orcamento : '',
                        readOnly: this.conf.values.orcamento != undefined,
                        disabled: this.conf.values.orcamento != undefined,
                        triggerAction: 'all',
                        allowBlank: false,
                        validateOnBlur: true,
                        editable: true
                    });
                }
                return this.firstTab;
            },

            getTabPanel: function() {
                if(!this.tabPanel) {
                    this.tabPanel = new Ext.TabPanel({
                        activeTab: 0,
                        region: 'center',
                        border: false,
                        items: [this.getFirstTab()]
                    });
                    if(this.conf.values.pk) this.tabPanel.add(this.getSecondTab());
                }
                return this.tabPanel
            },

            getSecondTab: function() {
                if(!this.secondTab) {
                    var store = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            this.controller,
                            'list_produto_from'
                        ),
                        fields: [
                            'status', 'produto', 'produto_pk', 'qnt',
                            'valor_estimado', 'valor_estimado_unitario',
                            'nd', 'pk', 'descricao', 'orcamento'
                        ],
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: {processo_aquisicao: this.conf.values.pk},
                        autoLoad: true
                    });

                    this.secondTab = new Ext.grid.GridPanel({
                        title: 'Produtos para Aquisição',
                        store: store,
                        tbar: [
                            {
                                text: 'Adicionar',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/images/add.png',
                                scope: this,
                                handler: this.addItem
                            },
                            {
                                text: 'Editar',
                                icon: '/' + global.Context + '/static/images/edit.png',
                                scope: this,
                                handler: this.editItem
                            },
                            {
                                text: 'Remover',
                                icon: '/' + global.Context + '/static/images/delete.png',
                                scope: this,
                                handler: this.deleteItems
                            },
                            '-',
                            '->',
                            '-',
                            {
                                text: 'Selecionar ND',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/adm/images/sel_nd.png',
                                scope: this,
                                handler: this.setNd
                            },
                            {
                                text: 'ND não Gerada',
                                iconCls: true,
                                icon: '/' + global.Context + '/static/adm/images/unsel_nd.png',
                                scope: this,
                                handler: this.unSetNd
                            }
                        ],
                        bbar: new Ext.PagingToolbar({store: store,displayInfo: true}),
                        cm: new Ext.grid.ColumnModel([
                            {
                                header: '',
                                dataIndex: 'status',
                                id: 'status',
                                width: 25,
                                menuDisabled: true,
                                renderer: toolkit.util.formatStatus
                            },
                            {header: 'Produto',dataIndex: 'produto',sortable: true,width: 260},
                            {header: 'Quantidade',dataIndex: 'qnt',sortable: true,width: 75,menuDisabled: true},
                            {
                                header: 'Estimado',
                                dataIndex: 'valor_estimado',
                                sortable: true,
                                width: 75,
                                renderer: toolkit.util.formatCurrency
                            },
                            {header: 'N.D.',dataIndex: 'nd',sortable: true,width: 90}
                        ]),
                        listeners: { scope: this,dblclick: this.editItem }
                    });
                }

                return this.secondTab
            },

            setProcessoId: function(pk) {
                this.conf.values.pk = pk;
                if(this.conf.values.pk) this.getTabPanel().add(this.getSecondTab());
            },

            commit: function() {
                var form = this.getFormPanel().getForm();
                form.waitMsgTarget = this.getEl();
                form.submit({
                    url: toolkit.util.Normalize.controller_action(
                        this.controller,
                        (this.conf.values.pk ? 'update' : 'create')
                    ),
                    params: {
                        processo: this.conf.values ? this.conf.values.pk : undefined
                    },
                    validate: 'client',
                    waitMsg: 'Gravando dados do processo...',
                    success: function(form, action) {
                        if(this.conf.scope) {
                            this.conf.scope.__call__ = this.conf.trigger;
                            this.conf.scope.__call__();
                            this.conf.scope.__call__ = undefined;
                        }
                        this.setProcessoId(action.result.pk);
                    },
                    failure: function(form, action) {console.debug(action);},
                    scope: this
                });
            },

            constructor: function(conf)  {
                toolkit.adm.compras.ProcessoAquisicao.superclass.constructor.call(this, conf);
                this.getFormPanel().setWidth(565);
                this.getFormPanel().setHeight(440);
                this.doLayout();
                this.setTitle('Processo de Aquisição');
            }
        }
    );
    toolkit.adm.eproc.registraTipoProcesso({
        icon: 'static/adm/images/processo_aquisicao.png',
        title: 'Processo de Aquisição',
        object: toolkit.adm.compras.ProcessoAquisicao
    });


    toolkit.adm.compras.Gemp = Ext.extend(
        Ext.Panel,
        {
            _not_implemented: function(){ console.debug('not implemented'); },

            constructor: function(args) {
                var cf = {
                    title: 'Notas de Empenho',
                    border: false,
                    closable: false,
                    layout: 'border'
                };
                this.storeGrid = {'get_store/ne': undefined}
                toolkit.adm.compras.Gemp.superclass.constructor.call(this, cf);
                var active = toolkit.Application.tabspace.getActiveTab();
                toolkit.Application.tabspace.remove(active);
                toolkit.Application.tabspace.add(this);
                this.add(this.getPanelNe());
                this.on('render', function(){
                    this.getStore(this.getParamsGrid({method:'get_store/ne'})).load({params:{start: 0, limit: 50}});
                },this);
            },

            /*****
             *
             *    PANEL Nota de Empenho
             *
             **/
            getPanelNe: function(){
                if(!this.panelNe){
                    this.panelNe = new Ext.grid.GridPanel({
                        region: 'center',
                        border: false,
                        cm: this.getNeColumnModel(),
                        store: this.getStore(this.getParamsGrid({method:'get_store/ne'})),
                        sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                        bbar: this.getNeGridPaginator(),
                        tbar: this.getNeGridToolbar(),
                        listeners: {
                            scope: this,
                            dblclick: function() {if(this.panelNe.getSelectionModel().getSelected()) this.editNe();}
                        }
                    });
                }
                return this.panelNe;
            },

            getCredor: function(){
                if(this.getPanelNe().getSelectionModel().getSelected())
                    return this.getPanelNe().getSelectionModel().getSelected().get('credor_pk');
                else return undefined;
            },

            getControllerAction: function(){
                if(this.getPanelNe().getSelectionModel().getSelected())
                    return this.getPanelNe().getSelectionModel().getSelected().get('controller');
                else return undefined;
            },

            getFatherNe: function() {
                return {
                    store: this.getStore(this.getParamsGrid({method:'get_store/ne'})),
                    controller: this.getControllerAction(),
                    reload_grid: function(){this.store.reload();}
                };
            },

            /**
             *  getStore
             *
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(!this.storeGrid[args.method]){
                    this.storeGrid[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid[args.method];
            },

            getParamsGrid: function(args){
                if(args.method == 'get_store/ne')
                    return {
                        controller: 'COMPRASGemp',
                        method: 'get_store/ne',
                        fields: [
                            'codigo',
                            'numero',
                            'credor',
                            'credor_pk',
                            'modalidade',
                            'modalidade_pk',
                            'data',
                            'valor',
                            'processo',
                            'licitacao',
                            'status',
                            'controller',
                            'produto',
                            'quantidade'
                        ],
                        baseParams: {}
                    };
                return undefined;
            },

            getNeColumnModel: function() {
                if(!this.neColumnModel) {
                    this.neColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'processo', header: 'Processo', sortable: true, width: 100},
                        {dataIndex: 'data', header: 'Data', sortable: true, width: 70},
                        {dataIndex: 'numero', header: 'Número', sortable: true, width: 100},
                        {dataIndex: 'credor', header: 'Credor', sortable: true, width: 200},
                        {dataIndex: 'modalidade', header: 'Modalidade', sortable: true, width: 80},
                        {dataIndex: 'produto', header: 'Produto', sortable: true, width: 250},
                        {dataIndex: 'quantidade', header: 'Qtd.', sortable: true, width: 50},
                        {dataIndex: 'valor', header: 'Valor', sortable: true, width: 70, renderer: toolkit.util.formatCurrency},
                    ]);
                }
                return this.neColumnModel;
            },

            getNeGridPaginator: function() {
                if(!this.gridPaginator) {
                    this.gridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(this.getParamsGrid({method:'get_store/ne'})),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.gridPaginator;
            },

            editNe: function() {
                var codigo = undefined;
                try{
                    codigo = this.getPanelNe().getSelectionModel().getSelected().get('codigo');
                }catch(e){;}
                if(codigo != undefined){
                    new toolkit.widget.ExtCrudForm(
                        this.getFatherNe(),
                        toolkit.widget.ExtCrudForm.TYPE.EDIT,
                        this.getPanelNe().getSelectionModel().getSelected().get('codigo'),
                        [
                            {name: 'credor',enabled: false},
                            {name: 'produto_processo',enabled: false},
                            {name: 'modalidade',enabled: false},
                            {name: 'valor',enabled: false}
                        ]
                    ).show();
                }
                else alert('Primeiro selecione um Processo para alterar Licitação.');
            },

            getNeGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: 'Criar NE Registro de Preço',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/add.png',
                    handler: function(){
                        var wnd = new toolkit.adm.compras.NeAquisicaoRegistroPreco(
                            {
                                store_ne: this.getStore(this.getParamsGrid({method:'get_store/ne'}))
                            }
                        );
                        wnd.show();
                    },
                    scope: this
                });
                menu.push(['-']);
                menu.push({
                    text: 'Alterar',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/engine/images/icons/athenas-0034.png',
                    handler: function(){this.editNe();},
                    scope: this
                });
                menu.push(['-']);
                menu.push({
                    text: 'Ver Itens',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/document-sing.png',
                    handler: function(){
                        if(this.getCredor()){
                            var wnd = new toolkit.adm.compras.WindowSubItem({
                                credor: this.getCredor()
                            });
                            wnd.show();
                        }else alert('Selecione uma NE!');
                    },
                    scope: this
                });
                return menu;
            }
        }
    );

    toolkit.adm.compras.WindowSubItem = Ext.extend(
        Ext.Window,
        {
            constructor: function(conf) {
                var cf = {
                    border: false,
                    resizable: false,
                    modal: true,
                    layout: 'border',
                    width: 700,
                    height: 550,
                    conf_obj: conf
                }
                this.storeGrid = {
                    'get_store/subitem': undefined,
                    'get_store/item': undefined
                }
                toolkit.adm.compras.WindowSubItem.superclass.constructor.call(this, cf);
                this.setTitle('Itens da NE');
                this.add(this.getPanelSubItem());
                this.add(this.getPanelItem());
                var obj = this;
                setTimeout(function() {obj.doLayout();}, 50);
                this.on('render', function() {
                    this.getStore(this.getParamsGrid({method:'get_store/subitem'})).baseParams['produto_vencedor'] = this.conf_obj.credor;
                    this.getStore(this.getParamsGrid({method:'get_store/subitem'})).load({params:{start: 0, limit: 50}});
                },this);
            },

            /**
             *  getStore
             *
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(!this.storeGrid[args.method]){
                    this.storeGrid[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid[args.method];
            },

            getParamsGrid: function(args){
                if(args.method == 'get_store/subitem')
                    return {
                        controller: 'COMPRASGemp',
                        method: 'get_store/subitem',
                        fields: ['codigo','nome', 'numero','elemento','elemento_pk'],
                        baseParams: { produto_vencedor: '' }
                    };
                if(args.method == 'get_store/item')
                    return {
                        controller: 'COMPRASGemp',
                        method: 'get_store/item',
                        fields: ['codigo','nome','unidade','descricao','quantidade','valor_unitario','valor_total'],
                        baseParams: {sub_item: '', produto_vencedor: ''}
                    };
            },

            /*****
             *
             *    PANEL SubItem
             *
             **/
            getPanelSubItem: function(){
                if(!this.panelSubItem){
                    this.panelSubItem = new Ext.grid.GridPanel({
                        title: 'SubItem',
                        region: 'center',
                        border: false,
                        cm: this.getSubItemColumnModel(),
                        store: this.getStore(this.getParamsGrid({method:'get_store/subitem'})),
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:true,
                            listeners: {
                                scope: this,
                                rowselect: function(sm) {
                                    this.getStoreItem().baseParams['sub_item'] = sm.getSelected().get('codigo');
                                    this.getStoreItem().baseParams['produto_vencedor'] = this.conf_obj.credor;
                                    this.getStoreItem().load({params:{start: 0, limit: 50}});
                                 }
                            }
                        }),
                        bbar: this.getSubItemGridPaginator(),
                        tbar: []
                    });
                }
                return this.panelSubItem;
            },

            getSubItemGridPaginator: function() {
                if(!this.subItemGridPaginator) {
                    this.subItemGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(this.getParamsGrid({method:'get_store/subitem'})),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.subItemGridPaginator;
            },

            getSubItemColumnModel: function() {
                if(!this.subItemColumnModel) {
                    this.subItemColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'numero', header: 'Número', sortable: true, width: 100},
                        {dataIndex: 'nome', header: 'Nome', sortable: true, width: 505},
                        {dataIndex: 'elemento', header: 'Elemento', sortable: true, width: 80}
                    ]);
                }
                return this.subItemColumnModel;
            },

            /*****
             *
             *    PANEL Item
             *
             **/
            getPanelItem: function(){
                if(!this.panelItem){
                    this.panelItem = new Ext.grid.EditorGridPanel({
                        title: 'Item',
                        region: 'south',
                        height: 250,
                        border: false,
                        clicksToEdit: 1,
                        cm: this.getItemColumnModel(),
                        store: this.getStoreItem(),
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getItemGridPaginator(),
                        tbar: []
                    });
                }
                return this.panelItem;
            },

            getItem: function(){
                if(!this.item){
                    this.item = Ext.data.Record.create([
                        { name: 'codigo', type: 'string'},
                        { name: 'nome', type: 'string'},
                        { name: 'descricao', type: 'string'},
                        { name: 'quantidade', type: 'string'},
                        { name: 'valor_unitario', renderer: toolkit.util.formatCurrency},
                        { name: 'valor_total', renderer: toolkit.util.formatCurrency}
                    ]);
                }
                return this.item;
            },

            getReader: function(){
                if(this.reader == undefined){
                    this.reader = new Ext.data.JsonReader({
                            totalProperty: 'totalRows',
                            successProperty: 'success',
                            root: 'result',
                            start: 0,
                            limit: 50
                        },
                    this.getItem());
                }
                return this.reader;
            },

            getProxy:function(){
                if(this.proxy == undefined){
                    this.proxy = new Ext.data.HttpProxy({
                        api: {
                            read: 'COMPRASGemp/get_store/item/',
                            create: 'COMPRASGemp/update/item/',
                            update: 'COMPRASGemp/update/item/',
                            destroy: 'COMPRASGemp/get_store/item/destroy/'
                        }
                    });
                }
                return this.proxy;
            },

            getWriter: function(){
                if(this.writer == undefined){
                    this.writer = new Ext.data.JsonWriter({
                        encode: true,
                        writeAllFields: false
                    });
                }
                return this.writer;
            },

            getStoreItem: function(){
                if(this.storeItem == undefined){
                    this.storeItem = new Ext.data.Store({
                        id: 'user',
                        proxy: this.getProxy(),
                        reader: this.getReader(),
                        writer: this.getWriter(),
                        autoSave: false,
                        baseParams:{start: 0, limit: 50},
                        listeners: {
                            scope: this,
                            update: function(store, record, operation ){
                                store.save();
                                store.reload();
                            }
                        }
                    });
                }
                return this.storeItem;
            },

            getItemGridPaginator: function() {
                if(!this.itemGridPaginator) {
                    this.itemGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreItem(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.itemGridPaginator;
            },

            getItemColumnModel: function() {
                if(!this.itemColumnModel) {
                    this.itemColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'nome', header: 'Nome', sortable: true, width: 140},
                        {dataIndex: 'descricao', header: 'Descrição', sortable: true, width: 300, height: 40, editor:{xtype:'xhtmleditor',allowBlank: true}},
                        {dataIndex: 'quantidade', header: 'Quantidade', sortable: true, width: 80},
                        {dataIndex: 'valor_unitario', header: 'Valor', sortable: true, width: 80, renderer: toolkit.util.formatCurrency},
                        {dataIndex: 'valor_total', header: 'Total', sortable: true, width: 80, renderer: toolkit.util.formatCurrency}
                    ]);
                }
                return this.itemColumnModel;
            }
        }
    );

    toolkit.adm.compras.NeAquisicaoRegistroPreco = Ext.extend(
        Ext.Window,
        {
            constructor: function(conf) {
                var cf = {
                    border: false,
                    resizable: false,
                    modal: true,
                    layout: 'border',
                    width: 700,
                    height: 550,
                    store_ne: conf.store_ne
                }
                this.storeGrid = {
                    'get_store/processo': undefined,
                    'get_store/vencedor': undefined
                }
                toolkit.adm.compras.NeAquisicaoRegistroPreco.superclass.constructor.call(this, cf);
                this.setTitle('NE por Registro de Preço');
                this.add(this.getPanelProcesso());
                this.add(this.getPanelVencedor());
            },

            /**
             *  getStore
             *
             * @param args.controller
             * @param args.method
             * @param args.fields
             * @param args.baseParams
             **/
            getStore: function(args){
                if(this.storeGrid[args.method] == undefined){
                    this.storeGrid[args.method] = new Ext.data.JsonStore({
                        url: toolkit.util.Normalize.controller_action(
                            args.controller,
                            args.method
                        ),
                        fields: args.fields,
                        root: 'result',
                        totalProperty: 'totalRows',
                        baseParams: args.baseParams,
                        autoLoad: true
                    });
                }
                return this.storeGrid[args.method];
            },

            getParamsGrid: function(args){
                if(args.method == 'get_store/processo')
                    return {
                        controller: 'COMPRASNeAquisicaoRegistroPreco',
                        method: 'get_store/processo',
                        fields: ['codigo','numero', 'titulo','interessado'],
                        baseParams: {start: 0, limit: 50}
                    };
                if(args.method == 'get_store/vencedor')
                    return {
                        controller: 'COMPRASNeAquisicaoRegistroPreco',
                        method: 'get_store/vencedor',
                        fields: ['codigo','nome','unidade','descricao','quantidade','valor_unitario','valor_total', 'usado'],
                        baseParams: {start: 0, limit: 50, processo: this.getProcesso()}
                    };
                return undefined;
            },

            getProcesso: function() {
                try{
                    return this.getPanelProcesso().getSelectionModel().getSelected().get('codigo');
                }catch(e){alert('Selecione um processo!');}
            },

            /*****
             *
             *    PANEL Processo
             *
             **/
            getPanelProcesso: function(){
                if(!this.panelProcesso){
                    this.panelProcesso = new Ext.grid.GridPanel({
                        title: 'Processos',
                        region: 'center',
                        border: false,
                        cm: this.getProcessoColumnModel(),
                        store: this.getStore(this.getParamsGrid({method:'get_store/processo'})),
                        sm: new Ext.grid.RowSelectionModel({
                            singleSelect:true,
                            listeners: {
                                scope: this,
                                rowselect: function(sm) {
                                    this.getStoreVencedor().baseParams['processo'] = sm.getSelected().get('codigo');
                                    this.getStoreVencedor().load();
                                 }
                            }
                        }),
                        bbar: this.getProcessoGridPaginator(),
                        tbar: []
                    });
                }
                return this.panelProcesso;
            },

            getProcessoGridPaginator: function() {
                if(!this.processoGridPaginator) {
                    this.processoGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStore(this.getParamsGrid({method:'get_store/processo'})),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.processoGridPaginator;
            },

            getProcessoColumnModel: function() {
                if(!this.processoColumnModel) {
                    this.processoColumnModel = new Ext.grid.ColumnModel([
                        {header: 'Numero', dataIndex: 'numero',sortable: true,width: 105},
                        {header: 'Título',dataIndex: 'titulo',sortable: true,width: 280},
                        {header: 'Interessado',dataIndex: 'interessado',sortable: true,width: 280}
                    ]);
                }
                return this.processoColumnModel;
            },

            /*****
             *
             *    PANEL Vencedor
             *
             **/
            getPanelVencedor: function(){
                if(!this.panelVencedor){
                    this.panelVencedor = new Ext.grid.EditorGridPanel({
                        title: 'Vencedor e Produto',
                        region: 'south',
                        height: 250,
                        border: false,
                        clicksToEdit: 1,
                        cm: this.getVencedorColumnModel(),
                        store: this.getStoreVencedor(),
                        sm: new Ext.grid.RowSelectionModel({singleSelect:false}),
                        bbar: this.getVencedorGridPaginator(),
                        tbar: this.getVencedorGridToolbar(),
                        scope: this
                    });
                }
                return this.panelVencedor;
            },

            getVencedorCodigo: function(){
              return this.getPanelVencedor().getSelectionModel().getSelected().get('vencedor_cod');
            },

            getProdutoCodigo: function(){
                try{
                    return this.getPanelVencedor().getSelectionModel().getSelected().get('produto_cod');
                }catch(e){ return undefined;}
            },

            getVencedor: function(){
                if(!this.vencedor){
                    this.vencedor = Ext.data.Record.create([
                        { name: 'codigo', type: 'string'},
                        { name: 'vencedor', type: 'string'},
                        { name: 'vencedor_cod', type: 'string'},
                        { name: 'produto', type: 'string'},
                        { name: 'produto_cod', type: 'string'},
                        { name: 'quantidade', type: 'string'},
                        { name: 'usado', type: 'string'},
                        { name: 'valor_unitario', renderer: toolkit.util.formatCurrency},
                        { name: 'valor_total', renderer: toolkit.util.formatCurrency}
                    ]);
                }
                return this.vencedor;
            },

            getReader: function(){
                if(this.reader == undefined){
                    this.reader = new Ext.data.JsonReader({
                            totalProperty: 'totalRows',
                            successProperty: 'success',
                            root: 'result',
                            start: 0,
                            limit: 50
                        },
                        this.getVencedor()
                    );
                }
                return this.reader;
            },

            getProxy:function(){
                if(this.proxy == undefined){
                    this.proxy = new Ext.data.HttpProxy({
                        api: {
                            read: 'COMPRASNeAquisicaoRegistroPreco/get_store/vencedor/',
                            create: 'COMPRASNeAquisicaoRegistroPreco/update/vencedor/',
                            update: 'COMPRASNeAquisicaoRegistroPreco/update/vencedor/',
                            destroy: 'COMPRASNeAquisicaoRegistroPreco/get_store/vencedor/destroy/'
                        }
                    });
                }
                return this.proxy;
            },

            getWriter: function(){
                if(this.writer == undefined){
                    this.writer = new Ext.data.JsonWriter({
                        encode: true,
                        writeAllFields: false
                    });
                }
                return this.writer;
            },

            getStoreVencedor: function(){
                if(this.storeVencedor == undefined){
                    this.storeVencedor = new Ext.data.Store({
                        id: 'user',
                        proxy: this.getProxy(),
                        reader: this.getReader(),
                        writer: this.getWriter(),
                        autoSave: false,
                        baseParams:{start: 0, limit: 50},
                        listeners: {
                            scope: this,
                            update: function(store, record, operation ){
                                store.save();
                                store.reload();
                            }
                        }
                    });
                }
                return this.storeVencedor;
            },

            getVencedorGridPaginator: function() {
                if(!this.vencedorGridPaginator) {
                    this.vencedorGridPaginator = new Ext.PagingToolbar({
                        autoWidth: true,
                        store: this.getStoreVencedor(),
                        displayInfo: true,
                        pageSize: 50,
                        prependButtons: true
                    });
                }
                return this.vencedorGridPaginator;
            },

            mannagerNe: function(){
                new toolkit.widget.ExtCrudForm(
                    {
                        store: this.store_ne,
                        controller: 'COMPRASNeAquisicaoRegistroPreco',
                        reload_grid: function(){
                            this.store.reload();
                        }
                    },
                    toolkit.widget.ExtCrudForm.TYPE.NEW,
                    false,
                    [
                        {name: 'credor', value: this.getVencedorCodigo(), enabled: false},
                        {name: 'produto_processo', value: this.getProdutoCodigo(), enabled: false},
                        {name: 'modalidade', enabled: true},
                        {name: 'valor', enabled: false}
                    ]
                ).show();
            },

            getVencedorGridToolbar: function() {
                var menu = [];
                menu.push({
                    text: 'Criar NE',
                    iconCls: true,
                    icon: '/' + global.Context + '/static/images/add.png',
                    handler: function(){
                        if(this.getProdutoCodigo())
                            this.mannagerNe();
                        else alert('Selecione um produto!');
                    },
                    scope: this
                });
                return menu;
            },

            getVencedorColumnModel: function() {
                if(!this.vencedorColumnModel) {
                    this.vencedorColumnModel = new Ext.grid.ColumnModel([
                        {dataIndex: 'vencedor', header: 'Vencedor', width: 190, sortable: true},
                        {dataIndex: 'produto', header: 'Produto', width: 260, sortable: true},
                        {dataIndex: 'quantidade', header: 'Qtd', width: 50, sortable: true},
                        {dataIndex: 'usado', header: 'Emp.', width: 50, sortable: true}
                    ]);
                }
                return this.vencedorColumnModel;
            }
        }
    );

}
