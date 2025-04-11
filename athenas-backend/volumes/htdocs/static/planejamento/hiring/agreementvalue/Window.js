Ext._define('planning.hiring.agreementvalue.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.agreementvalue.Restful',

    width: 500,

    TIPO_VALOR_CONTRATO: {
        Principal: 1,
        Prazo: 2,
        Valor: 3,
        Outros: 4,
        Apostilamento: 5
    },

    getButtons: function (cfg) {
        if (!this._buttons) {
            this._buttons = [
                {
                    text: "Salvar",
                    handler: function () {
                        var values = this.getFormPanel().getForm().getValues();

                    if(values.tipo_valor_contrato == this.TIPO_VALOR_CONTRATO.Principal || values.tipo_valor_contrato == this.TIPO_VALOR_CONTRATO.Prazo) {
                        schedule_annotation_field = this.getFormPanel().getForm().findField('schedule_annotation');
                        schedule_annotation_field.setValue("on");
                        this.save();
                    }

                    else
                    {
                        this.save();
                    }},

                    scope: this
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    getValueDocumentGrid: function() {
        if(!this._valueDocumentGrid) {
            this._valueDocumentGrid = Ext._create('planning.hiring.document.ValueDocumentGrid', {
                title: 'Documentos',
                height: 200,
                width: 510,
                region: 'south',
                gridAutoLoad: false
            });
        }

        return this._valueDocumentGrid;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getTipoValorContratoField(),
                    this.getOrdemField(),
                    this.campoObjeto(),
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data da Assinatura",
                        name: "data_assinatura",
                        xtype: "datefield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data Início",
                        name: "data_ref_inicio",
                        xtype: "datefield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data Fim",
                        name: "data_ref_fim",
                        xtype: "datefield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Valor (R$)",
                        name: "valor",
                        xtype: "currencyfield",
                    },
                    {
                        width: 358,
                        allowBlank: false,
                        fieldLabel: "Data Publicação",
                        name: "data_publicacao",
                        xtype: "datefield",
                    },
                    {
                        width: 358,
                        hidden: true,
                        allowBlank: true,
                        fieldLabel: 'Criar Anotação?',
                        name: 'schedule_annotation',
                        xtype: "checkbox"
                    },
                    this.getValueDocumentGrid()
                ]
            });
        }
        return this._formPanel;
    },

    _tipoValorContratoChangeValid: function(combo, newValue, oldValue, valid) {
        var self = this;

        function enableFields() {
            self.campoObjeto().enable();
        }

        function disableFields() {
            self.campoObjeto().disable();
        }

        this.getOrdemField().getStore().setBaseParam('pk', 0);

        switch (newValue) {
            case this.TIPO_VALOR_CONTRATO.Principal:
                disableFields();
                break;
            case this.TIPO_VALOR_CONTRATO.Apostilamento:
                enableFields();
                this.getOrdemField().getStore().setBaseParam('pk', this.values.contrato);
                break;
            default:
                enableFields();
        }

        this.getOrdemField().getStore().load();
    },

    getTipoValorContratoField: function() {
        if (!this._tipoValorContratoField) {
            this._tipoValorContratoField = Ext._create('standard.fields.ChoiceField', {
                name: 'tipo_valor_contrato',
                hiddenName: 'tipo_valor_contrato',
                fieldLabel: 'Tipo de Aditivo',
                choiceId: 'contrato.TIPO_VALOR_CONTRATO',
                width: 358,
                allowBlank: false,
                listeners: {
                    scope: this,
                    changevalid: this._tipoValorContratoChangeValid,
                },
            });
        }
        return this._tipoValorContratoField;
    },

    getOrdemField: function () {
        var me = this;
        if (!this._ordemField) {
            this._ordemField = Ext._create('Ext.form.ComboBox', {
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('PHAAgreement', 'tipo_ordem_contrato'),
                        disableCaching: false,
                        method: 'GET'
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'label', type: 'string'},
                            {name: 'value', type: 'int'}
                        ]
                    }),
                    //baseParams: null,
                    autoLoad: true,

                    // ******* FORÇA A EXIBIÇÃO DO displayField ********
                    // Isso se faz necessário porque ao criar a janela,
                    // o form chama o método setValue bem antes do combo
                    // ter seu store populado, o que faz com que o
                    // displayField não seja exibido.
                    listeners: {
                        scope: this,
                        load: function (store, records, options) {
                            var value = me.getOrdemField().getValue();
                            if (value !== '') {
                                me.getOrdemField().setValue(value);
                            }
                        }
                    }
                }),
                lazyInit: false,
                triggerAction: 'all',
                name: 'ordem',
                hiddenName: 'ordem',
                fieldLabel: "Sequência do Termo Aditivo",
                displayField: 'label',
                valueField: 'value',
                editable: false,
                width: 358,
            });
        }

        return this._ordemField;
    },

    campoObjeto: function () {
        if (!this._campoObjeto) {
            this._campoObjeto = Ext._create('Ext.form.TextArea', {
                name: 'objeto',
                fieldLabel: "Objeto",
                width: 358,
            });
        }
        return this._campoObjeto;
    },

    value: function (value, prevent) {
        prevent = core.nullValue(prevent, false);
        if (value !== undefined) {
            this._value = value;
            !prevent && this.observeValue();
        }
        return this._value;
    },


    observeValue: function () {
        var value = this.value();

        if (value) {

            this.getValueDocumentGrid().enable();
            this.getValueDocumentGrid().setParam('value', value);
            this.getValueDocumentGrid().setFilterProperty('value', value, 101);

        } else {

            this.getValueDocumentGrid().disable();
            this.getValueDocumentGrid().setParam('value', 0);
            this.getValueDocumentGrid().setFilterProperty('value', 0, 101);
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        this.campoObjeto().disable();

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.action = 'update';
                    this.value(instance.pk);
                    this.oId = instance.pk;
                }
            }
        });

        planning.hiring.agreementvalue.Window.superclass.constructor.call(this, cfg);
        this.value(cfg.oId === undefined ? null : cfg.oId);
    },
});
