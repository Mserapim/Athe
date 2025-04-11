/**
 *
 **/
Ext._define('edocs.processo.movprocessoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.movprocessoWindow',

    keywordFieldMessage: '',

    hideItemsToolbar: ['add','edit', 'search', 'remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Processo', dataIndex: 'codigo_processo', width: 180},
                    {header: 'Volume', dataIndex: 'volume', width: 60},
                    {header: 'Página', dataIndex: 'paginas', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        return undefined;
    },

     getFooterbar: function(cfg) {
        return undefined;
    },

    updateItem: function(record) {
        if(!this.allowUpdate)
            return

        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('id'),
                values: selected.data,
                params: this.getParams(),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Editando',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item para editar.'
            });
    },

    getActionColumn: function() {
        if(!this._actionColumn)
            this._actionColumn = Ext._create('Ext.grid.ActionColumn', {
                width: 70,
                scope: this,
                items: [
                    {
                        iconCls: 'icon-16px icon-core icon-core-edit',
                        tooltip: 'Editar item.',
                        handler: function(action, index) {
                            var record = this.getStore().getAt(index);
                            record && this.updateItem(record);
                        }
                    }
                ]
            });

        return this._actionColumn;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg,{
            allowCreate: false,
            allowRemove: false,
        })

        edocs.processo.movprocessoGrid.superclass.constructor.call(this, cfg);
    }

})
