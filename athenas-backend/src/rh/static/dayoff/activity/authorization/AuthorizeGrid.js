Ext._define('rh.dayoff.activity.authorization.AuthorizeGrid', {
    extend: 'rh.dayoff.activity.Grid',
    rest: 'rh.dayoff.activity.authorization.AuthorizeRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.activity.authorization.AuthorizeRestful',
    'rh.dayoff.activity.authorization.AuthorizeGrid'
);

