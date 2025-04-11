
Ext._define('planning.hiring.commitmentnote.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.commitmentnote.Restful',

    width: 500,

    campoContratado: function(cfg) {
        if (!this._campoContratado)
            this._campoContratado = Ext._create('core.fields.AutocompleteField', {
                width: 362,
                allowBlank: false,
                fieldLabel: "Contratado(s)",
                name: "fornecedor",
                xtype: "rest-autocompletefield",
                rest: "rh.pessoa.Restful",
                preFilter: [
                    {property: 'contratos', value: cfg.params.contrato, stage: 100}
                ]
            });

        return this._campoContratado;
    },

    campoOrdem: function(cfg) {
        if (!this._campoOrdem)
            this._campoOrdem = Ext._create('core.fields.AutocompleteField', {
                width: 362,
                allowBlank: false,
                fieldLabel: "Referência",
                name: "ref_valor_contrato",
                xtype: "rest-autocompletefield",
                rest: "planning.hiring.agreementvalue.Restful",
                preFilter: [
                    {property: 'contrato', value: cfg.params.contrato, stage: 100}
                ]
            });

        return this._campoOrdem;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Número NE",
                        name: "numero_ne",
                        xtype: "textfield",
                    },
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Valor (R$)",
                        name: "valor",
                        xtype: "currencyfield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Tipo de NE",
                        name: "TIPO_NE",
                        choiceId: "contrato.TIPO_NE",
                        xtype: "choicefield",
                        hiddenName: "tipo"
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Classificação da NE",
                        name: "CLASSIFICACAO_NE",
                        choiceId: "contrato.CLASSIFICACAO_NE",
                        xtype: "choicefield",
                        hiddenName: "classificacao"
                    },
                    this.campoContratado(cfg),
                    this.campoOrdem(cfg),
                ]
            });

        return this._formPanel;
    },
});
