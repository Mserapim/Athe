/**
 *
 **/
Ext._define('cif.schedule.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getSchedule: function() {
        if(!this.schedule) {
            this.schedule = Ext._create('cif.schedule.ScheduleGrid', {
                region: 'center',
            });
        }

        return this.schedule;
    },
    
    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Horários'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getSchedule(),
                ]
            }
        );

        cif.schedule.Manage.superclass.constructor.call(this, cfg);
    }
});
