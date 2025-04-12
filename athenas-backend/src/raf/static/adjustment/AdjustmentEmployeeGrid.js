Ext._define('raf.adjustment.AdjustmentEmployeeGrid', {
    extend: 'raf.adjustment.BaseGrid',

    restWindow: 'raf.adjustment.AdjustmentEmployeeWindow',

    configOrderToolBar: ['add', 'edit', '->', 'cancelAdjustment'],


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        raf.adjustment.AdjustmentEmployeeGrid.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'raf.adjustment.AdjustmentEmployeeRestful',
    'raf.adjustment.AdjustmentEmployeeGrid'
);
