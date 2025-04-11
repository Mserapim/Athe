Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationItemManage', {
    extend: 'toolkit.widget.TabPanel',

    getMinuteSolicitationItemGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationItemGrid', {
                region: 'center',
                gridAutoLoad: false
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'MinuteSolicitationItem'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getMinuteSolicitationItemGrid(),
                ]
            }
        );

        planning.hiring.minutesolicitation.MinuteSolicitationItemManage.superclass.constructor.call(this, cfg);
    }
});

