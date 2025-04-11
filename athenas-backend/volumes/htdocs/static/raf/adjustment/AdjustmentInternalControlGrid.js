Ext._define('raf.adjustment.AdjustmentInternalControlGrid', {
    extend: 'raf.adjustment.BaseGrid',

    restWindow: 'raf.adjustment.AdjustmentInternalControlWindow',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'accept', 'requestInformation', 'rejected', '->', '-'],

});

core.RestfulGrid.register(
    'raf.adjustment.AdjustmentInternalControlRestful',
    'raf.adjustment.AdjustmentInternalControlGrid'
);
