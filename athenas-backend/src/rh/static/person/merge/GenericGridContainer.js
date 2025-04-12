Ext._define('rh.person.merge.GenericGridContainer', {
    extend: 'Ext.Panel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(
            cfg,
            {
                id: 'genericgridcontainer_' + cfg.name,
                scope: this,
                items: [
                    this.getGrid({
                        data: cfg.data,
                        fieldsStore: cfg.fieldsStore,
                        columns: cfg.columnsStore,
                        configOfTypeObj: cfg.configOfTypeObj,
                    })
                ]
            }
        );
        rh.person.merge.GenericGridContainer.superclass.constructor.call(this, cfg);
        this.windowCt.getGridArray().push(this.getGrid());
    },

    getGrid: function(cfg){
        if(!this._grid){
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {sm: undefined});
            this._grid = Ext._create('rh.person.merge.GenericGrid', cfg);
        }
        return this._grid;
    },
});
