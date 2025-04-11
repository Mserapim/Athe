Ext._define('rh.registration.forminformation.ged.Grid', {
    extend: 'Ext.grid.GridPanel',

    setForm: function(value) {
        this._formregistration = value;
        this._observeForm();
    },

    _observeForm: function() {
        if(this._formregistration) {
            this.getStore().baseParams = {'form': this._formregistration};
            this.getStore().load({});
            this.enable();
        }
        else {
            this.getStore().baseParams = {'form': null};
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
                        {'name': 'pk', 'type': 'int'},
                        {'name': 'file', 'type': 'int'},
                        {'name': 'icone', 'type': 'auto'},
                        {'name': 'document_type', 'type': 'string'},
                        {'name': 'state', 'type': 'string'},
                        {'name': 'document_type_display', 'type': 'string'},
                        {'name': 'state_display', 'type': 'string'},
                        {type: "string", name: "created_by"},
                        {'name': 'permalink', 'type': 'string'}
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

    createItem: function() {
        new rh.registration.forminformation.ged.Window({
            action: 'create',
            params: this.getParams(),
            success: {
                scope: this,
                callback: function() {
                    this.getStore().reload();
                    //this.ownerCt.save();
                }
            }
        }).show();
    },

    updateItem: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            var params = this.getParams();
            params.pk = selected.get('pk');

            new rh.registration.forminformation.ged.Window({
                action: 'update',
                params: params,
                values: {
                    document_type: selected.get('document_type'),
                    file: selected.get('file')
                },
                success: {
                    scope: this,
                    callback: function() {
                        this.getStore().reload();
                        //this.ownerCt.save();
                    }
                }
            }).show();
        }
        else Ext.Msg.show({
            title: this.title,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            msg: 'Primeiro selecione o item que deseja editar.'
        });
    },

    removeItems: function() {
        var selections = this.getSelectionModel().getSelections();

        if(selections.length > 0) {
            new rh.registration.forminformation.ged.Window({
                params: {
                    pk: selections.map(function(item) { return item.get('pk'); })
                },
                success: {
                    scope: this,
                    callback: function() {
                        this.getStore().reload();
                        //this.ownerCt.save();
                    }
                }
            }).removeItems(this.getEl());
        }
        else Ext.Msg.show({
            title: this.title,
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK,
            msg: 'Primeiro selecione os itens que deseja remover.'
        });
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
                        text: 'Novo',
                        scope: this,
                        handler: this.createItem,
                        iconCls: 'icon-diarias icon-add'
                    },
                    {
                        text: 'Editar',
                        scope: this,
                        handler: this.updateItem,
                        iconCls: 'icon-diarias icon-update'
                    },
                    {
                        text: 'Remover',
                        scope: this,
                        handler: this.removeItems,
                        iconCls: 'icon-diarias icon-remove'
                    },
                    '-',
                    '->',
                    '-',
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

        Ext.applyIf(cfg, {
            autoExpandColumn: 'autoExpandId',
            tbar: this.getToolbar(),
            bbar: new Ext.PagingToolbar({
                displayInfo: true,
                store: this.getStore()
            }),
            store: this.getStore(),
            listeners: {
                render: function(panel) {
                    new Ext.LoadMask(panel.getEl(), {
                        msg: 'Carregando lista de anexos...',
                        store: panel.getStore()
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
                },{
                    header: 'Estado',
                    dataIndex: 'state_display',
                    width: 120
                }
            ]
        });
        rh.registration.forminformation.ged.Grid.superclass.constructor.call(this, cfg);
        this._observeForm();
    }
});