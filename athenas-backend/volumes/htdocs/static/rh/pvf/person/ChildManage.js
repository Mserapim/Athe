Ext._define('rh.pvf.person.ChildManage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function(cfg) {
        if(!this._grid) {
            this._grid = Ext._create('rh.pvf.person.ChildGrid', {
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
                title: 'pessoas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid(),
                ]
            }
        );

        rh.pvf.person.ChildManage.superclass.constructor.call(this, cfg);
    }
});