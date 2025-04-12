Ext._define('rh.dayoff.activity.authorization.AdminAuthorizeManage', {
    extend: 'rh.dayoff.activity.authorization.Manage',

    getActivityGrid: function (cfgManage, cfg) {
        if (!this._activityGrid) {
            this._activityGrid = rh.dayoff.activity.authorization.AuthorizeManage.superclass.getActivityGrid.call(
                this,
                cfgManage,
                {
                    clsGrid: "rh.dayoff.activity.authorization.AdminAuthorizeGrid",
                    resource: "DAYOFFAdminAuthorization",
                    region: "center",
                    allowUpdate: false,
                    columnAction: false,
                    configOrderToolBar: [
                        "authorize",
                        "-",
                        "detail",
                        "-",
                        "notificate",
                        "-",
                        "cancel",
                        "-",
                        "homologate",
                        "-",
                        "search",
                        "GroupFilter",
                        "configurationFilter",
                        "typeOfFilter",
                        "->",
                        "download",
                    ],
                    statusActivityMenu: [
                        {
                            text: "Criado",
                            checked: true,
                            value: 1,
                        },
                        {
                            text: "Autorizado",
                            checked: false,
                            value: 2,
                        },
                        {
                            text: "Autorizado Chefe Mediato",
                            checked: false,
                            value: 6,
                        },
                        {
                            text: "Não autorizado",
                            checked: false,
                            value: 3,
                        },
                        {
                            text: "Homologado",
                            checked: false,
                            value: 4,
                        },
                        {
                            text: "Cancelado",
                            checked: false,
                            value: 5,
                        },
                        {
                            text: "Vendido",
                            checked: false,
                            value: 7,
                        },
                    ],
                }
            );
        }
        return this._activityGrid;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Autorização(Admin)'
            }
        );

        rh.dayoff.activity.authorization.AdminAuthorizeManage.superclass.constructor.call(this, cfg);
    }
});

