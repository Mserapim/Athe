Ext._define('common.itop.userrequest.UserRequestGrid', {
    extend: 'Ext.grid.GridPanel',

    keywordFieldMessage: 'Localizar pelo Nº do chamado',

    keywordFieldWidth: 320,

    getStore: function(){
        if(!this._getStore){
            this._getStore =  Ext._create('Ext.data.Store',{
                autoLoad: true,
                proxy: Ext._create('Ext.data.HttpProxy',{
                    url: toolkit.util.Normalize.controller_action('CIUserRequest', 'get_user_request'),
                    disableCaching: false,
                    method: 'GET'
                }),
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'ref', type: 'string'},
                        {name: 'status', type: 'string'},
                        {name: 'start_date', type: 'string'},
                        {name: 'caller_id_friendlyname', type: 'string'},
                        {name: 'location_name', type: 'string'},
                    ],
                }),
                sortInfo: {
                    field: "start_date",
                    direction: "DESC"
                }
            });
        }
        return this._getStore;
    },


    getColumnModel: function() {
        if(!this._columnModel){
            this._columnModel = Ext._create('Ext.grid.ColumnModel',{
                columns: [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nº Chamado', dataIndex: 'ref', width: 90},
                    {header: 'Estado', dataIndex: 'status', width: 140},
                    {header: 'Registro', dataIndex: 'start_date', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width:90},
                    {header: 'Solicitante', dataIndex: 'caller_id_friendlyname', width:160},
                    {header: 'Local', dataIndex: 'location_name', id: 'autoExpandColumn',}
                ]
            });
        }
        return this._columnModel;
    },

    getKeywordField: function(cfg) {
        cfg = core.nullValue(cfg, {});

        if(!this._keywordField)
            this._keywordField = Ext._create('Ext.form.TextField', {
                id: 'searchBox',
                emptyText: this.keywordFieldMessage,
                width: (cfg.keywordFieldWidth || this.keywordFieldWidth),
                enableKeyEvents: true,
                // submitValue: false,
                listeners: {
                    scope: this,
                    specialkey: function(field, event) {
                        if(event.getKey() == event.ENTER || event.getKey() == event.TAB)
                            this.doKeywordFilter(field.getValue());
                    }
                }
            });

        return this._keywordField;
    },

    doKeywordFilter: function(keyword) {
        var store = this.getStore();
        if(keyword !== '')
            store.baseParams.keyword = keyword;
        else {
            store.baseParams.keyword = null;
            delete store.baseParams.keyword;
        }

        store.load({});
    },

    createUserSolicitation: function(){
            wnd = Ext._create('common.itop.userrequest.UserRequestWindow', {
                listeners:{
                    scope: this,
                    beforedestroy: function(){
                        this.getStore().reload()
                    }
                }
            });
            wnd.show()
    },

    getToolbar: function(cfg) {
        if(!this._toolbar)
            this._toolbar = Ext._create('Ext.Toolbar', {
                items: [
                    {
                        text: 'Novo',
                        iconCls: 'icon-16px icon-core icon-core-add',
                        scope: this,
                        handler: this.createUserSolicitation,
                    },
                    '-',
                    [
                        'Buscar por: ',
                        this.getKeywordField(cfg),
                    ],
                ]
            });

        return this._toolbar;
    },

    getFooterbar: function(cfg) {
        if(!this._footerbar)
            this._footerbar = Ext._create('Ext.PagingToolbar', {
                store: this.getStore(),
                pageSize: 100,
                displayInfo: true
            });

        return this._footerbar;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(
            cfg,
            {
                store: this.getStore(cfg),
                colModel: this.getColumnModel(),
                autoExpandColumn: 'autoExpandColumn',
                tbar: this.getToolbar(),
                bbar: this.getFooterbar(),
                listeners: {
                    scope: this,
                    render: function(grid) {
                        new Ext.LoadMask(grid.getEl(), {
                            msg: 'Carregando chamados...',
                            store: grid.getStore()
                        });

                        grid.getStore().load({});
                    },
                },

            }
        );

        common.itop.userrequest.UserRequestGrid.superclass.constructor.call(this, cfg);

    },

});
