/**
 *
 **/
Ext._define('edocs.processo.situacao.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.situacao.Window',

    keywordFieldMessage: 'Situação',

    hideItemsToolbar: ['remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 100, sortable:true},
                    {header: 'Situação', dataIndex: 'nome', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg,{
            allowRemove: false,
            columnAction: false,
        })

        edocs.processo.situacao.Grid.superclass.constructor.call(this, cfg);
    }
    
})