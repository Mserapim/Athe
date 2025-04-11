Ext._define('corregedoria.scoretable.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.scoretable.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Tabela de Pontuação', dataIndex: 'score_table_display', id: 'autoExpandColumn', },
                    {header: 'Regulamentação', dataIndex: 'ordination', width: 400, },
                    {header: 'Início', dataIndex: 'initial_validity', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 75},
                    {header: 'Fim', dataIndex: 'final_validity', renderer: Ext.util.Format.dateRenderer('d/m/Y'), width: 75},
                    {header: '', xtype: 'actioncolumn', align: 'center', width: 50, scope: this, menuDisabled: true,
                        items: [
                            {
                                tooltip: 'Ver faixas',
                                icon: '/' + global.Context + '/static/images/format-list-ordered.png',
                                scope:this,
                                handler: function(grid, row, col) {
                                    grid.getSelectionModel().selectRow(row);
                                    var record = grid.getStore().getAt(row);
                                    Ext._create('corregedoria.scoretable.ListBandScoreTableWindow', {
                                        params: {
                                            scoretable: record.data.pk,
                                            scoretable_display: record.data.score_table_display
                                        }
                                    }).show();
                                }
                            },
                        ]
                    }
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.scoretable.Restful',
    'corregedoria.scoretable.Grid'
);
