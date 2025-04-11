Ext._define('judicial.reminder.lawsuit.WindowManage', {
    extend: 'judicial.reminder.WindowManage',

    title: 'Lembretes de Procedimento',

    gridClass: 'judicial.reminder.lawsuit.Grid',

    getReminderGrid: function (cfg) {
        if (!this._grid) {
            this._grid = judicial.reminder.partlawsuit.WindowManage.superclass.getReminderGrid.call(this, cfg);
        }

        this._grid.setParam('lawsuit', cfg.params.lawsuit);
        this._grid.setFilterProperty('lawsuit', cfg.params.lawsuit, 100);
        this._grid.setFilterProperty('deactivated_by__isnull', true, 101);
        this._grid.getStore().reload();

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, { title: 'Lembretes de Procedimento' });

        judicial.reminder.lawsuit.WindowManage.superclass.constructor.call(this, cfg);
    }
});
