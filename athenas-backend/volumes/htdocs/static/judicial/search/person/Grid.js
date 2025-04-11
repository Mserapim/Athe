Ext._define('judicial.search.person.Grid', {
    extend: 'judicial.OutCourtLawsuitGrid',

    restWindow: 'judicial.search.person.Window',

    updateItem: function (record) {},
    
    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 90,
                        menuDisabled: true,
                        renderer: core.rendererIconGrid,
                        hidden: true
                    },
                    { sortable: true, header: 'Código', dataIndex: 'origin_codigo', id: 'autoExpandColumn', hidden: true },
                    { sortable: true, header: 'Procedimento', dataIndex: 'cache_number', width: 120 },
                    { sortable: true, header: 'Título', dataIndex: 'title', width: 260 },
                    { sortable: true, header: 'Situação', dataIndex: 'status' },
                    { sortable: true, header: 'Tipo do Procedimento', dataIndex: 'type_lawsuit_display', width: 165 },
                    { sortable: true, header: 'Localização', dataIndex: 'current_location_unicode', width: 325 },
                    { sortable: true, header: 'Interessados', dataIndex: 'interesteds', width: 260 },
                    { sortable: true, header: 'Investigados', dataIndex: 'blokes', width: 260 }
                    
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(
            cfg,
            {
                viewConfig: {
                    getRowClass: function (record, rowIndex, rp, ds) {
                        var classes = ['grid-line-height-150'];
                        return classes.join(' ');
                    }
                }
            }
        );
        judicial.search.person.Grid.superclass.constructor.call(this, cfg);
    }
});

core.RestfulGrid.register(
    'judicial.search.person.Restful',
    'judicial.search.person.Grid'
);

