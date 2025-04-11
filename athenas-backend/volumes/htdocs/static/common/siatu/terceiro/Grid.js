/**
 *
 **/
Ext._define('common.siatu.terceiro.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'common.siatu.terceiro.Window',

    keywordFieldMessage: 'Nome',

    cleanFilter: function() {
        this._filter = [1];
        this.setFilter([
            {property: 'status__in', value: this._filter, stage: 1000},
        ]);
    },

    getColumnModel: function(){
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'busy', width: 20, renderer: common.siatu.rendererIconGrid},
                    {header: 'Nome', dataIndex: 'nome', width: 180, sortable:true},
                    {header: 'Telefone', dataIndex: 'telefone', width: 100},
                    {header: 'Endereço', dataIndex: 'endereco', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.cleanFilter()

        common.siatu.terceiro.Grid.superclass.constructor.call(this, cfg);
    }

})
