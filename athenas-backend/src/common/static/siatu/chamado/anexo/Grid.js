/**
 *
 **/
Ext._define('common.siatu.chamado.anexo.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.chamado.anexo.Window',

    configOrderToolBar: ['add', 'edit', 'remove', 'openDown','search', '-', '->'],

    // keywordFieldMessage: 'Nome',

    getOpenDownAction: function(){
        if(!this.openManager)
            this.openManager = Ext._create('Ext.Button', {
                text: 'Download',
                scope: this,
                iconCls: 'icon-siatu icon-siatu-move-down',
                handler: this.downloadItem
            });

        return this.openManager;
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Usuário', dataIndex: 'usuario', width: 150},
                    {header: 'Arquivo', dataIndex: 'filename', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

// updateItem sobrescrita:
// adicionando disableSave para visualizar informações apenas
    updateItem: function(record) {
        if(record instanceof Ext.Button)
            record = undefined;

        var selected = core.nullValue(record, this.getSelectionModel().getSelected());

        if(selected) {
            this.factoryRestfulWindow({
                action: 'update',
                oId: selected.get('pk'),
                values: selected.data,
                params: this.getParams(),
                disableSave: this.disableSave,
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
            if(this.disableSave)
                Ext.Msg.show({
                    title: 'Informações',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Primeiro selecione um item para obter informações.'
                });
            else
                Ext.Msg.show({
                    title: 'Editando',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Primeiro selecione um item para editar.'
                });
    },

    downloadItem: function() {
        var selected = this.getSelectionModel().getSelected()
        if (selected)
            open(selected.get('permalink'), "_self");
        else
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item!'
            });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        common.siatu.chamado.anexo.Grid.superclass.constructor.call(this, cfg);
    }

})
