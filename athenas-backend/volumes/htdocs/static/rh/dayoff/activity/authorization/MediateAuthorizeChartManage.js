Ext._define('rh.dayoff.activity.authorization.MediateAuthorizeChartManage', {
    extend: 'rh.dayoff.activity.authorization.Manage',

    getActivityGrid: function (cfgManage, cfg) {
        if (!this._activityGrid) {
            this._activityGrid = rh.dayoff.activity.authorization.AuthorizeManage.superclass.getActivityGrid.call(this, cfgManage, {
                clsGrid: 'rh.dayoff.activity.authorization.MediateAuthorizeChartGrid',
                region: 'center',
                allowUpdate: false,
                columnAction: false,
                statusActivityMenu: [
                    {
                        text: 'Criado',
                        checked: true,
                        value: 1
                    },
                    {
                        text: 'Autorizado',
                        checked: true,
                        value: 2
                    },
                    {
                        text: 'Autorizado Chefe Mediato',
                        checked: false,
                        value: 6
                    },
                    {
                        text: 'Não autorizado',
                        checked: false,
                        value: 3
                    },
                    {
                        text: 'Homologado',
                        checked: false,
                        value: 4
                    },
                    {
                        text: 'Cancelado',
                        checked: false,
                        value: 5
                    },
                    {
                        text: 'Vendido',
                        checked: false,
                        value: 7
                    },
                ],
            });
        }
        return this._activityGrid;
    },

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Autorização(Mediato do Organograma)'
            }
        );

        rh.dayoff.activity.authorization.MediateAuthorizeChartManage.superclass.constructor.call(this, cfg);

    }
});

