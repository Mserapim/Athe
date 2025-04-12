Ext._define('planning.hiring.agreement.Window', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.agreement.Restful',

    resizable: false,
    width: 840,
    height: 740,

    getFormPanel: function () {
        if (!this._formPanel) {
            this._formPanel = new Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                layout: 'fit',
                items: [
                    new Ext._create('Ext.TabPanel', {
                        activeTab: 0,
                        width: 480,
                        height: 820,
                        items: [
                            this.getPanelAgreement(),
                            this.getPanelOrder(),
                            this.getPanelValue(),
                            this.getCorporateStructurePanel(),
                            this.getPanelSupervisor(),
                            this.getPanelAnnotation()
                        ]
                    }),
                ]
            });
        }
        return this._formPanel;
    },

    getAgreementDocumentGrid: function() {
        if(!this._agreementDocumentGrid) {
            this._agreementDocumentGrid = Ext._create('planning.hiring.document.AgreementDocumentGrid', {
                anchor: '100%',
                title: 'Documentos',
                height: 320,
                width: 780,
                region: 'south',
                gridAutoLoad: false
            });
        }

        return this._agreementDocumentGrid;
    },

    getPanelHired: function () {
        if (!this._newHired) {
            this._newHired = Ext._create('planning.hiring.hired.Grid', {
                region: 'south',
                title: 'Contratados',
                height: 324,
            });

            this._newHired.getSelectionModel().on({
                scope: this,
                selectionchange: function (selm) {
                    var selection = selm.getSelections();
                    if (selection.length > 0) {
                        this.hired(selection[0].id);
                    } else {
                        this.hired(null);
                    }
                }
            });

            this._newHired.getStore().on({
                scope: this,
                load: function () {
                    this.observeHired();
                }
            });
        }

        return this._newHired;
    },

    getCorporateStructureGrid: function () {
        if (!this._corporateStructureGrid) {
            this._corporateStructureGrid = Ext._create('planning.hiring.corporatestructure.Grid', {
                title: 'Estrutura Corporativa',
                region: 'center',
                flex: 1.0,
                minWidth: '50%',
                height: 318,
                frame: true,
                columnAction: false,
            });
        }        
    
        return this._corporateStructureGrid;
    },
    
    getCorporateStructurePanel: function () {
        if (!this._corporateStructurePanel)
            this._corporateStructurePanel = Ext._create('Ext.Panel', {
                title: 'Contratados e Estrutura Corporativa',
                items: [
                    this.getPanelHired(),
                    this.getCorporateStructureGrid(),
                ]
            });
        return this._corporateStructurePanel;
    },

    getPanelSupervisor: function () {
        if (!this._newSupervisor) {
            this._newSupervisor = Ext._create('planning.hiring.supervisor.AgreementSupervisorGrid', {
                title: 'Fiscais',
                hideItemsToolbar: ['remove', 'download'],
                hideActions: ['copy', 'edit', 'remove'],
                allowRemove: false,
                keywordFieldWidth: 265,
            });
        }

        return this._newSupervisor;
    },

    orderField: function (cfg) {
        if (!this._orderField)
            this._orderField = Ext._create('core.fields.RelatedRestfulField', {
                xtype: 'rest-relatedfield',
                fieldLabel: 'Pedidos',
                name: 'order',
                relatedname: 'pedidos',
                displayField: 'minute_unicode',
                allowBlank: false,
                rest: this.rest,
                sourceRest: 'planning.hiring.minutesolicitation.MinuteSolicitationRestful',
                width: 800,
                height: 648,
                border: false
            });

        return this._orderField;
    },

    getPanelOrder: function (cfg) {
        if (!this._orderPanel)
            this._orderPanel = Ext._create('Ext.Panel', {
                title: 'Pedidos',
                frame: true,
                items: this.orderField(),
                height: 650
            });

        return this._orderPanel;
    },

    getPanelValue: function (cfg) {
        if (!this._valuePanel)
            this._valuePanel = Ext._create('planning.hiring.agreementvalue.Grid', {
                title: 'Valor do Contrato',
                region: 'center',
                height: 650
            });

        return this._valuePanel;
    },

    getPanelAnnotation: function (cfg) {
            if (!this._annotationPanel)
            this._annotationPanel = Ext._create('planning.hiring.agreementannotation.Grid', {
                title: 'Anotações',
                region: 'center',
                height: 650
            });

        return this._annotationPanel;
    },

    getMeetDateField: function () {
        if (!this._date)
            this._date = Ext._create('Ext.form.DateField', {
                name: 'annotatition_meetdate',
                fieldLabel: "Data",
                hidden: false,
                width: 370,
            });
        return this._date;
    },

    getPanelAgreement: function (cfg) {
        if (!this._agreementPanel)
            this._agreementPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                border: false,
                frame: true,
                title: 'Contrato',
                labelAlign: 'left',
                labelWidth: 130,
                height: 650,
                items: [
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: false,
                                        fieldLabel: "Número",
                                        name: "numero",
                                        xtype: "textfield",
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: false,
                                        fieldLabel: "Tipo de Contrato",
                                        name: "TIPO_CONTRATO",
                                        choiceId: "contrato.TIPO_CONTRATO",
                                        xtype: "choicefield",
                                        hiddenName: "tipo_contrato",
                                        listeners: {
                                            scope: this,
                                            select: this._orderSelect,
                                        }
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: false,
                                        fieldLabel: "Número do Processo",
                                        name: "numero_processo",
                                        xtype: "textfield"
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: true,
                                        fieldLabel: "Processo Mãe",
                                        name: "numero_processo_mae",
                                        xtype: "textfield"
                                    },
                                ]
                            },
                        ]
                    }, 
                    {
                        anchor: '99%',
                        allowBlank: false,
                        fieldLabel: "Objeto do Contrato",
                        name: "objeto_contrato",
                        xtype: "textarea"
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: false,
                                        fieldLabel: "Inicio Vigência",
                                        name: "data_inicio",
                                        xtype: "datefield"
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    this.campoDataVencimento(),
                                ]
                            },
                        ]
                    }, 
                    this.campoDataVencimentoFlag(),
                    {
                        anchor: '99%',
                        allowBlank: true,
                        fieldLabel: "Aviso de Vencimento",
                        name: "DIAS_AVISO",
                        choiceId: "contrato.DIAS_AVISO",
                        xtype: "choicefield",
                        hiddenName: "dias_para_aviso",
                        remoteGroup: true,
                        remoteSort: true,
                        sortInfo: { field: 'label', direction: 'DESC' },
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: true,
                                        fieldLabel: "Tipo de Licitação",
                                        name: "TIPO_LICITACAO",
                                        choiceId: "contrato.TIPO_LICITACAO",
                                        xtype: "choicefield",
                                        hiddenName: "tipo_licitacao",
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        anchor: '97%',
                                        allowBlank: true,
                                        fieldLabel: "Número da Licitação",
                                        name: "numero_licitacao",
                                        xtype: "textfield"
                                    }
                                ]
                            },
                        ]
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    this.campoTipoMedicao(),
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    this.campoDiaPagamento(),
                                ]
                            },
                        ]
                    },  
                    {
                        anchor: '99%',
                        allowBlank: true,
                        fieldLabel: "Número da Pasta/Arquivo",
                        name: "numero_pasta",
                        xtype: "textfield"
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '0.4',
                                layout: 'form',
                                items: [
                                    this.indexField()
                                ]
                            },
                            {
                                columnWidth: '0.3',
                                layout: 'form',
                                items: [
                                    this.referenceField() 
                                ]
                            },
                            {
                                columnWidth: '0.3',
                                layout: 'form',
                                items: [
                                    this.anniversaryField() 
                                ]
                            },
                        ]
                    },
                    this.getAgreementDocumentGrid(),
                ]
            });

        this.campoDataVencimentoFlag().value = this.campoDataVencimento().value;

        return this._agreementPanel;
    },

    anniversaryField: function () {
        if (!this._annniversaryField)
            this._annniversaryField = Ext._create('Ext.form.TextField', {
                anchor: '95%',
                allowBlank: true,
                fieldLabel: "Aniversário Reajuste",
                name: "readjustment_anniversary",
            });

        return this._annniversaryField;
    },

    referenceField: function () {
        if (!this._referenceField)
            this._referenceField = Ext._create('standard.fields.ChoiceField', {
                anchor: '95%',
                allowBlank: true,
                fieldLabel: "Mês de Referência",
                name: "MES_REAJUSTE",
                choiceId: "contrato.MES_REAJUSTE",
                hiddenName: "reference_month",
            });

        return this._referenceField;
    },

    _onOffIndexFields: function (combo, record, index) {
        var valor = combo.getValue();

        if (valor != 1) {
            this.referenceField().enable();
            this.referenceField().show();
            this.anniversaryField().enable();
            this.anniversaryField().show();
        } else {
            this.referenceField().disable();
            this.referenceField().setValue("");
            this.anniversaryField().disable();
            this.anniversaryField().setValue("");
        }
    },

    indexField: function () {
        if (!this._campoIndex)
            this._campoIndex = Ext._create('standard.fields.ChoiceField', {
                anchor: '95%',
                allowBlank: false,
                fieldLabel: "Índice de Reajuste",
                name: "INDICE_REAJUSTE",
                choiceId: "contrato.INDICE_REAJUSTE",
                hiddenName: "index",
                listeners: {
                    scope: this,
                    select: this._onOffIndexFields
                },
            });
        return this._campoIndex;
    },


    _manipular: function (combo, record, index) {
        var valor = combo.getValue();

        if (valor == 2) {
            this.campoDiaPagamento().enable();
            this.campoDiaPagamento().show();
        } else {
            this.campoDiaPagamento().disable();
        }
    },

    _orderSelect: function (combo, record, index) {
        var valor = combo.getValue();

        if (valor == 6 || valor == 9) {
            if (valor == 6)
                this.tipo_contrato = 6;
            if (valor == 9)
                this.tipo_contrato = 9;
            this.orderField().enable();
        } else {
            this.tipo_contrato = 0;
            this.orderField().disable();
        }
    },

    campoDiaPagamento: function () {
        if (!this._campoDiaPagamento)
            this._campoDiaPagamento = Ext._create('Ext.form.TextField', {
                name: 'dia_pagamento',
                fieldLabel: "Dia do Pagamento",
                anchor: '97%'
            });

        return this._campoDiaPagamento;
    },

    campoTipoMedicao: function () {
        if (!this._campoTipoMedicao)
            this._campoTipoMedicao = Ext._create('standard.fields.ChoiceField', {
                anchor: '97%',
                allowBlank: false,
                fieldLabel: "Tipo da Medição",
                name: "TIPO_MEDICAO",
                choiceId: "contrato.TIPO_MEDICAO",
                hiddenName: "tipo_medicao",
                listeners: {
                    scope: this,
                    select: this._manipular
                },
            });
        return this._campoTipoMedicao;
    },

    campoDataVencimento: function () {
        if (!this._campoDataVencimento)
            this._campoDataVencimento = Ext._create('Ext.form.DateField', {
                name: 'data_vencimento',
                fieldLabel: "Fim da Vigência",
                hidden: false,
                anchor: '97%'
            });
        return this._campoDataVencimento;
    },

    campoDataVencimentoFlag: function () {
        if (!this._campoDataVencimentoFlag)
            this._campoDataVencimentoFlag = Ext._create('Ext.form.DateField', {
                name: 'data_vencimento_flag',
                hidden: true,
                fieldLabel: "Data de Vencimento",
            });

        return this._campoDataVencimentoFlag;
    },

    contrato: function (value, prevent) {
        prevent = core.nullValue(prevent, false);
        if (value !== undefined) {
            this._contrato = value;
            !prevent && this.observeContrato();
        }
        return this._contrato;
    },

    hired: function (value, observe) {
        observe = (observe === undefined ? true : observe);
        
        if (value !== undefined) {
            this._hired = value;

            if (observe)
                this.observeHired();
        }
        return this._hired;
    },

    observeHired: function(){
        var selected = this.getPanelHired().getSelectionModel().getSelected();
        if (selected) {
            this.getCorporateStructureGrid().enable();
            this.getCorporateStructureGrid().setParam('enterprise', selected['id']);
            this.getCorporateStructureGrid().setFilterProperty('enterprise', selected['id'], 100);
        } else {
            this.getCorporateStructureGrid().disable();
            this.getCorporateStructureGrid().setParam('enterprise', 0);
            this.getCorporateStructureGrid().setFilterProperty('enterprise', 0, 100);
        }
    },

    observeContrato: function () {
        var value = this.contrato();
        this.getPanelValue().disable();

        if(this.tipo_contrato == 6 || this.values.tipo_contrato == 6)
            this.orderField().objectId(value);

        if(this.tipo_contrato == 9 || this.values.tipo_contrato == 9)
            this.orderField().objectId(value);

        if (value) {
            this.getPanelValue().enable();
            this.getPanelValue().setParam('contrato', value);
            this.getPanelValue().setFilterProperty('contrato', value, 6);

            this.getPanelSupervisor().enable();
            this.getPanelSupervisor().setParam('agreement', value);
            this.getPanelSupervisor().setFilterProperty('agreement', value, 100);

            this.getPanelHired().enable();
            this.getPanelHired().setParam('agreement', value);
            this.getPanelHired().setFilterProperty('agreement', value, 100);

            this.getPanelAnnotation().enable();
            this.getPanelAnnotation().setParam('agreement', value);
            this.getPanelAnnotation().setFilterProperty('agreement', value, 101);

            this.getAgreementDocumentGrid().enable();
            this.getAgreementDocumentGrid().setParam('agreement', value);
            this.getAgreementDocumentGrid().setFilterProperty('agreement', value, 101);

            if(this.values.tipo_contrato == 6 || this.values.tipo_contrato == 9)
                this.orderField().objectId(value);
        } else {
            this.getPanelValue().disable();
            this.getPanelValue().setParam('contrato', 0);
            this.getPanelValue().setFilterProperty('contrato', 0, 6);

            this.getPanelSupervisor().disable();
            this.getPanelSupervisor().setParam('agreement', 0);
            this.getPanelSupervisor().setFilterProperty('agreement', 0, 100);

            this.getPanelHired().disable();
            this.getPanelHired().setParam('agreement', 0);
            this.getPanelHired().setFilterProperty('agreement', 0, 100);

            this.getCorporateStructurePanel().disable();

            this.getPanelAnnotation().disable();
            this.getPanelAnnotation().setParam('agreement', 0);
            this.getPanelAnnotation().setFilterProperty('agreement', 0, 101);

            this.getAgreementDocumentGrid().disable();
            this.getAgreementDocumentGrid().setParam('agreement', 0);
            this.getAgreementDocumentGrid().setFilterProperty('agreement', 0, 101);
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.contrato(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        planning.hiring.agreement.Window.superclass.constructor.call(this, cfg);
        this.getPanelAgreement().getComponent(0).focus(true, 1000);
        this.contrato(cfg.oId === undefined ? null : cfg.oId);
    },
});
