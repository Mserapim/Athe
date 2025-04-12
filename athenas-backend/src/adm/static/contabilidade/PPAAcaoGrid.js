Ext._define('adm.contabilidade.PPAAcaoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'adm.contabilidade.PPAAcaoWindow',

    getColumnModel: function() {
        if (this._columnModel) {
            return this._columnModel;
        }

        this._columnModel = Ext._create(
            'Ext.grid.ColumnModel',
            [
                Ext._create('Ext.grid.RowNumberer'),
                { header: 'Id', dataIndex: 'id', width: 50, hidden: true },
                { header: 'Descrição', dataIndex: 'unicode', width: 150, hidden: true },
                { header: 'Código', dataIndex: 'cache_codigo', width: 105 },
                { header: 'Ano revisão', dataIndex: 'revision_year', width: 75 },
                { header: 'Título', dataIndex: 'titulo', id: 'autoExpandColumn' },
                { header: 'Fonte exclusiva', dataIndex: 'fonte_exclusiva_unicode', width: 160 },
                { header: 'Programa', dataIndex: 'programa_titulo', width: 150 },
            ]
        );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'adm.contabilidade.PPAAcaoRestful',
    'adm.contabilidade.PPAAcaoGrid'
);
