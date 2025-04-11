/**
 *
 **/
Ext._define("rh.movimentacao.possession.request.Window", {
    extend: "rh.movimentacao.possession.Window",
    rest: "rh.movimentacao.possession.request.Restful",

    width: 650,
    height: 750,

    tabPanelHeight: 750,
    border: false,

    constructor: function (cfg) {
        rh.movimentacao.possession.request.Window.superclass.constructor.call(this, cfg);
    },

    _observe: function () {
        var grid;

        if (this.oId) {
            grid = this.getTabEncargoFinanceiro();
            grid.enable();
            grid.setParam("request_move", this.oId);
            grid.setFilterProperty("request_move__id", this.oId);

            gridPeriodo = this.getTabPeriodo();
            gridPeriodo.enable();
            gridPeriodo.setParam("request_move", this.oId);
            gridPeriodo.setFilterProperty("request_move__id", this.oId);
        } else {
            this.getTabEncargoFinanceiro().disable();
            this.getTabPeriodo().disable();
        }

        if (this.getParams().servidor) {
            this.getPossessionOrigin().setPreFilter([
                {
                    property: "servidor__id",
                    value: this.getParams().servidor,
                    stage: 0,
                },
            ]);
        }
    },

    getTabPanelItems: function (cfg_window) {
        return [
            this.getPanelInformation(cfg_window, {}),
            this.getTabEncargoFinanceiro(cfg_window, {}),
            this.getTabPeriodo(cfg_window, {}),
            this.getPanelText(cfg_window, {}),
        ];
    },

    getTabEncargoFinanceiro: function (cfg_window, cfg) {
        if (!this._tabEncargoFinanceiro)
            this._tabEncargoFinanceiro = Ext._create("rh.movimentacao.possession.request.EncargoFinanceiroGrid", {
                title: "Encargo Financeiro",
                gridAutoLoad: false,
                layout: 'fit',
            });
        return this._tabEncargoFinanceiro;
    },

    getTabPeriodo: function (cfg_window, cfg) {
        if (!this._tabPeriodo)
            this._tabPeriodo = Ext._create("rh.movimentacao.possession.request.PeriodoRequisicaoGrid", {
                title: "Períodos",
                gridAutoLoad: false,
                layout: 'fit'
            });
        return this._tabPeriodo;
    },

    getPossessionOrigin: function () {
        if (!this._possessionOrigin) {
            this._possessionOrigin = Ext._create("core.fields.AutocompleteField", {
                fieldLabel: "Posse Origem",
                name: "possession_origin",
                rest: "rh.movimentacao.possession.AllPossessionsRestful",
                width: 360,
            });
        }
        return this._possessionOrigin;
    },

    getOrganOrigin: function () {
        if (!this._organOrigin) {
            this._organOrigin = Ext._create("core.fields.AutocompleteField", {
                fieldLabel: "Órgão Origem",
                name: "organ_origin",
                rest: "rh.administrativeunit.Restful",
                width: 360,
            });
        }
        return this._organOrigin;
    },

    getPublicationField: function (cfg_window, cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            fieldLabel: "Publicação",
        });
        return rh.movimentacao.possession.Window.superclass.getPublicationField.call(this, cfg_window, cfg);
    },

    getPanelInformationItems: function (cfg_window) {
        var items = rh.movimentacao.possession.request.Window.superclass.getPanelInformationItems.call(
            this,
            cfg_window
        );
        // rh.util.itemRemove(items, "quadro");
        rh.util.itemRemove(items, "data_posse");
        rh.util.itemRemove(items, "servidor");
        rh.util.itemRemove(items, "public_concurrence");
        rh.util.itemRemove(items, "bond");
        rh.util.itemRemove(items, "publicacao_movimentacao");
        rh.util.itemRemove(items, "publication_possession");
        rh.util.itemRemove(items, "publication_exercise");
        rh.util.itemRemove(items, "number_process");
        rh.util.itemRemove(items, "judicial_deposit");
        rh.util.itemRemove(items, "legal_amnesty_process");
        rh.util.itemRemove(items, "financial_effect_date");
        rh.util.itemRemove(items, "aid_moving_house_paymente_date");
        rh.util.itemRemove(items, "aid_moving_house_gedoc");
        rh.util.itemRemove(items, "data_inicio_instancia");

        items.push(this.getOrganOrigin());
        // items.push(this.getPossessionOrigin());
        items.push(this.getPublicationField());
        items.push(this.getPublicationFieldChange(cfg_window, { fieldLabel: "Publicação Revogação" }));
        // items.push({
        //     fieldLabel: "Cargo na origem",
        //     name: "job_position_origin",
        //     xtype: "textfield",
        //     allowBlank: false,
        // });
        items.push({
            fieldLabel: "Data posse na origem",
            name: "possession_origin_date",
            xtype: "datefield",
            allowBlank: false,
        });
        items.push({
            xtype: "choicefield",
            fieldLabel: "Ônus",
            hiddenName: "onus",
            choiceId: "rh.TIPO_ONUS",
        });
        items.push({
            fieldLabel: "Categoria origem (eSocial)",
            name: "category",
            xtype: "choicefield",
            hiddenName: "category",
            choiceId: "rh.CATEGORY_WORKER",
            width: 360,
        });
        items.push({
            fieldLabel: "Regime do contrato",
            name: "regime_contract",
            xtype: "choicefield",
            hiddenName: "regime_contract",
            choiceId: "rh.REGIME_CONTRACT",
            width: 360,
            allowBlank: false,
        });
        items.push({
            xtype: 'rest-autocompletefield',
            fieldLabel: 'CBO',
            allowBlank: false,
            rest: 'rh.parameters.CboRestful',
            name: 'cbo'
        });

        return items;
    },
});
