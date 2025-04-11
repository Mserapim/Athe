Ext._define('rh.dayoff.mpmt.activity.authorization.MediateAuthorizeGrid', {
    extend: 'rh.dayoff.mpmt.activity.Grid',
    rest: 'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeRestful',
    'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeGrid'
);
