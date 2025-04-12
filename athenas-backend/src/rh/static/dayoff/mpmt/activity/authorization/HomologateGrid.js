Ext._define('rh.dayoff.mpmt.activity.authorization.HomologateGrid', {
    extend: 'rh.dayoff.mpmt.activity.Grid',
    rest: 'rh.dayoff.mpmt.activity.authorization.HomologateRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.activity.authorization.HomologateRestful',
    'rh.dayoff.mpmt.activity.authorization.HomologateGrid'
);

