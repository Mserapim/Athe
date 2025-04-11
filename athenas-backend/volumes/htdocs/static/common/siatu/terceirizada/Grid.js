/**
 *
 **/
Ext._define('common.siatu.terceirizada.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.terceirizada.Window',

    keywordFieldMessage: 'Nome',

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Nome', dataIndex: 'nome', width: 250, sortable: true},
                    {header: 'Cnpj', dataIndex: 'cnpj', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        common.siatu.terceirizada.Grid.superclass.constructor.call(this, cfg);
    }
    
})