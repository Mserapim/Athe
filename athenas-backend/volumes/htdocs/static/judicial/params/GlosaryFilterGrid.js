Ext._define('judicial.params.GlosaryFilterGrid', {
    extend: 'judicial.params.GlosaryGrid',

    rest: 'judicial.params.GlosaryFilterRestful'
    // restWindow: 'judicial.params.GlosaryFilterWindow',

});

core.RestfulGrid.register(
    'judicial.params.GlosaryFilterRestful',
    'judicial.params.GlosaryFilterGrid'
);
