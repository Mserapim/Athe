Ext._define("esocial.manager.MenuSelecionarCategoriaWindow", {
    extend: "Ext.Window",

    width: 570,

    getGenerateCategoryField: function (config) {
        if (this._generateActionField) {
            return this._generateActionField;
        }

        this._generateCategoryField = Ext._create("Ext.form.ComboBox", {
            emptyText: "Selecione a categoria",
            hiddenName: "generate_category",
            fieldLabel: "",
            store: [
                ["EFE", "Efetivos"],
                ["CMS", "Comissionados"],
                ["MBR", "Membros"],
                ["BFP", "Beneficiários/Aposentados"],
                ["REQ", "Externos/Requisitados"],
                ["EST", "Estagiários/Residentes"],
            ],
            value: "EFE",
            allowBlank: false,
            triggerAction: "all",
            width: 375,
        });

        return this._generateCategoryField;
    },

    getItemsForm: function (cfg) {
        var _items = []
        _items.push(this.getGenerateCategoryField(cfg));

        return [
            {
                title: "Selecione a Categoria",
                xtype: "fieldset",
                items: _items,
            },
        ];
    },

    getFormPanel: function (cfg) {
        if (!this.formPanel)
            this.formPanel = new Ext.form.FormPanel({
                border: false,
                labelWidth: 150,
                items: this.getItemsForm(cfg),
            });

        return this.formPanel;
    },

    executeAction: function (action, params, msg) {
        var rest = Ext._create("esocial.manager.EventRestful", {});
        var mask = new Ext.LoadMask(this.getEl(), { msg: msg ? msg : "Aguarde..." });
        var wnd = this;

        mask.show();
        rest.executeAction(
            action,
            params,
            {
                scope: this,
                fn: function (rst) {
                    core.invokeCallback(wnd.externalCallback || { fn: Ext.emptyFn }, rst, mask);
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

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: "Gerar Eventos de Cadastro",
        });

        Ext.apply(cfg, {
            border: false,
            items: [this.getFormPanel(cfg)],
            buttons: [
                {
                    text: "Gerar",
                    scope: this,
                    handler: function () {
                        var values = this.getFormPanel().getForm().getValues();
                        this.executeAction("generate_events_registration", values, "Gerando eventos...");
                    },
                },
                {
                    text: "Cancelar",
                    scope: this,
                    handler: function () {
                        this.close();
                    },
                },
            ],
        });

        esocial.manager.MenuSelecionarCategoriaWindow.superclass.constructor.call(this, cfg);
    },
});
