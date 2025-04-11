Ext._define('raf.adjustment.AdjustmentInternalControlWindow', {
    extend: 'raf.adjustment.BaseWindow',

    rest: 'raf.adjustment.AdjustmentInternalControlRestful',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        raf.adjustment.AdjustmentInternalControlWindow.superclass.constructor.call(this, cfg);
    }

});
