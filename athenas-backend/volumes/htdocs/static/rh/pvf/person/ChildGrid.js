Ext._define('rh.pvf.person.ChildGrid', {
    extend: 'rh.pvf.person.Grid',

    restWindow: 'rh.pvf.person.ChildWindow',

});
core.RestfulGrid.register(
    'rh.pvf.person.ChildRestful',
    'rh.pvf.person.ChildGrid'
);    