Ext._define('standard.emailtemplate.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'standard.emailtemplate.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer',),
                    {header: 'Código Template', dataIndex: 'code', width: 250},
                    {header: 'Assunto', dataIndex: 'subject', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'standard.emailtemplate.Restful',
    'standard.emailtemplate.Grid'
);

