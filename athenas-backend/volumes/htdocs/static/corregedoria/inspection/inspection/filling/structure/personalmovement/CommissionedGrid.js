Ext._define('corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedGrid', {
    extend: 'corregedoria.inspection.inspection.filling.structure.personalmovement.BaseGrid',

    rest: 'corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedRestful',

});

core.RestfulGrid.register(
    'corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedRestful',
    'corregedoria.inspection.inspection.filling.structure.personalmovement.CommissionedGrid'
);
