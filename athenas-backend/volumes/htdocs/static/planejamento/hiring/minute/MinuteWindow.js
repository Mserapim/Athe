Ext._define('planning.hiring.minute.MinuteWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minute.MinuteRestful',
    resizable: false,
    width: 1000,
    autoHeigth: true,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: true,
                frame: true,
                layout: 'form',
                autoHeight: true,
                items: [
                    new Ext._create('Ext.TabPanel', {
                        activeTab: 0,
                        items: [
                            this.getMinutePanel(),
                            this.getMainMinuteItemPanel(cfg),
                            this.getSupervisorPanel(),
                            this.getCorporateStructurePanel(),
                            this.getMinuteDocumentPanel(),
                            this.getMinuteAnnotationPanel()
                        ]
                    })
                ]

            });

        return this._formPanel;
    },

    getManagementOrgan: function () {
        if (!this._managementOrgan) {
            this._managementOrgan = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: "Órgão gerenciador",
                allowBlank: false,
                rest: "rh.generalorgan.Restful",
                name: "management_organ",
                anchor: '99%',
                listeners: {
                    scope: this,
                    render: function () {
                        if (this.values.management_organ === undefined)
                            Ext.Ajax.request({
                                scope: this,
                                url: toolkit.util.Normalize.controller_action(
                                    'PHMMinute',
                                    'get_management_organ'
                                ),
                                success: function (response) {
                                    var rst = Ext.decode(response.responseText);
                                    this.getManagementOrgan().setValue(rst.management_organ_id);
                                },

                            });

                    },
                }
            });
        }

        return this._managementOrgan;
    },
    getMinutePanel: function (cfg) {
        if (!this._minutePanel) {
            this._minutePanel = Ext._create('Ext.Panel', {
                title: 'Ata',
                layout: 'form',
                labelAlign: 'top',
                frame: true,
                autoHeight: true,
                listeners: {
                    scope: this,
                    show: function () {
                        if (this.oId) {
                            Ext.Ajax.request({
                                scope: this,
                                url: toolkit.util.Normalize.controller_action(
                                    'PHMMinute',
                                    'total_amount_display'
                                ),
                                params: {
                                    pk: this.oId
                                },
                                success: function (response) {
                                    var rst = Ext.decode(response.responseText);
                                    if (rst.success)
                                        this.getTotalAmount().setValue(rst.total_amount_display);
                                    else
                                        this.getTotalAmount().setValue('0,00');
                                },
                                failure: function (response) {
                                    Ext.Msg.show({
                                        title: 'Buscando valor total',
                                        icon: Ext.Msg.INFO,
                                        buttons: Ext.Msg.OK,
                                        msg: 'Não foi possível encontrar o valor total'
                                    });
                                }

                            });
                        } else {
                            this.getTotalAmount().setValue('0,00');
                        }

                    }
                },

                items: [
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.3',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: false,
                                        fieldLabel: "N\u00famero da Ata",
                                        name: "number",
                                        xtype: "textfield",
                                        anchor: '97%',
                                        maxLength: 30,
                                        listeners: {
                                            afterrender: function (field) {
                                                field.focus(false, 1000);
                                            }
                                        }
                                    },
                                ],
                            },
                            {
                                columnWidth: '.3',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: true,
                                        fieldLabel: "N\u00famero do Edital",
                                        name: "notice_number",
                                        xtype: "textfield",
                                        anchor: '97%',
                                        maxLength: 30,
                                    },
                                ],
                            },
                            {
                                columnWidth: '.4',
                                layout: 'form',
                                items: [
                                    this.getBiddingTypeChoiceField()
                                ],
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
                                        xtype: "textfield",
                                        fieldLabel: "N\u00famero do Processo",
                                        allowBlank: true,
                                        name: "process_number",
                                        anchor: '99%'
                                    }
                                ]
                            },
                            {
                                columnWidth: '0.5',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: "textfield",
                                        fieldLabel: "N\u00famero do processo M\u00e3e",
                                        allowBlank: true,
                                        name: "parent_process",
                                        anchor: '99%'
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype: "rest-autocompletefield",
                        fieldLabel: "Contratado",
                        allowBlank: false,
                        rest: "rh.pessoa.Restful",
                        name: "provider",
                        anchor: '99%',

                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.7',
                                layout: 'form',
                                items: [
                                    this.getManagementOrgan()
                                ]
                            },
                            {
                                columnWidth: '.3',
                                layout: 'form',
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Qtd Máx. Adesões',
                                        hiddenName: 'adhesions_quantity',
                                        choiceId: 'contrato.MINUTE_ADHESION_QUANTITY',
                                        anchor: '99%',
                                        listeners: {
                                            scope: this,
                                            render: function () {
                                                if (this.values.adhesions_quantity === undefined)
                                                    this.getFormPanel().getForm().findField('adhesions_quantity').setValue(100);
                                            },
                                        },
                                    }
                                ]
                            },

                        ]

                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Objeto da Ata",
                        name: "minute_object",
                        xtype: "textarea",
                        anchor: '99%',
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    this.getTotalAmount(),
                                ]
                            },
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: false,
                                        fieldLabel: "Data da assinatura",
                                        name: "signature_date",
                                        xtype: "datefield",
                                        anchor: '99%'
                                    },
                                ]
                            }

                        ]
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: false,
                                        fieldLabel: "In\u00edcio Vig\u00eancia",
                                        name: "begin_validity",
                                        xtype: "datefield",
                                        anchor: '98%'
                                    }
                                ]
                            },
                            {
                                columnWidth: '.5',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: false,
                                        fieldLabel: "T\u00e9rmino Vig\u00eancia",
                                        name: "end_validity",
                                        xtype: "datefield",
                                        anchor: '99%'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Execução do Objeto",
                        name: "object_execution",
                        xtype: "textarea",
                        anchor: '99%',
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Aviso de Vencimento ',
                        hiddenName: 'days_for_notice',
                        choiceId: 'contrato.DIAS_AVISO',
                        anchor: '99%',
                    },
                    {
                        layout: 'column',
                        items: [
                            {
                                columnWidth: '.7',
                                layout: 'form',
                                items: [
                                    {
                                        maxLength: 50,
                                        allowBlank: true,
                                        fieldLabel: "N\u00famero do Di\u00e1rio Oficial",
                                        name: "official_diary",
                                        xtype: "textfield",
                                        anchor: '98%',
                                    },
                                ]
                            },
                            {
                                columnWidth: '.3',
                                layout: 'form',
                                items: [
                                    {
                                        allowBlank: true,
                                        fieldLabel: "Data da publica\u00e7\u00e3o",
                                        name: "publication_date",
                                        xtype: "datefield",
                                        anchor: '99%'
                                    },
                                ]
                            },
                        ]
                    },
                ],
            });
        }

        return this._minutePanel;
    },

    getBiddingTypeChoiceField: function (cfg) {
        if (!this._biddingTypeChoiceField) {
            this._biddingTypeChoiceField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo de Pregão',
                hiddenName: 'bidding_type',
                choiceId: 'contrato.TIPO_LICITACAO',
                anchor: '99%'
            });
            var store = this._biddingTypeChoiceField.getStore();
            var filter = Ext.decode(store.baseParams.filter);
            filter.push({ property: 'value__in', value: [3, 4], stage: 1 });
            store.baseParams.filter = Ext.encode(filter);
            store.load();
        }
        return this._biddingTypeChoiceField;

    },

    getTotalAmount: function () {
        if (!this._totalAmount) {
            this._totalAmount = Ext._create('Ext.form.DisplayField', {
                fieldLabel: "Valor Total (R$)",
                name: "total_amount",
            });
        }
        return this._totalAmount;
    },
    
    getMinuteItemGrid: function (cfg) {
        if (!this._minuteItemGrid) {
            this._minuteItemGrid = Ext._create('planning.hiring.minuteitem.MinuteItemGrid', {
                title: 'Grupos',
                region: 'center',
                flex: 1.0,
                minWidth: '50%',
                height: 582,
                frame: true,
                columnAction: false,
            });
        }        

        return this._minuteItemGrid;
    },

    getMainMinuteItemPanel: function (cfg) {
        if (!this._mainMinuteItemPanel)
            this._mainMinuteItemPanel = Ext._create('Ext.Panel', {
                title: 'Itens da Ata',
                layout: 'hbox',
                align: 'stretch',
                height: 582,
                border: false,
                bbar: [],
                items: [
                    this.getMinuteItemGrid(cfg),
                ]
            });
        return this._mainMinuteItemPanel;
    },

    getMinuteAnnotationGrid: function (cfg) {
        if (!this._minuteAnnotationGrid) {
            this._minuteAnnotationGrid = Ext._create('planning.hiring.agreementannotation.MinuteAnnotationGrid', {
                title: 'Anotações',
                region: 'center',
                flex: 1.0,
                minWidth: '50%',
                height: 582,
                frame: true,
                columnAction: false,
            });
        }        

        return this._minuteAnnotationGrid;
    },

    getMinuteAnnotationPanel: function (cfg) {
        if (!this._MinuteAnnotationPanel)
            this._MinuteAnnotationPanel = Ext._create('Ext.Panel', {
                title: 'Anotações da Ata',
                layout: 'hbox',
                align: 'stretch',
                height: 582,
                border: false,
                bbar: [],
                items: [
                    this.getMinuteAnnotationGrid(cfg),
                ]
            });
        return this._MinuteAnnotationPanel;
    },

    getSupervisorPanel: function () {
        if (!this._supervisor) {
            this._supervisor = Ext._create('planning.hiring.supervisor.MinuteSupervisorGrid', {
                title: 'Fiscais',
                hideItemsToolbar: ['remove', 'download'],
                hideActions: ['copy', 'edit', 'remove'],
                allowRemove: false,
                keywordFieldWidth: 265,
                height: 582,
            });
        }

        return this._supervisor;
    },

    getCorporateStructureGrid: function () {
        if (!this._corporateStructureGrid) {
            this._corporateStructureGrid = Ext._create('planning.hiring.corporatestructure.Grid', {
                title: 'Sócios',
                region: 'center',
                flex: 1.0,
                minWidth: '50%',
                height: 582,
                frame: true,
                columnAction: false,
            });
        }        

        return this._corporateStructureGrid;
    },

    getCorporateStructurePanel: function () {
        if (!this._corporateStructurePanel)
            this._corporateStructurePanel = Ext._create('Ext.Panel', {
                title: 'Estrutura Corporativa',
                layout: 'hbox',
                align: 'stretch',
                height: 582,
                border: false,
                bbar: [],
                items: [
                    this.getCorporateStructureGrid(),
                ]
            });
        return this._corporateStructurePanel;
    },

    getMinuteDocumentGrid: function () {
        if (!this._minuteDocumentGrid) {
            this._minuteDocumentGrid = Ext._create('planning.hiring.document.MinuteDocumentGrid', {
                title: 'Arquivos',
                region: 'center',
                flex: 1.0,
                minWidth: '50%',
                height: 582,
                frame: true,
                columnAction: false,
            });
        }

        return this._minuteDocumentGrid;
    },

    getMinuteDocumentPanel: function () {
        if (!this._minuteDocumentPanel)
            this._minuteDocumentPanel = Ext._create('Ext.Panel', {
                title: 'Documentos',
                layout: 'hbox',
                align: 'stretch',
                height: 582,
                border: false,
                bbar: [],
                items: [
                    this.getMinuteDocumentGrid(),
                ]
            });
        return this._minuteDocumentPanel;
    },

    getMinuteSolicitationDisplayTilePanel: function () {
        if (!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                height: '100%',
                width: '50%',
                split: true,
            });

        return this._feedbackDisplayTilePanel;
    },

    getMinuteSolicitationGrid: function (cfg) {
        if (!this._minuteSolicitationGrid) {
            this._minuteSolicitationGrid = Ext._create('planning.hiring.minutesolicitation.MinuteSolicitationGrid', {
                region: 'center',
                height: 582,
                frame: true,
                flex: 1.0,
                columnAction: false
            });
        }

        return this._minuteSolicitationGrid;
    },

    minute: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._minute = value;

            if (observe)
                this.observeMinute();
        }

        return this._minute;
    },

    observeMinute: function () {
        var value = this.minute();

        if (value) {
            this.getMainMinuteItemPanel().enable();

            this.getMinuteItemGrid().setParam('minute', value);
            this.getMinuteItemGrid().setFilterProperty('minute', value, 100);
            this.getMinuteItemGrid().setFilterProperty('status__in', [1, 2, 3, 4], 101);

            //Fiscal
            this.getSupervisorPanel().enable();
            this.getSupervisorPanel().setParam('minute', value);
            this.getSupervisorPanel().setFilterProperty('minute', value, 100);

            this.getMinuteSolicitationGrid().enable();
            this.getMinuteSolicitationGrid().setParam('minute', value);
            this.getMinuteSolicitationGrid().setFilterProperty('minute', value, 100);

            // Estrutura Corporativa
            enterprise_provider = 0
            if (parseInt(this.enterprise_provider) > 0)
                enterprise_provider = this.enterprise_provider
            else
                enterprise_provider = this.values.enterprise_provider;
            this.getCorporateStructurePanel().enable();
            this.getCorporateStructureGrid().enable();
            this.getCorporateStructureGrid().setParam('enterprise', enterprise_provider);
            this.getCorporateStructureGrid().setFilterProperty('enterprise', enterprise_provider, 100);

            //Documents
            this.getMinuteDocumentGrid().enable();
            this.getMinuteDocumentGrid().setParam('minute', value);
            this.getMinuteDocumentGrid().setFilterProperty('minute', value, 100);

            //Anotações
            this.getMinuteAnnotationGrid().enable();
            this.getMinuteAnnotationGrid().setParam('minute', value);
            this.getMinuteAnnotationGrid().setFilterProperty('minute', value, 100);

        } else {
            this.getMainMinuteItemPanel().disable();

            this.getMinuteItemGrid().setParam('minute', 0);
            this.getMinuteItemGrid().setFilterProperty('minute', value, 100, false);
            this.getMinuteItemGrid().getStore().removeAll();

            this.getSupervisorPanel().disable();
            this.getSupervisorPanel().setParam('minute', 0);
            this.getSupervisorPanel().setFilterProperty('minute', 0, 100);

            this.getMinuteSolicitationGrid().disable();
            this.getMinuteSolicitationGrid().setParam('minute', 0);
            this.getMinuteSolicitationGrid().setFilterProperty('minute', 0, 100);
            
            this.getCorporateStructurePanel().disable();
            this.getMinuteSolicitationGrid().disable();

            // Document
            this.getMinuteDocumentGrid().disable();
            this.getMinuteDocumentGrid().setParam('minute', 0);
            this.getMinuteDocumentGrid().setFilterProperty('minute', 0, 100);

            // Annotations
            this.getMinuteAnnotationGrid().disable();
            this.getMinuteAnnotationGrid().setParam('minute', 0);
            this.getMinuteAnnotationGrid().setFilterProperty('minute', 0, 100);
        }
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.minute(instance.pk);
                    this.oId = instance.pk;
                    this.action = 'update';
                    this.enterprise_provider = instance.enterprise_provider;
                    this.getCorporateStructureGrid().setParam('enterprise', this.enterprise_provider);
                    this.getCorporateStructureGrid().setFilterProperty('enterprise', this.enterprise_provider, 100);
                }
            }
        });

        this.getCorporateStructurePanel().disable();
        planning.hiring.minute.MinuteWindow.superclass.constructor.call(this, cfg);
        this.minute(cfg.oId === undefined ? null : cfg.oId);
    }
});
