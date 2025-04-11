Ext._define("rh.person.naturalpersonhistory.Grid", {
    extend: "core.RestfulGrid",

    restWindow: "rh.person.naturalpersonhistory.Window",

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            gridAutoLoad: true,
            eSocialMenuValue: [
                {
                    name: 'enviar',
                    checked: true,
                    value: true,
                },
                {
                    name: 'nao_enviar',
                    checked: true,
                    value: false,
                },
            ],
        });

        this.eSocialMenuValue = cfg.eSocialMenuValue;

        rh.person.naturalpersonhistory.Grid.superclass.constructor.call(this, cfg);

        this.__setFilterPropertyDefault(this.gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad) {
        var eSocialMenuValueToFilter = [];

        this.eSocialMenuValue.forEach(
            function (item) {
                if (item.checked)
                    eSocialMenuValueToFilter.push(item.value);
            }
        );

        if (eSocialMenuValueToFilter.length > 0) {
            this.setFilterProperty('send_esocial__in', eSocialMenuValueToFilter, 1, false);
        }

        if (gridAutoLoad) {
            var store = this.getStore();
            store.load({});
        }

    },

    getESocialItemsMenu: function () {
        if (this._eSocialItems == undefined) {
            this._eSocialItems = [];
            for (var i = 0; i < this.eSocialMenuValue.length; i++) {
                if (this.eSocialMenuValue[i].name == 'enviar') {
                    this._eSocialItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'enviar',
                            groupMenu: 'e_social',
                            text: 'SIM',
                            checked: this.eSocialMenuValue[i].checked,
                            value: true,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterESocial();
                            }
                        })
                    );
                }
                if (this.eSocialMenuValue[i].name == 'nao_enviar') {
                    this._eSocialItems.push(
                        new Ext.menu.CheckItem({
                            hideOnClick: false,
                            name: 'nao_enviar',
                            groupMenu: 'e_social',
                            text: 'NÃO',
                            checked: this.eSocialMenuValue[i].checked,
                            value: false,
                            scope: this,
                            checkHandler: function (item, checked) {
                                this.filterESocial();
                            }
                        })
                    );
                }
            }
        }
        return this._eSocialItems;
    },

    filterESocial: function () {
        var values = [];
        this.getESocialItemsMenu().forEach(
            function (item) {
                if (item.checked)
                    values.push(item.value);
            }
        );
        this.setFilterProperty('send_esocial__in', values, 1, true);
        var store = this.getStore();
        store.load({});
    },

    getToolbar: function (cfg) {
        if(!this._toolbar) {
            var itensTollBar = this.getConfigItemsToolbar(cfg);

            itensTollBar.splice(6, 0, '-');
            itensTollBar.splice(
                7,
                0,
                {
                    text: 'Enviar ao e-Social?',
                    iconCls: 'icon-patrimonio icon-pat-filter',
                    menu: this.getESocialItemsMenu()
                }
            );

            this._toolbar = Ext._create('Ext.Toolbar', {
                style: cfg.toolbarStyle,
                items: itensTollBar,
            });

            if((this.toolbarHideLabel || cfg.toolbarHideLabel))
                this._toolbar.items.each(
                    function(item) {
                        item.tooltip = (item.tooltip || item.text);

                        if(item.text && core.nullValue(item.hideLabel, true))
                            item.text = null;
                    }
                );

        }

        return this._toolbar;
    },

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create("Ext.grid.ColumnModel", [
                Ext._create("Ext.grid.RowNumberer"),
                { header: "Cod", dataIndex: "pk", width: 50, hidden: true },
                {
                    header: "Enviar para eSocial?",
                    dataIndex: "send_esocial",
                    width: 150,
                    hidden: false,
                    renderer: toolkit.util.formatIconYesNo,
                },
                { header: "Descrição", dataIndex: "unicode", id: "autoExpandColumn" },
                { header: "Criado por", dataIndex: "created_by_unicode", width: 120, sortable: true, hidden: true },
                {
                    header: "Criado em",
                    dataIndex: "created_at",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    sortable: true,
                    hidden: true,
                },
                {
                    header: "Modificado por",
                    dataIndex: "modified_by_unicode",
                    width: 120,
                    sortable: true,
                    hidden: true,
                },
                {
                    header: "Modificado em",
                    dataIndex: "modified_at",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    sortable: true,
                    hidden: true,
                },
                { header: "Quando", dataIndex: "when", width: 90, renderer: Ext.util.Format.dateRenderer("d/m/Y") },
            ]);

        return this._columnModel;
    },
});

core.RestfulGrid.register("rh.person.naturalpersonhistory.Restful", "rh.person.naturalpersonhistory.Grid");
