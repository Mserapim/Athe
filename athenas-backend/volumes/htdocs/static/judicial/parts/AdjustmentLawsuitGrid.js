
Ext._define('judicial.parts.AdjustmentLawsuitGrid', {
    extend: 'judicial.PartLawsuitGrid',

    restWindow: 'judicial.parts.AdjustmentLawsuitWindow',

});

core.RestfulGrid.register(
    'judicial.parts.AdjustmentLawsuitRestful',
    'judicial.parts.AdjustmentLawsuitGrid'
);
