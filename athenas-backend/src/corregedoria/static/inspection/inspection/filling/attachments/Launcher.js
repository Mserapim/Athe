
Ext._define('corregedoria.inspection.inspection.filling.attachments.Launcher', {
    extend: 'Ext.Panel',

    getAttachmentsGrid: function(cfg) {
        if(!this._attachmentsGrid) {
            this._attachmentsGrid = Ext._create('corregedoria.inspection.inspection.filling.attachments.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 530,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getAttachmentsGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._attachmentsGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'ANEXOS',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            items: [
                this.getAttachmentsGrid(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.attachments.Launcher.superclass.constructor.call(this, cfg);

    }
});
