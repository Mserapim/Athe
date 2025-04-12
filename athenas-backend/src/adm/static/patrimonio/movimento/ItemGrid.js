/**
 *
 **/
Ext._define('adm.patrimonio.movimento.ItemGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.movimento.ItemWindow',

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.movimento.ItemGrid.superclass.getToolbar.call(this, cfg);

            this._toolbar.remove(this._toolbar.getComponent(0)); // Adicionar
            this._toolbar.remove(this._toolbar.getComponent(0)); // Editar
            this._toolbar.remove(this._toolbar.getComponent(0)); // Remover
            this._toolbar.remove(this._toolbar.getComponent(0)); // Separador
        }

        return this._toolbar;
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 60,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Plaqueta',
                        dataIndex: 'patrimonio_plaqueta',
                        width: 70
                    },
                    {
                        header: 'Especie',
                        dataIndex: 'patrimonio_unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Conservação',
                        dataIndex: 'patrimonio_conservacao',
                        width: 100
                    }
                ]
            );

        return this._columnModel;
    },

    defaultClickFunction: function() {
        var selected = this.getSelectionModel().getSelected();

        if(selected) {
            Ext._create('adm.patrimonio.PatrimonioRestfulWindow', {
                action: 'update',
                values: 'remote',
                scope: this,
                oId: selected.get('patrimonio')
            }).show();
        }
        else
            Ext.Msg.show({
                title: 'Visualizando Patrimonio',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Primeiro selecione um item'
            });
    }
});
