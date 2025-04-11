Ext._define('rh.dayoff.mpmt.activity.authorization.MediateAuthorizeChartGrid', {
    extend: 'rh.dayoff.mpmt.activity.Grid',
    rest: 'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeChartRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeChartRestful',
    'rh.dayoff.mpmt.activity.authorization.MediateAuthorizeChartGrid'
);
