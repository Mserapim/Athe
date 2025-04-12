/**
 *
 **/
Ext._define('rh.gfp.classcode.LoaderGrid', {
    extend: 'standard.classcode.Grid',

    restWindow: 'rh.gfp.classcode.LoaderWindow',
});

core.RestfulGrid.register(
    'rh.gfp.classcode.LoaderRestful',
    'rh.gfp.classcode.LoaderGrid'
);
