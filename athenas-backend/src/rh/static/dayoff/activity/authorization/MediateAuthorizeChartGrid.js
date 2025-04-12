Ext._define('rh.dayoff.activity.authorization.MediateAuthorizeChartGrid', {
    extend: 'rh.dayoff.activity.Grid',
    rest: 'rh.dayoff.activity.authorization.MediateAuthorizeChartRestful',
});

core.RestfulGrid.register(
    'rh.dayoff.activity.authorization.MediateAuthorizeChartRestful',
    'rh.dayoff.activity.authorization.MediateAuthorizeChartGrid'
);
