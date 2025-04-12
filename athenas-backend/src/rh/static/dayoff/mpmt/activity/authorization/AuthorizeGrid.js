Ext._define('rh.dayoff.mpmt.activity.authorization.AuthorizeGrid', {
    extend: 'rh.dayoff.mpmt.activity.Grid',
    rest: 'rh.dayoff.mpmt.activity.authorization.AuthorizeRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.activity.authorization.AuthorizeRestful',
    'rh.dayoff.mpmt.activity.authorization.AuthorizeGrid'
);

