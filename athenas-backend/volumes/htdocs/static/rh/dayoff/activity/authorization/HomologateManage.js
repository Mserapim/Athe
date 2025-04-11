Ext._define('rh.dayoff.activity.authorization.HomologateManage', {
    extend: 'rh.dayoff.activity.authorization.Manage',

    getActivityGrid: function (cfgManage, cfg) {
        if (!this._activityGrid) {
            this._activityGrid = rh.dayoff.activity.authorization.HomologateManage.superclass.getActivityGrid.call(
                this,
                cfgManage,
                {
                    clsGrid: "rh.dayoff.activity.authorization.HomologateGrid",
                    region: "center",
                    allowUpdate: false,
                    columnAction: false,
                    configOrderToolBar: [
                        "homologate",
                        "-",
                        "detail",
                        "-",
                        "search",
                        "GroupFilter",
                        "configurationFilter",
                        "typeOfFilter",
                        "->",
                        "download",
                    ],
                    externalCallback: cfgManage.externalCallback,
                    statusActivityMenu: [
                        {
                            text: "Criado",
                            checked: true,
                            value: 1,
                        },
                        {
                            text: "Autorizado",
                            checked: true,
                            value: 2,
                        },
                        {
                            text: "Autorizado Chefe Mediato",
                            checked: true,
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
                title: 'Homologação',
            }
        );

        rh.dayoff.activity.authorization.HomologateManage.superclass.constructor.call(this, cfg);
    }
});

