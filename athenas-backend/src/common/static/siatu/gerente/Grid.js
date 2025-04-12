/**
 *
 **/
Ext._define('common.siatu.gerente.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.gerente.Window',

    keywordFieldMessage: 'username',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Usuario', dataIndex: 'username', width: 110},
                    {header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    getToolbar: function(cfg) {
        if(!this._toolbar) {
            this._toolbar = common.siatu.gerente.Grid.superclass.getToolbar.call(this, cfg);

            this._toolbar.remove(this._toolbar.getComponent(1)); // Editar
            this._toolbar.remove(this._toolbar.getComponent(9)); // Download
        }

        return this._toolbar;
    },

    updateItem: function(record) {
    },

})