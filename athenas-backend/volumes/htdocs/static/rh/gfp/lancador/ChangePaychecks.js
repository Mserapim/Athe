/**
 *
 */

Ext.ns('rh.gfp.lancador');

rh.gfp.lancador.ChangePaychecks = Ext.extend(
    Ext.Window,
    {
        'setRequest': function(request) {
            this._request = request;
            Ext.apply(
                this.getStore().baseParams,
                {'solicitacao': request}
            );

            if(this._request)
                this.getStore().load({});
            else
                this.getStore().removeAll();
        },

        'reload': function() {
            this.getStore().reload()
        },

        'getColumnModel': function() {
            if(!this._columnModel)
                this._columnModel = new Ext.grid.ColumnModel({
                    // specify any defaults for each column
                    defaults: {
                        sortable: true // columns are not sortable by default           
                    },
                    columns: [{
                        id: 'pk',
                        header: 'Código',
                        dataIndex: 'pk',
                        width: 80
                    },{
                        id: 'autoExpandColumn',
                        header: 'Contracheque',
                        dataIndex: 'contracheque',
                        width: 300
                    },{
                        id: 'resumo',
                        header: 'Resumo',
                        dataIndex: 'resumo',
                        width: 200
                    },{
                        // xtype: 'checkcolumn',
                        header: 'Conferido',
                        dataIndex: 'conferido',
                        width: 55
                    }]
                });
            console.debug('getColumnModel...');
            return this._columnModel;
        },

        'confirmChange': function(){
            var selections = this.getAuditoriaContrachequeGrid().getSelectionModel().getSelections();
            if(selections.length > 0) {
                var fes = [];
                
                Ext.each(selections, function(fe) {fes.push(fe.get('pk'));});
                
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('GFPContraChequeAuditoria', 'confirm'),
                    params: {changes: fes},
                    success: function(request) {
                        var obj = Ext.decode(request.responseText);
                        if(!obj.success){
                            Ext.Msg.show({
                                icon: Ext.Msg.ERROR,
                                msg: obj.message,
                                buttons: Ext.Msg.OK
                            });                            
                        }else{
                            this.reload();
                        }                        },
                    failure: function() {alert('Ocorreu um erro tentando remover os lançamentos.');},
                    scope: this
                });
            }
            else alert('Primeiro selecione as mudanças a serem confirmadas.');
        },

        'changeFilter': function(bnt){
            console.debug(bnt.pressed);
            this.getStore().baseParams['all']= bnt.pressed;
            this.getStore().load({});            

        },

        'getToolbar': function() {
            if(!this._toolbar)
                this._toolbar = new Ext.Toolbar({
                    'items': [
                        {
                            'text': 'Confirmar',
                            'scope': this,
                            'handler': this.confirmChange,
                            'icon': '/' + global.Context + '/static/rh/images/folha-validar.png',                           
                        },
                        '-',
                        {
                            'text': 'Todos',
                            'enableToggle': true,
                            'toggleHandler': this.changeFilter,
                            'pressed': false,                            
                            'scope': this,
                        },
                        '->',
                        '-',
                        {
                            'iconCls': 'icon-diarias icon-refresh',
                            'scope': this,
                            'handler': this.reload
                        }
                    ]
                });

            return this._toolbar;
        },

        getProxy: function(){
            if(!this.proxyLancamentos){
                this.proxyLancamentos = new Ext.data.HttpProxy({
                    scope: this,
                    method: 'POST',
                    api: {
                        read : toolkit.util.Normalize.controller_action('GFPContraChequeAuditoria', 'list'),
                        create : toolkit.util.Normalize.controller_action('GFPContraChequeAuditoria', 'create'),
                        update: toolkit.util.Normalize.controller_action('GFPContraChequeAuditoria', 'update'),
                        destroy: toolkit.util.Normalize.controller_action('GFPContraChequeAuditoria', 'destroy'),
                    },
                    listeners:{
                        scope: this,
                        beforewrite: function(proxy, action){
                            console.debug('Before Write Proxy...');
                        },
                        write: function(proxy, action){
                            console.debug('After Write Proxy...');
                            this.reload();
                        },
                    }
                });                        
            }
            return this.proxyLancamentos;
        },

        getReader: function(){
            if(!this._readerGhanges){
                this._readerGhanges = new Ext.data.JsonReader({
                    totalProperty: 'totalRows',
                    successProperty: 'success',
                    idProperty: 'pk',
                    root: 'result',
                    messageProperty: 'message'  // <-- New "messageProperty" meta-data
                }, [
                    {'name': 'pk',},
                    {'name': 'resumo',},
                    {'name': 'texto',},
                    {'name': 'contracheque',},
                    {'name': 'modified_by',},
                    {'name': 'modified_at',},
                ]);
            }
            return this._readerGhanges;
        },

        getWriter: function(){
            if(!this._writeChanges){
                this._writeChanges = new Ext.data.JsonWriter({
                    encode: true,
                    writeAllFields: false
                });
            }
            return this._writeChanges;                    
        },

        // getStore: function(){

        //     if(!this._storeChanges){
        //         this._storeChanges = new Ext.data.Store({
        //             id: 'store_changes',
        //             proxy: this.getProxy(),
        //             reader: this.getReader(),
        //             writer: this.getWriter(),  // <-- plug a DataWriter into the store just as you would a Reader
        //             autoSave: false, // <-- false would delay executing create, update, destroy requests until specifically told to do so with some [save] buton.
        //         }); 
        //     }
        //     return this._storeChanges;
        // },

        'getStore': function() {
            if(!this._store) {
                this._store = new Ext.data.Store({
                    'proxy': new Ext.data.HttpProxy({
                        'url': toolkit.util.Normalize.controller_action(
                            'GFPContraChequeAuditoria', 'list'
                        ),
                        'method': 'POST',
                        // 'disableCaching': false
                    }),
                    'reader': new Ext.data.JsonReader({
                        'root': 'result',
                        'totalProperty': 'totalRows',
                        'fields': [
                            {'name': 'pk', 'type': 'int'},
                            {'name': 'resumo', 'type': 'string'},
                            {'name': 'texto', 'type': 'string'},
                            {'name': 'servidor', 'type': 'string'},
                            {'name': 'modified_by', 'type': 'string'},
                            {'name': 'modified_at', 'type': 'string'},
                            {'name': 'conferido', 'type': 'boolean'},
                        ],
                        // 'baseParams': {
                        //     folha: this.folha.pk,
                        //     all: false
                        // }
                    })
                });
            }
            console.debug('getStore...');

            return this._store;
        },

        'getExpander': function(){
            if(!this._expander){
                this._expander = new Ext.ux.grid.RowExpander({
                    tpl : new Ext.Template(
                        '<p><b>{resumo}</b> por {modified_by} em {modified_at}</p><br>',
                        '<p>{texto}</p>'
                    )
                });
            }
            console.debug('getExpander...');
            return this._expander;
        },

        'getAuditoriaContrachequeGrid': function() {
            if(!this._auditoriaGrid) {
                console.debug('getAuditoriaContrachequeGrid...');
                this._auditoriaGrid = new Ext.grid.GridPanel({
                    'tbar': this.getToolbar(),
                    'height': 300,
                    'store': this.getStore(),
                    'plugins': this.getExpander(),
                    'autoExpandColumn': 'autoExpand',
                    'iconCls': 'icon-grid',
                    'viewConfig': {
                        'forceFit':true
                    },                     
                    // 'cm': this.getColumnModel(),
                    'cm': new Ext.grid.ColumnModel([
                    // 'columns': [
                            // { header: '', dataIndex: 'status', sortable: true, width: 95, menuDisabled: true, renderer: toolkit.util.formatStatus },
                            this.getExpander(),
                            // { header: 'Código', dataIndex: 'pk', sortable: true, width: 55 },
                            { header: 'Servidor', dataIndex: 'servidor', width: 300, sortable: true, id: 'autoExpand'},
                            { header: 'Resumo', dataIndex: 'resumo', width: 250, menuDisabled: true },
                            // { header: 'Usuário', dataIndex: 'modified_by', width: 80, menuDisabled: true },
                            // { header: 'Conferido', dataIndex: 'conferido', width: 55}
                    ]),
                    listeners: {
                        'render': function(g) {
                            new Ext.LoadMask(
                                g.getEl(),
                                {
                                    store: g.getStore(),
                                    msg: 'Carregando alterações na folha...'
                                }
                            );
                            // g.getStore().load({});
                        }
                    },                    
                });
            }
            console.debug('getAuditoriaContrachequeGrid 2...');

            return this._auditoriaGrid;
        },

        'getDisplayPanel': function() {
            if(!this._displayPanel)
                this._displayPanel = new Ext.Panel({
                    'region': 'center',
                    'autoScroll': true,
                    'height': 200
                });

            return this._displayPanel;
        },

        'constructor': function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                'title': 'Alterações na Folha de Pagamento [ '+cfg.folha.description+' ]',
                // 'layout': 'border',
                'height': 300,
                'width': 650,
                'items': [
                    this.getAuditoriaContrachequeGrid(),
                    // this.getDisplayPanel()
                ],
                'listeners': {
                    'scope': this,
                    'render': function() {
                        // new Ext.LoadMask(this.getEl(), {
                        //     'store': this.getStore(),
                        //     'msg': 'Carregando informações...'
                        // })
                        console.debug(this);
                        this.getStore().baseParams['folha']= this.folha.pk;
                        this.getStore().baseParams['all']= false;
                        this.getStore().load({});
                    }
                }
            });

            rh.gfp.lancador.ChangePaychecks.superclass.constructor.call(this, cfg);
            console.debug(this);
        }
    }
);