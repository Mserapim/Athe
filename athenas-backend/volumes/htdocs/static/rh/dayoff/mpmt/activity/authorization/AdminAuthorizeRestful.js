Ext._define('rh.dayoff.mpmt.activity.authorization.AdminAuthorizeRestful', {
    extend: 'rh.dayoff.mpmt.activity.Restful',

    resource: 'DAYOFFAdminAuthorizationMPMT',

    constructor: function (cfg) {
        rh.dayoff.mpmt.activity.authorization.AdminAuthorizeRestful.superclass.constructor.call(this, cfg);
    },
});
