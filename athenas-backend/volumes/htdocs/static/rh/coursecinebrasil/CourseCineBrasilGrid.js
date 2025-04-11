 Ext._define('rh.coursecinebrasil.CourseCineBrasilGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.coursecinebrasil.CourseCineBrasilWindow',

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Código', dataIndex: 'code', width: 90},
                    {header: 'Rótulo', dataIndex: 'label', id: 'autoExpandColumn'},
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.coursecinebrasil.CourseCineBrasilRestful',
    'rh.coursecinebrasil.CourseCineBrasilGrid'
);

