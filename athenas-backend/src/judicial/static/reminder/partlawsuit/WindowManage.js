Ext._define('judicial.reminder.partlawsuit.WindowManage', {
    extend: 'judicial.reminder.WindowManage',

    gridClass: 'judicial.reminder.partlawsuit.Grid',

    getReminderGrid: function (cfg) {
        if (!this._grid) {
            this._grid = judicial.reminder.partlawsuit.WindowManage.superclass.getReminderGrid.call(this, cfg);
        }

        this._grid.setParam('part_lawsuit', cfg.params.part_lawsuit);
        this._grid.setFilterProperty('part_lawsuit', cfg.params.part_lawsuit, 100);
        this._grid.setFilterProperty('deactivated_by__isnull', true, 101);
        this._grid.getStore().reload();

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, { title: 'Lembretes de Documento' });

        judicial.reminder.lawsuit.WindowManage.superclass.constructor.call(this, cfg);
    }
});
