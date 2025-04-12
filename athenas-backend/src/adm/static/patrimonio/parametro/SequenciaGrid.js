/**
 *
 **/
Ext._define('adm.patrimonio.parametro.SequenciaGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.patrimonio.parametro.SequenciaWindow',

    keywordFieldMessage: 'Descrição ou código.',

    rendererSequencia: function(value) {
        var text = new String(value);

        while(text.length < 6)
            text = '0' + text;

        return '<div style="text-align:center">' + text + '</div>';
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 60, hidden: true},
                    {header: 'Reg. Atual', dataIndex: 'proximo', width: 70, renderer: this.rendererSequencia},
                    {header: 'Descrição', dataIndex: 'titulo', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'adm.patrimonio.parametro.SequenciaRestful',
    'adm.patrimonio.parametro.SequenciaGrid'
);
