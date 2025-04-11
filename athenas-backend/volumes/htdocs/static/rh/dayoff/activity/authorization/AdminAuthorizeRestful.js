Ext._define('rh.dayoff.activity.authorization.AdminAuthorizeRestful', {
    extend: 'rh.dayoff.activity.Restful',

    resource: 'DAYOFFAdminAuthorization',

    constructor: function (cfg) {
        rh.dayoff.activity.authorization.AdminAuthorizeRestful.superclass.constructor.call(this, cfg);
    },
});
