/**
 *
 **/
Ext._define('rh.gfp.classcode.CalculationGrid', {
    extend: 'standard.classcode.Grid',

    restWindow: 'rh.gfp.classcode.CalculationWindow',
});

core.RestfulGrid.register(
    'rh.gfp.classcode.CalculationRestful',
    'rh.gfp.classcode.CalculationGrid'
);
