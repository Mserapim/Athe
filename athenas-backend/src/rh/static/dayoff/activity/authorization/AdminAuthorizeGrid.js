Ext._define('rh.dayoff.activity.authorization.AdminAuthorizeGrid', {
    extend: 'rh.dayoff.activity.Grid',

    rest: 'rh.dayoff.activity.authorization.AdminAuthorizeRestful',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            type_window: 'admin'
        });

        rh.dayoff.activity.authorization.AdminAuthorizeGrid.superclass.constructor.call(this, cfg);
    },

    getFilterMenu: function () {
        if (!this._filterMenu)
            this._filterMenu = rh.dayoff.activity.authorization.AdminAuthorizeGrid.superclass.getFilterMenu.call(this, {}).concat(
                this.getTypeByPossessionMenu()
            );
        return this._filterMenu;
    },

    togglePossessionType: function (possession) {
        if (!this._filterPossessionType)
            this._filterPossessionType = ['M', 'S'];

        if (this._filterPossessionType.indexOf(possession) >= 0)
            this._filterPossessionType.remove(possession);
        else
            this._filterPossessionType.push(possession);

        this.setFilterProperty('acquisition_period__employee__tipo__in', this._filterPossessionType, 3001);
    },

    getTypeByPossessionMenu: function () {
        return [{
            text: 'Por Tipo de Posse',
            menu: [
                {
                    text: 'Membros',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function () {
                        this.togglePossessionType('M')
                    }
                },
                {
                    text: 'Servidores',
                    checked: true,
                    scope: this,
                    hideOnClick: false,
                    handler: function () {
                        this.togglePossessionType('S')
                    }
                },
            ]
        }]
    },

    authorize: function (authorize) {
        var selected = this.getSelectionModel().getSelected();
        var _manage = this;
        if (!selected) {
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Selecione um item'
            });
        }
        else {
            Ext._create('rh.dayoff.activity.authorization.AdminAuthorizeWindow', {
                title: 'Autorização',
                scope: this,
                params: {
                    actionCustom: 'authorize',
                    authorize: authorize,
                    activity: selected.get('pk'),
                },
                values: {
                    mediate_authorization_by: selected.get('mediate_authorization_by'),
                    immediate_authorization_by: selected.get('immediate_authorization_by'),
                },
                externalCallback: {
                    fn: function () {
                        _manage.getStore().reload();
                    },
                    scope: this
                }
            }).show();
        }
    }
});

core.RestfulGrid.register(
    'rh.dayoff.activity.authorization.AdminAuthorizeRestful',
    'rh.dayoff.activity.authorization.AdminAuthorizeGrid'
);

