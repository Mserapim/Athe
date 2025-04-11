Ext._define('corregedoria.inspection.inspection.filling.generaldata.memberorgan.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'corregedoria.inspection.inspection.filling.generaldata.memberorgan.Window',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Membro', dataIndex: 'employee_unicode', id: 'autoExpandColumn', },
                    {header: 'Papel', dataIndex: 'member_role_display', width: 250, },
                    {header: 'Atuação Exclusiva', renderer: toolkit.util.formatIconYesNo, dataIndex: 'exclusive', width: 100, },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.generaldata.memberorgan.Restful',
    'corregedoria.inspection.inspection.filling.generaldata.memberorgan.Grid'
);
