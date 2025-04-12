
Ext._define('planning.hiring.meterage.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.meterage.Restful',

    width: 500,

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        planning.hiring.meterage.Window.superclass.constructor.call(this, cfg);
    },

    campoNE: function(cfg) {
        if (!this._campoNE)
            this._campoNE = Ext._create('core.fields.AutocompleteField', {
                width: 362,
                allowBlank: false,
                fieldLabel: "Nota de Empenho",
                name: "nota_empenho",
                xtype: "rest-autocompletefield",
                rest: "planning.hiring.commitmentnote.Restful",
                preFilter: [
                    {property: 'contrato', value: cfg.params.contrato, stage: 100},
                    {property: 'ne_anterior', value: null, stage: 101}
                ],
                comboListeners: {
                    scope: this,
                    changevalid: function(cmb, nv, ov, valid){
                        if(nv && !this.oId)
                        {
                            valor = cmb.lastSelectionText.split(" - ");
                            valor = Math.round(valor[1] * 100) / 100;
                            this._formPanel.getComponent(2).setValue(valor);
                        }
                    },
                },
            });

        return this._campoNE;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.campoNE(cfg),
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Nota Fiscal",
                        name: "nota_fiscal",
                        xtype: "numberfield",
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Valor",
                        name: "valor",
                        xtype: "currencyfield",
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Data Inicial da Referência",
                        name: "inicio_periodo_referencia",
                        xtype: "datefield",
                        value: new Date(),
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Data Final da Referência",
                        name: "fim_periodo_referencia",
                        xtype: "datefield",
                        value: new Date(),
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Observação",
                        name: "observacao",
                        xtype: "ckeditor",
                    },
                ]
            });
        return this._formPanel;
    },
});

