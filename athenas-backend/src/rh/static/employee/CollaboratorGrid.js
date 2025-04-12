/**
 *
 **/
Ext._define('rh.employee.CollaboratorGrid', {
    extend: 'rh.employee.Grid',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {
                        header: 'Ativo',
                        dataIndex: 'ativo',
                        width: 70,
                        renderer: toolkit.util.formatIconYesNo,
                    },
                    {header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function(value) { return '<div style="text-align:right">' + value + '</div>'; }},
                    {header: 'Nome', dataIndex: 'pessoa_fisica_unicode', id: 'autoExpandColumn'},
                    {header: 'CPF', dataIndex: 'cpf', width: 100},
                    {header: 'Data Nascimento', dataIndex: 'date_born', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.employee.CollaboratorRestful',
    'rh.employee.CollaboratorGrid'
);
