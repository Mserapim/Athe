Ext._define('rh.dayoff.mpmt.acquisitionperiod.attachment.Grid', {
    extend: 'core.RestfulGrid',
    restWindow: 'rh.dayoff.mpmt.acquisitionperiod.attachment.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'download', '-', 'search'],

    constructor: function(cfg) {
        rh.dayoff.mpmt.acquisitionperiod.attachment.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Período aquisitivo', dataIndex: 'acquisition_period_unicode', width: 150, id: 'autoExpandColumn' },
                    { header: 'Descrição', dataIndex: 'description', width: 70 },
                    { header: 'Informação', dataIndex: 'information', width: 70 },
                    { header: 'Data início', dataIndex: 'date_start', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Data fim', dataIndex: 'date_end', width: 70, renderer: Ext.util.Format.dateRenderer('d/m/Y') },
                    { header: 'Qtd. de dias direito', dataIndex: 'days_law', width: 70 },
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.acquisitionperiod.attachment.Restful',
    'rh.dayoff.mpmt.acquisitionperiod.attachment.Grid'
);