Ext._define("esocial.manager.MenuGeneratePayrollWindow", {
    extend: "Ext.Window",

    width: 570,

    getGenerateActionField: function (config) {
        if (this._generateActionField) {
            return this._generateActionField;
        }

        this._generateActionField = Ext._create("Ext.form.ComboBox", {
            emptyText: "Selecione o Tipo de Geração",
            hiddenName: "generate_action",
            fieldLabel: "",
            store: [
                ["payroll_process", "Gerar"],
                ["payroll_process_demonstratives", "Gerar Demonstrativos(s1200, s1202, s1207)"],
                ["payroll_process_payments", "Gerar Pagamentos(s1210)"],
                ["payroll_demonstrative_deletion", "Exclusão - Demonstrativos(s1200, s1202, s1207)"],
                ["payroll_payment_deletion", "Exclusão - Pagamentos(s1210)"],
                ["payroll_closing", "Fechamento"],
                ["payroll_reopening", "Reabertura"],
                ["payroll_closing_analysis", "Análise"],
            ],
            value: "payroll_process",
            allowBlank: false,
            triggerAction: "all",
            width: 375,
        });

        return this._generateActionField;
    },

    getItemsForm: function (cfg) {
        var _items = [
            {
                xtype: "rest-autocompletefield",
                fieldLabel: "Selecione o Período",
                name: "period",
                rest: "rh.gfp.payroll.PeriodRestful",
                allowBlank: false,
            },
        ];
        if (cfg.maintenance == true) {
            _items.push({
                xtype: "rest-autocompletefield",
                fieldLabel: "Selecione o Período Final",
                name: "period_end",
                rest: "rh.gfp.payroll.PeriodRestful",
                allowBlank: true,
            });
        }

        _items.push(this.getGenerateActionField(cfg));

        return [
            {
                title: "Informações da Geração dos Eventos",
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
            title: "Gerar Eventos da Folha",
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
                        this.executeAction("generate_events_payroll", values, "Gerando eventos...");
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

        esocial.manager.MenuGeneratePayrollWindow.superclass.constructor.call(this, cfg);
    },
});
