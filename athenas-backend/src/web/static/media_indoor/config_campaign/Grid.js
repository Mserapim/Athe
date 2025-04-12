Ext._define('media_indoor.config_campaign.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'media_indoor.config_campaign.Window',

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    { header: 'Cod', dataIndex: 'pk', width: 50, hidden: true },
                    { header: 'Grupo', dataIndex: 'group_unicode', width: 120, id: 'autoExpandColumn' },
                    { header: 'Campanha', dataIndex: 'campaign_unicode', width: 120 },
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'media_indoor.config_campaign.Restful',
    'media_indoor.config_campaign.Grid'
);

