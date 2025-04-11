Ext._define("rh.dayoff.acquisitionperiod.Grid", {
    extend: "core.RestfulGrid",

    restWindow: "rh.dayoff.acquisitionperiod.Window",

    configOrderToolBar: [
        "add",
        "edit",
        "remove",
        "-",
        "release",
        "-",
        "updateAP",
        "-",
        "LockPeriod",
        "-",
        "sell",
        "-",
        "search",
        "groupFilter",
        "configurationFilter",
        "typeOfFilter",
        "->",
    ],

    keywordFieldWidth: 220,

    autoExpandMax: 300,

    actionColumnWidth: 120,

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});
        var gridAutoLoad = cfg.gridAutoLoad == undefined ? true : cfg.gridAutoLoad;
        Ext.apply(cfg, { gridAutoLoad: false });
        Ext.applyIf(cfg, {
            statusItemsMenuConf: [
                {
                    text: "Aguardando Liberação p/ Marcação",
                    checked: true,
                    value: 1,
                },
                {
                    text: "Em Andamento",
                    checked: true,
                    value: 2,
                },
                {
                    text: "Concluído",
                    checked: true,
                    value: 4,
                },
                {
                    text: "Indenizado Total ou Parcialmente",
                    checked: true,
                    value: 8,
                },
                {
                    text: "Prescrito",
                    checked: true,
                    value: 12,
                },
            ],
            blockedItemsMenuConf: [
                {
                    text: "Bloqueado",
                    checked: true,
                    value: true,
                },
                {
                    text: "Desbloqueado",
                    checked: true,
                    value: false,
                },
            ],
            pendencyItemsMenuConf: [
                {
                    text: "Com pendência",
                    checked: true,
                    value: true,
                },
                {
                    text: "Sem pendência",
                    checked: true,
                    value: false,
                },
            ],
        });

        this.statusItemsMenuConf = cfg.statusItemsMenuConf;
        this.blockedItemsMenuConf = cfg.blockedItemsMenuConf;
        this.pendencyItemsMenuConf = cfg.pendencyItemsMenuConf;
        rh.dayoff.acquisitionperiod.Grid.superclass.constructor.call(this, cfg);
        this.__setFilterPropertyDefault(gridAutoLoad);
    },

    __setFilterPropertyDefault: function (gridAutoLoad) {
        var _grid = this;
        var statusMenu = [];
        var blockedMenu = [];
        var pendencyMenu = [];
        this.getStatusMenuItems().forEach(function (item) {
            if (item.checked) statusMenu.push(item.value);
        });
        this.getBlockedMenuItems().forEach(function (item) {
            if (item.checked) blockedMenu.push(item.value);
        });
        this.getPendencyMenuItems().forEach(function (item) {
            if (item.checked) pendencyMenu.push(item.value);
        });

        if (statusMenu.length > 0) {
            this.setFilterProperty("status__in", statusMenu, 200, false);
        }
        if (blockedMenu.length > 0) {
            this.setFilterProperty("blocked__in", blockedMenu, 300, false);
        }
        if (pendencyMenu.length > 0) {
            this.setFilterProperty("pendency__in", pendencyMenu, 400, false);
        }

        if (gridAutoLoad) {
            var store = this.getStore();
            store.load({});
        }
    },

    getLockPeriodAction: function (cfg) {
        if (!this._lockAction) {
            this._lockAction = Ext._create("Ext.Button", {
                text: "Bloqueio/Desbloqueio",
                iconCls: "icon-cif icon-cif-manager",
                scope: this,
                menu: [
                    {
                        text: "Bloquear",
                        scope: this,
                        iconCls: "icon-cif icon-cif-lock",
                        handler: function () {
                            this.getLockUnlock(true);
                        },
                    },
                    {
                        text: "Desbloquear",
                        scope: this,
                        iconCls: "icon-cif icon-cif-unlock",
                        handler: function () {
                            this.getLockUnlock(false);
                        },
                    },
                ],
            });
        }

        return this._lockAction;
    },

    getLockUnlock: function (lock) {
        var sels = this.getSelectionModel().getSelections();
        var pks = [];
        Ext.each(sels, function (record) {
            pks.push(record.get("pk"));
        });

        Ext.Msg.show({
            scope: this,
            title: "PERGUNTA",
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.OKCANCEL,
            msg: "Confirmar Ação ?",
            fn: function (button) {
                if (button == "ok") {
                    var params = {
                        actionCustom: "block_periods",
                        pks: pks,
                        lock: lock,
                    };

                    this._process(params);
                }
            },
        });
    },

    getGroupFilterAction: function () {
        if (!this._groupFilter)
            this._groupFilter = Ext._create("rh.dayoff.acquisitionperiod.GroupFilterAction", { objToFilter: this });
        return this._groupFilter;
    },

    getConfigurationFilterAction: function () {
        if (!this._configurationFilter)
            this._configurationFilter = Ext._create("rh.dayoff.acquisitionperiod.ConfigurationFilterAction", {
                objToFilter: this,
            });
        return this._configurationFilter;
    },

    getTypeOfFilterAction: function () {
        if (!this._typeOfFilterFilter)
            this._typeOfFilterFilter = Ext._create("rh.dayoff.acquisitionperiod.TypeOfFilterAction", {
                objToFilter: this,
            });
        return this._typeOfFilterFilter;
    },

    getHomologateWindow: function (cfg) {
        var _windowHomologateAP = Ext._create("Ext.Window", {
            title: "Homologar Periodos Aquisitivos",
            width: 400,
            height: 180,
            border: false,
            items: [
                {
                    xtype: "form",
                    border: false,
                    frame: true,
                    defaults: {
                        width: 260,
                        border: false,
                    },
                    items: [
                        {
                            xtype: "button",
                            text: "Visualizar Anexo",
                            fieldLabel: "Anexo",
                            anchor: "50%",
                            scope: this,
                            handler: function () {
                                form = _windowHomologateAP.getComponent(0).getForm();
                                attachment_value = form.findField("attachment").getValue();

                                if (attachment_value === undefined || attachment_value === "") {
                                    action = "create";
                                    oId_value = null;
                                } else {
                                    action = "update";
                                    oId_value = attachment_value;
                                }
                                Ext._create("rh.dayoff.attachment.Window", {
                                    title: "Anexo",
                                    oId: oId_value,
                                    action: action,
                                    values: "remote",
                                    callback: {
                                        success: {
                                            scope: this,
                                            fn: function (instance) {
                                                form.findField("attachment").setValue(instance.pk);
                                            },
                                        },
                                    },
                                }).show();
                            },
                        },
                        {
                            name: "attachment",
                            fieldLabel: "Anexo",
                            xtype: "textfield",
                            allowBlank: true,
                            hidden: true,
                        },
                        {
                            xtype: "datefield",
                            fieldLabel: "Data de Publicação",
                            name: "publication_date",
                            allowBlank: true,
                        },
                        {
                            xtype: "datefield",
                            fieldLabel: "Data de Homologação",
                            name: "homologation_date",
                            allowBlank: true,
                        },
                    ],
                    buttons: [
                        {
                            text: "Homologar",
                            scope: this,
                            handler: function () {
                                var selections = this.getSelectionModel().getSelections();
                                if (selections.length <= 0) {
                                    Ext.Msg.show({
                                        title: "Homologar",
                                        msg: "Selecione um periodo aquisitivo",
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK,
                                    });
                                    return;
                                }
                                var items = [];
                                Ext.each(selections, function (item) {
                                    items.push(item.get("pk"));
                                });

                                form = _windowHomologateAP.getComponent(0).getForm();
                                homologation_date = Ext.util.Format.date(
                                    form.findField("homologation_date").getValue(),
                                    "d/m/Y"
                                );
                                publication_date = Ext.util.Format.date(
                                    form.findField("publication_date").getValue(),
                                    "d/m/Y"
                                );
                                attachment = form.findField("attachment").getValue();
                                if (!homologation_date || !attachment || !publication_date) {
                                    Ext.Msg.show({
                                        title: "Homologar",
                                        msg: "Publicação e Data de Publicação/Homologação obrigatório(s)",
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK,
                                    });
                                    return;
                                }
                                var params = {
                                    actionCustom: "homologate_batch",
                                    acquisition_period: items,
                                    homologation_date: homologation_date,
                                    publication_date: publication_date,
                                    attachment: attachment,
                                };

                                this._process(params, _windowHomologateAP);
                            },
                        },
                        {
                            text: "Fechar",
                            scope: this,
                            handler: function () {
                                _windowHomologateAP.destroy();
                            },
                        },
                    ],
                },
            ],
        }).show();
    },

    getHomologateAction: function (cfg) {
        if (!this._homologate) {
            this._homologate = Ext._create("Ext.Button", {
                text: "Homologar",
                icon: "/" + global.Context + "/static/rh/images/pasu_homologado.png",
                scope: this,
                handler: function () {
                    if (this.getSelectionModel().getSelected()) {
                        this.getHomologateWindow();
                    } else {
                        Ext.Msg.show({
                            title: "Homologar",
                            msg: "Selecione um grupo",
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                        });
                    }
                },
            });
        }
        return this._homologate;
    },

    getReleaseAction: function (cfg) {
        if (!this._setMainAction) {
            this._setMainAction = Ext._create("Ext.Button", {
                text: "Liberar",
                iconCls: "icon-core icon-core-success",
                scope: this,
                handler: function () {
                    if (this.getSelectionModel().getSelected()) {
                        var params = {
                            actionCustom: "release",
                            acquisition_period: this.getSelectionModel().getSelected().id,
                        };

                        this._process(params);
                    } else {
                        Ext.Msg.show({
                            title: "Liberar Periodo Aquisitivo",
                            msg: "Selecione um período",
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                        });
                    }
                },
            });
        }
        return this._setMainAction;
    },

    getUpdateAPAction: function (cfg) {
        if (!this._updateAPAction) {
            var _owner = this;
            this._updateAPAction = Ext._create("Ext.Button", {
                text: "Atualizar",
                iconCls: "icon-core icon-core-refresh",
                scope: this,
                handler: function () {
                    var selection = _owner.getSelectionModel().getSelections();

                    if (selection.length) {
                        var params = {
                            actionCustom: "run_upgrade_aquisition_period",
                            acquisition_period: selection.map(function (item) {
                                return item.get("pk");
                            }),
                        };

                        this._process(params);
                    } else {
                        Ext.Msg.show({
                            title: "Atualizar Período Aquisitivo",
                            msg: "Selecione um período",
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                        });
                    }
                },
            });
        }
        return this._updateAPAction;
    },

    getSellAction: function (cfg) {
        if (!this.sellAction)
            this.sellAction = Ext._create("Ext.Button", {
                text: "Vender",
                iconCls: "icon-fopag icon-cash",
                scope: this,
                handler: function () {
                    var selected = this.getSelectionModel().getSelected();
                    if (!selected) {
                        Ext.Msg.show({
                            title: "Venda de Período Aquisitivo",
                            width: 250,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: "Selecione um item",
                        });
                    } else {
                        this.getSellWindow(selected);
                    }
                },
            });

        return this.sellAction;
    },

    getSellWindow: function (selected) {
        var form = Ext._create("Ext.form.FormPanel", {
            frame: true,
            items: [
                {
                    fieldLabel: "Informe a quantidade de dias para vender:",
                    name: "days",
                    hiddenName: "days",
                    xtype: "numberfield",
                    width: 220,
                },
            ],
        });

        wnd = Ext._create("Ext.Window", {
            title: "Venda de Período Aquisitivo",
            width: 400,
            height: 150,
            border: false,
            params: {
                actionCustom: "sell",
                acquisition_period: selected.get("pk"),
            },
            items: [form],
            buttons: [
                {
                    text: "Enviar",
                    scope: this,
                    handler: function () {
                        var params = wnd.params;
                        params.days = form.getForm().getValues().days;
                        this._process(params);
                        wnd.close();
                    },
                },
                {
                    text: "Cancelar",
                    scope: this,
                    handler: function () {
                        wnd.destroy();
                    },
                },
            ],
        });

        wnd.show();
    },

    _process: function (params, window_) {
        var rest = Ext._create("rh.dayoff.acquisitionperiod.Restful", { resource: this.resource });
        var mask = Ext._create("Ext.LoadMask", this.getEl(), { msg: "Processando informações." });
        var _grid = this;
        var wnd = window_ == null ? this : window_;

        console.info(wnd.externalCallback);

        if (wnd.externalCallback == undefined)
            wnd.externalCallback = {
                fn: function (message) {
                    console.info(message);
                    _grid.getStore().load();
                },
            };
        mask.show();
        rest._process(
            params,
            {
                scope: this,
                fn: function (rst) {
                    console.info(rst);
                    core.invokeCallback(wnd.externalCallback || { fn: Ext.emptyFn }, rst);
                },
            },
            {
                fn: function (message) {
                    Ext.Msg.show({
                        title: "Informando",
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: message,
                    });
                },
            },
            {
                fn: function () {
                    mask.hide();
                },
            }
        );
    },

    getFilterMenu: function () {
        return this.getFilterMenuItems();
    },

    getFilterMenuItems: function () {
        return [
            {
                text: "Por Situação",
                menu: this.getStatusMenuItems(),
            },
            {
                text: "Por Bloqueio",
                menu: this.getBlockedMenuItems(),
            },
            {
                text: "Por Pendência",
                menu: this.getPendencyMenuItems(),
            },
            {
                text: "Por Tipo de Usufruto",
                menu: this.getUsufurctMenuItems(),
            },
        ];
    },

    getUsufurctMenuItems: function () {
        if (!this._filterUsufruct)
            this._filterUsufruct = [
                {
                    text: "Selecionar",
                    scope: this,
                    handler: this.filterTypeOfUsufruct,
                },
                {
                    text: "Limpar filtro",
                    scope: this,
                    handler: this.clearFilter,
                },
            ];
        return this._filterUsufruct;
    },

    clearFilter: function () {
        this.removeFilterProperty("group_period__configuration__type_of_usufruct__in", 1003);
    },

    filterTypeOfUsufruct: function () {
        var select = Ext._create("core.GridSelectWindow", {
            rest: "standard.ChoiceRestful",
            title: "Selecione um tipo de usufruto para filtrar",
            width: Ext.getBody().getBox().width * 0.9,
            height: Ext.getBody().getBox().height * 0.9,
            params: [
                { property: "app_label", value: "dayoff", stage: 1001 },
                { property: "name", value: "CONFIGURATION_CHOICE", stage: 1002 },
            ],
            multi: true,
            callback: {
                scope: this,
                fn: function (instance) {
                    var pks = [];
                    instance.forEach(function (selection) {
                        pks.push(selection.get("value"));
                    });
                    if (instance.length > 0)
                        this.setFilterProperty("group_period__configuration__type_of_usufruct__in", pks, 1003);
                    else this.removeFilterProperty("group_period__configuration__type_of_usufruct__in", 1003);
                },
            },
        });
        select._gridPanel.getToolbar().hide();
        select._gridPanel.getActionColumn().destroy();
        select._gridPanel.setFilterProperty("app_label", "dayoff", 1001);
        select._gridPanel.setFilterProperty("name", "CONFIGURATION_CHOICE", 1002);
        select._gridPanel.getColumnModel().setColumnHeader(5, "Tipo");
        collums = [1, 2, 3, 4, 6, 7, 8];
        collums.forEach(function (c) {
            select._gridPanel.getColumnModel().setHidden(c, true);
        });
        select.show();
    },

    getStatusMenuItems: function () {
        if (!this._statusMenuItems) {
            this._statusMenuItems = [];
            for (var i = 0; i < this.statusItemsMenuConf.length; i++) {
                var item = this.statusItemsMenuConf[i];
                this._statusMenuItems.push(
                    new Ext.menu.CheckItem({
                        text: item.text,
                        scope: this,
                        hideOnClick: false,
                        checked: item.checked,
                        value: item.value,
                        checkHandler: function (item, checked) {
                            this.toggleStatusFilter();
                        },
                    })
                );
            }
        }
        return this._statusMenuItems;
    },

    toggleStatusFilter: function () {
        var values = [];
        this.getStatusMenuItems().forEach(function (item) {
            if (item.checked) values.push(item.value);
        });
        this.setFilterProperty("status__in", values, 200);
    },

    getBlockedMenuItems: function () {
        if (!this._blockedMenuItems) {
            this._blockedMenuItems = [];
            for (var i = 0; i < this.blockedItemsMenuConf.length; i++) {
                var item = this.blockedItemsMenuConf[i];
                this._blockedMenuItems.push(
                    new Ext.menu.CheckItem({
                        text: item.text,
                        scope: this,
                        hideOnClick: false,
                        checked: item.checked,
                        value: item.value,
                        checkHandler: function (item, checked) {
                            this.toggleBlockedFilter();
                        },
                    })
                );
            }
        }
        return this._blockedMenuItems;
    },

    toggleBlockedFilter: function () {
        var values = [];
        this.getBlockedMenuItems().forEach(function (item) {
            if (item.checked) values.push(item.value);
        });
        this.setFilterProperty("blocked__in", values, 300);
    },

    getPendencyMenuItems: function () {
        if (!this._pendencyMenuItems) {
            this._pendencyMenuItems = [];
            for (var i = 0; i < this.pendencyItemsMenuConf.length; i++) {
                var item = this.pendencyItemsMenuConf[i];
                this._pendencyMenuItems.push(
                    new Ext.menu.CheckItem({
                        text: item.text,
                        scope: this,
                        hideOnClick: false,
                        checked: item.checked,
                        value: item.value,
                        checkHandler: function (item, checked) {
                            this.togglePendencyFilter();
                        },
                    })
                );
            }
        }
        return this._pendencyMenuItems;
    },

    togglePendencyFilter: function () {
        var values = [];
        this.getPendencyMenuItems().forEach(function (item) {
            if (item.checked) values.push(item.value);
        });
        this.setFilterProperty("pendency__in", values, 400);
    },

    getColumnModel: function () {
        if (!this._columnModel)
            this._columnModel = Ext._create("Ext.grid.ColumnModel", [
                Ext._create("Ext.grid.RowNumberer"),
                { header: "Cod", dataIndex: "pk", width: 50, hidden: true },
                {
                    id: "icons",
                    dataIndex: "icons",
                    header: "",
                    width: 100,
                    sortable: false,
                    renderer: toolkit.util.formatStatus,
                    menuDisabled: true,
                },
                { header: "Grupo", dataIndex: "group_period_unicode", width: 200 },
                { header: "Grupo", dataIndex: "unicode_full_group_period", width: 220, hidden: true },
                { header: "Servidor", dataIndex: "employee_unicode", width: 200 },
                { header: "Situação", dataIndex: "status_display", id: "autoExpandColumn" },
                { header: "Total Periodo Aquisitivo", dataIndex: "days", width: 120 },
                { header: "Dias agendados", dataIndex: "booked_days_cache", width: 80 },
                { header: "Dias a usufruir", dataIndex: "days_to_enjoy_cache", width: 80 },
                { header: "Saldo disponível", dataIndex: "days_not_booked_cache", width: 100 },
                { header: "Informação", dataIndex: "information", width: 90, hidden: true },
                {
                    header: "Início aquisição",
                    dataIndex: "start_date_acquisition",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {
                    header: "Fim aquisição",
                    dataIndex: "end_date_acquisition",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {
                    header: "Início fruição",
                    dataIndex: "start_date_fruition",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {
                    header: "Fim fruição",
                    dataIndex: "end_date_fruition",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y"),
                },
                {
                    header: "Período aquisitivo anterior",
                    dataIndex: "previous_period_unicode",
                    width: 120,
                    hidden: true,
                },
                {
                    header: "Período contínuo",
                    dataIndex: "continuous_period",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                {
                    header: "Bloqueado",
                    dataIndex: "blocked",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                {
                    header: "Criado automaticamente",
                    dataIndex: "automatic_created",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                { header: "Dias vendidos", dataIndex: "paid_days_cache", width: 90, hidden: true },
                {
                    header: "Pago sem folha",
                    dataIndex: "paid_without_payroll",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                {
                    header: "Indenizado",
                    dataIndex: "indemnified",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                { header: "Dias Suspensos", dataIndex: "suspended_days", width: 90, hidden: true },
                { header: "Folha Evento", dataIndex: "paycheck_event_unicode", width: 120, hidden: true },
                { header: "Anexo", dataIndex: "attachment_unicode", width: 120, hidden: true },
                { header: "Criado por", dataIndex: "created_by_unicode", width: 120, hidden: true },
                {
                    header: "Criado em",
                    dataIndex: "created_at",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    hidden: true,
                },
                { header: "Modificado por", dataIndex: "modified_by_unicode", width: 120, hidden: true },
                {
                    header: "Modificado em",
                    dataIndex: "modified_at",
                    width: 90,
                    renderer: Ext.util.Format.dateRenderer("d/m/Y H:i"),
                    hidden: true,
                },
                {
                    header: "Gerar anotação",
                    dataIndex: "note",
                    width: 90,
                    renderer: function (value) {
                        return value ? "SIM" : "NÃO";
                    },
                    hidden: true,
                },
                { header: "Anotação", dataIndex: "annotation_unicode", width: 120, hidden: true },
            ]);

        return this._columnModel;
    },

    getPaymentGrid: function(record) {
        this._gridPayments = new rh.dayoff.payment.Grid({
            // title: 'Anexos da Justificativa',
            layout: 'fit',
            region: 'center',
            hideColumns: ['unicode', 'acquisition_period_unicode', 'description', 'payment_oid'],
            // hideItemsToolbar: ['add', 'edit', 'remove'],
            hideActions: ['edit', 'remove', 'copy', ]
            // solicitacao: this.params.solicitacao,
        });
        this._gridPayments.setParam('acquisition_period', record.data.pk);
        this._gridPayments.setParam('employee', record.data.employee);
        this._gridPayments.setFilterProperty('acquisition_period', record.data.pk, 1001);

        return this._gridPayments;
    },

    paymentsWindow: function(index){
        var record = this.getStore().getAt(index);
        console.debug(record);
        new Ext.Window({
            title: 'Pagamentos',
            closable: true,
            modal: true,
            layout: 'border',
            width: 900,
            height: 450,
            border: false,
            items:[this.getPaymentGrid(record)]
        }).show();
    },

    getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-fopag icon-money-pencil',
                tooltip: 'Pagamentos',
                scope: this,
                handler: function(action, index) {
                	if(!this.getSelectionModel().isSelected(index))
                		this.getSelectionModel().selectRow(index);
                	this.paymentsWindow(index);
                }
            },
        ];
    },
});

core.RestfulGrid.register(
    'rh.dayoff.acquisitionperiod.Restful',
    'rh.dayoff.acquisitionperiod.Grid'
);

