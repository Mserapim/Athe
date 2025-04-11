Ext._define('rh.dayoff.mpmt.acquisitionperiod.ManageAdmin', {
    extend: 'rh.dayoff.mpmt.acquisitionperiod.Manage',

    openActivityWindow: function (actionCustom, title, type_window) {
        rh.dayoff.mpmt.acquisitionperiod.ManageAdmin.superclass.openActivityWindow.call(this, actionCustom, title, 'admin');
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                title: 'Período Aquisitivo - Admin'
            }
        );

        rh.dayoff.mpmt.acquisitionperiod.ManageAdmin.superclass.constructor.call(this, cfg);
    },

    getActivityGrid: function (cfgManage, cfg) {
        if (!this._activityGrid) {
            Ext.apply(
                cfg,
                {
                    clsGrid: 'rh.dayoff.mpmt.activity.authorization.AdminAuthorizeGrid',
                    resource: 'DAYOFFAdminAuthorizationMPMT',
                    region: 'center',
                    allowUpdate: true,
                    // columnAction: true,
                    hideActions: ['remove', 'copy'],
                    hideItemsToolbar: ['add', 'remove'],
                    configOrderToolBar: ["delete","-","search","->","download",],
                    statusActivityMenu: [
                        {text: 'Criado',checked: true,value: 1},
                        {text: 'Autorizado',checked: true,value: 2},
                        {text: 'Autorizado Chefe Mediato',checked: true,value: 6},
                        {text: 'Não autorizado',checked: false,value: 3},
                        {text: 'Homologado',checked: true,value: 4},
                        {text: 'Cancelado',checked: false,value: 5},
                        {text: 'Vendido',checked: false,value: 7},
                    ],
                }
            );
            this._activityGrid = rh.dayoff.mpmt.acquisitionperiod.ManageAdmin.superclass.getActivityGrid.call(this, cfgManage, cfg);
        }
        return this._activityGrid;
    },
});
