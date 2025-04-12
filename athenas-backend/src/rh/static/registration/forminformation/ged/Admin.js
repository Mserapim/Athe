Ext._define('rh.registration.forminformation.ged.Admin', {
    extend: 'Ext.grid.GridPanel',

    setForm: function(value) {
        this._formregistration = value;
        this._observeForm();
    },

    _observeForm: function() {
        if(this._formregistration) {
            this.getStore().baseParams = {form: this._formregistration};
            this.getStore().load({});
            this.enable();
        }
        else {

            this.getStore().baseParams = {form: null};
            this.getStore().removeAll();
            this.disable();
        }
    },

    getStore: function() {
        if(!this._store)
            this._store = new Ext.data.Store({
                proxy: new Ext.data.HttpProxy({
                    url: toolkit.util.Normalize.controller_action('RegistrationFormInformation', 'get_attachment'),
                    method: 'GET',
                    disableCaching: false
                }),
                reader: new Ext.data.JsonReader({
                    root: 'collection',
                    totalProperty: 'count',
                    fields: [
                        {name: 'pk', type: 'int'},
                        {name: 'file', type: 'int'},
                        {name: 'icone', type: 'auto'},
                        {name: 'document_type_display', type: 'string'},
                        {name: 'document_type', type: 'string'},
                        {type: "string", name: "created_by"},
                        {name: 'permalink', type: 'string'}
                    ]
                })
            });

        return this._store;
    },

    getParams: function() {
        var params = {};

        if(this._formregistration)
            params.form = this._formregistration;

        return params;
    },

    downloadItem: function() {
        var selections = this.getSelectionModel().getSelections();
        var pks = selections.map(function(item) {return item.get('pk');});

        if(selections.length == 1){
            open(this.getSelectionModel().getSelected().get('permalink'), "_self");
        }
        else if(selections.length > 1){
            url = toolkit.util.Normalize.controller_action('RegistrationFormInformationBase', 'download_attachment') + '?pks=' + pks
            open(url, "_new");
        } else {
            Ext.Msg.show({
                'title': this.title,
                'icon': Ext.Msg.ERROR,
                'buttons': Ext.Msg.OK,
                'msg': 'Selecione o(s) arquivo(s) que deseja realizar o download.'
            });
        }
    },

    getToolbar: function() {
        if(!this._toolbar)
            this._toolbar = new Ext.Toolbar({
                items: [
                    {
                        text: 'Download',
                        scope: this,
                        handler: this.downloadItem,
                        iconCls: 'icon-diarias icon-diarias icon-move-down'
                    }
                ]
            });

        return this._toolbar;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});
        var sm = new Ext.grid.CheckboxSelectionModel();
        Ext.applyIf(cfg, {
            autoExpandColumn: 'autoExpandId',
            tbar: this.getToolbar(),
            sm: sm,
            bbar: new Ext.PagingToolbar({
                displayInfo: true,
                store: this.getStore()
            }),
            store: this.getStore(),
            listeners: {
                render: function(panel) {
                    new Ext.LoadMask(panel.getEl(), {
                        msg: 'Carregando lista de anexos...',
                    });
                }
            },
            columns: [
                // {
                //     header: '',
                //     dataIndex: 'icone',
                //     width: 30,
                //     menuDisabled: true,
                //     renderer: adm.daily.rendererIconGrid
                // },
                {
                    header: 'Chave',
                    dataIndex: 'pk',
                    width: 45
                },
                {
                    header: 'Tipo de documento',
                    dataIndex: 'document_type_display',
                    id: 'autoExpandId'
                },
                sm
            ]
        });

        rh.registration.forminformation.ged.Admin.superclass.constructor.call(this, cfg);

        this._observeForm();
    }
});