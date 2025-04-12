/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.ParametroGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.avaliacao.ParametroWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: 'Conceito',
                        dataIndex: 'variavel_display',
                        id: 'autoExpandColumn'
                    },
                    {
                        header: 'Valor',
                        dataIndex: 'valor',
                        width: 70
                    }
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.avaliacao.ParametroRestful',
    'adm.patrimonio.avaliacao.ParametroGrid'
);
