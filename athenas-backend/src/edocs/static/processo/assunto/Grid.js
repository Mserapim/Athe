/**
 *
 **/
Ext._define('edocs.processo.assunto.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'edocs.processo.assunto.Window',

    keywordFieldMessage: 'Assunto',

    hideItemsToolbar: ['remove', 'download'],

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    {header: 'Chave', dataIndex: 'pk', width: 100, sortable:true},
                    {header: 'Assunto', dataIndex: 'nome', id: 'autoExpandColumn'},
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

        edocs.processo.assunto.Grid.superclass.constructor.call(this, cfg);
    }
    
});

core.RestfulGrid.register(
    'edocs.processo.assunto.Restful',
    'edocs.processo.assunto.Grid'
);