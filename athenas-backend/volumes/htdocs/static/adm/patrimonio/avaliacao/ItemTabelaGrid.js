/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ItemTabelaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.avaliacao.ItemTabelaWindow',

    statics: {
        numberRenderer: function(value) {
            return '<div style="text-align:center">' + value + '</div>';
        },
        percentRenderer: function(value) {
            return '<div style="text-align:center">' + value + ' %</div>';
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: 'Descrição',
                        dataIndex: 'unicode',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'VU',
                        dataIndex: 'vida_util',
                        width: 70,
                        renderer: adm.patrimonio.avaliacao.ItemTabelaGrid.numberRenderer
                    },
                    {
                        header: 'TD',
                        dataIndex: 'depreciacao',
                        width: 70,
                        renderer: adm.patrimonio.avaliacao.ItemTabelaGrid.percentRenderer
                    },
                    {
                        header: 'VR',
                        dataIndex: 'residual',
                        width: 70,
                        renderer: adm.patrimonio.avaliacao.ItemTabelaGrid.percentRenderer
                    }
                ]
            );

        return this._columnModel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(cfg, {
            viewConfig: {
                scope: this,
                getRowClass: function(record) {
                    if(record.get('tipo') == 1) {
                        return 'x-grid3-gray';
                    }
                }
            }
        });

        adm.patrimonio.avaliacao.ItemTabelaGrid.superclass.constructor.call(this, cfg);
    }
});
