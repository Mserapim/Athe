Ext._define('rh.dayoff.activity.authorization.MediateAuthorizeGrid', {
    extend: 'rh.dayoff.activity.Grid',
    rest: 'rh.dayoff.activity.authorization.MediateAuthorizeRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.activity.authorization.MediateAuthorizeRestful',
    'rh.dayoff.activity.authorization.MediateAuthorizeGrid'
);
