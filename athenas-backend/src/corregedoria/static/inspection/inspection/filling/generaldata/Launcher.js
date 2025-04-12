
Ext._define('corregedoria.inspection.inspection.filling.generaldata.Launcher', {
    extend: 'Ext.Panel',

    getMemberOrganGrid: function(cfg) {
        if(!this._memberOrgan) {
            this._memberOrgan = Ext._create('corregedoria.inspection.inspection.filling.generaldata.memberorgan.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 530,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['edit', 'download', '-', 'search'],
                params: {inspection: cfg.values.inspection_id},
            });
            this.getMemberOrganGrid().setFilterProperty('inspection', cfg.values.inspection_id, 100);
        }
        return this._memberOrgan;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'DADOS GERAIS',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            labelWidth: 1,
            items: [
                this.getMemberOrganGrid(cfg),
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.generaldata.Launcher.superclass.constructor.call(this, cfg);

    }
});
