Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveGrid', {
    extend: 'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseGrid',

    rest: 'corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveRestful',

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveRestful',
    'corregedoria.inspection.inspection.filling.structure.personalmovement.EffetiveGrid'
);
