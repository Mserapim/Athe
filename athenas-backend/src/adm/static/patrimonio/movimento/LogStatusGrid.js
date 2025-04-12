/**
 *
 **/
Ext._define('adm.patrimonio.movimento.LogStatusGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.movimento.LogStatusWindow',

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = adm.patrimonio.movimento.LogStatusGrid.superclass.getToolbar.call(this, cfg);

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
                        width: 30,
                        menuDisabled: true,
                        renderer: adm.daily.rendererIconGrid
                    },
                    {
                        header: 'Estado',
                        dataIndex: 'status_display',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Atribuido por',
                        dataIndex: 'atribuido_por_unicode',
                        width: 160
                    },
                    {
                        header: 'Momento',
                        dataIndex: 'atribuido',
                        width: 115,
                        renderer: Ext.util.Format.dateRenderer('d/m/Y H:i')
                    }
                ]
            );

        return this._columnModel;
    },
});
