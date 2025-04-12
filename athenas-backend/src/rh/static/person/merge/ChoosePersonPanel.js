Ext._define('rh.person.merge.ChoosePersonPanel', {
    extend: 'Ext.Panel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                id: 'chooseperson',
                scope: this,
                items: [
                    this.grid({data: cfg.person})
                ]
            }
        );
        rh.person.merge.ChoosePersonPanel.superclass.constructor.call(this, cfg);
    },

    grid: function(cfg){
        if(!this._grid){
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {sm: false});
            this._grid = Ext._create('rh.person.merge.GenericGrid', cfg);
        }
        return this._grid;
    },
});
