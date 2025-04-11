Ext._define('edocs.protocolo.requestform.compensateexpense.Window', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    mixins: { '1': 'edocs.protocolo.requestform.mixins.Common' },

    _resource: 'RequestCompensateExpense',

    rest: 'edocs.protocolo.requestform.compensateexpense.Restful',

    width: 900,
    height: 600,
    
    getFinalityField: function (cfg) {
        if (!this._finalityField) {
            this._finalityField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Finalidade',
                name: 'finality',
                anchor: '99%',
                allowBlank: false
            });
        }

        return this._finalityField;
    },

    getOutputDateField: function(cfg) {
        if (!this._outputDateField) {
            this._outputDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de saída",
                name: "output_date",
                width: 200,
                allowBlank: false
            });
        }

        return this._outputDateField;
    }, 

    getReturnDateField: function(cfg) {
        if (!this._returnDateField) {
            this._returnDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: "Data de retorno",
                name: "return_date",
                width: 200,
                allowBlank: false
            });
        }

        return this._returnDateField;
    }, 

    getTotalCompensateField: function (cfg) {
        if (!this._totalCompensateField) {
            this._totalCompensateField = Ext._create('Ext.form.NumberField', {
                fieldLabel: "Total a ressarcir",
                name: "total_compensate",
                width: 200,
                allowBlank: false,
                decimalPrecision: 2,
                allowDecimals: true,
                maxLength: 10
            });
        }

        return this._totalCompensateField;
    },

    getMaterialField: function (cfg) {
        if (!this._materialField) {
            this._materialField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Material',
                name: 'material',
                anchor: '90%',
                allowBlank: false
            });
        }

        return this._materialField;
    },

    getServiceField: function (cfg) {
        if (!this._serviceField) {
            this._serviceField = Ext._create('Ext.form.TextField', {
                fieldLabel: 'Serviço',
                name: 'service',
                anchor: '90%',
                allowBlank: false
            });
        }

        return this._serviceField;
    },

    getCombustibleField: function (cfg) {
        if (!this._combustibleField) {
            this._combustibleField = Ext._create('Ext.form.NumberField', {
                fieldLabel: "Combustível",
                name: "combustible",
                width: 200,
                allowBlank: false,
                decimalPrecision: 2,
                allowDecimals: true,
                maxLength: 10
            });
        }

        return this._combustibleField;
    },

    getNoteFieldSet: function(cfg) {
        if(this._note)
            return this._note

        this._note = Ext._create('Ext.form.FieldSet', {
            title: 'Observação',
            layout: 'anchor',
            style: {marginBottom: '10px'},
            items: [
                {
                    xtype: 'ckeditor',
                    name: 'note',
                    height: 180,
                    toolbarGroups: [
                        { name: 'styles', itens: ['Format'] },
                        { name: 'clipboard' },
                        { name: 'editing' },
                        { name: 'basicstyles', groups: ['basicstyles', 'cleanup'] },
                        {
                            name: 'paragraph',
                            groups: ['list', 'indent', 'blocks', 'align', 'bidi'],
                        }
                    ]
                },
            ]
        });

        return this._note;
    },

    getMainPanel: function (cfg) {
        if (this._mainPanel) {
            return this._mainPanel;
        }

        this._mainPanel = Ext._create('Ext.Panel', {
            frame: true,
            layout: 'form',
            labelWidth: 90,
            items: [
                {
                    xtype: 'fieldset',
                    items: [
                        this.getCodeField(cfg),
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 2.75,
                                    items: this.getHomeCourtField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    style: 'margin-left: 15px',
                                    layout: 'form',
                                    flex: 1.25,
                                    labelWidth: 30,
                                    items: this.getDocumentTypeField('REQUERIMENTO')  // mixin
                                },
                            ]
                        },
                        this.getSubjectField(cfg, {
                            value: 'Requerimento de Ressarcimento de Despesa',
                            readOnly: true,
                        }),
                        this.getControlContainer(cfg),
                        this.getFinalityField(cfg),
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getOutputDateField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getReturnDateField(cfg)
                                }
                            ]
                        },
                    ],
                },
                {
                    xtype: 'fieldset',
                    style: { marginBottom: '1px' },
                    title: 'Ressarcimento das despesas',
                    layout: 'form',
                    items: [
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getTotalCompensateField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getCombustibleField(cfg)
                                }
                            ]
                        },
                        {
                            xtype: 'container',
                            layout: 'hbox',
                            items: [
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getMaterialField(cfg)
                                },
                                {
                                    xtype: 'container',
                                    layout: 'form',
                                    flex: 1.0,
                                    items: this.getServiceField(cfg)
                                }
                            ]
                        },
                    ]
                },
                // this.getNoteFieldSet(cfg)
            ],
        });

        return this._mainPanel;
    }, 

    getCompensatePanel: function (cfg) {
        if (!this._compensatePanel) {
            this._compensatePanel = Ext._create('edocs.protocolo.requestform.compensateexpenseitem.Grid', {
                flex: 1,
                gridAutoLoad: false,
                columnAction: false
            });
        }

        return this._compensatePanel;
    },

    getMainFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.Panel', {
                title: 'Informações',
                frame: false,
                items: [
                    this.getMainPanel(cfg),
                    {
                        layout: 'vbox',
                        border: false,
                        height: 200,
                        padding: '1px 0 0 0',
                        items: this.getAttachmentPanel(cfg),
                    },
                ]
            });
        }

        return this._formPanel;
    },

    getCompensateExpenseFormPanel: function (cfg) {
        if (!this._compensateExpenseformPanel) {
            this._compensateExpenseformPanel = Ext._create('Ext.Panel', {
                title: 'Dados da Nota Fiscal',
                frame: false,
                items: [
                    {
                        layout: 'vbox',
                        border: false,
                        height: 200,
                        padding: '1px 0 0 0',
                        items: this.getCompensatePanel(cfg)
                    },
                    {
                        layout: 'form',
                        frame: true,
                        items: this.getNoteFieldSet(cfg)
                    }
                ]
            });
        }

        return this._compensateExpenseformPanel;
    },

    getTabPanel: function (cfg) {
        if (!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: [
                    this.getMainFormPanel(cfg),
                    this.getCompensateExpenseFormPanel(cfg)
                ]
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                activeTab: 0,
                border: false,
                deferredRender: false,
                items: this.getTabPanel(cfg)
            });
        }

        return this._formPanel;
    },

    observeMovement: function () {
        edocs.protocolo.requestform.compensateexpense.Window.superclass.observeMovement.call(this, {});

        var value = this.movement();
        var grid = this.getCompensatePanel();

        if (value) {
            var protocol = this.values ? this.values.protocol : this.protocol;

            grid.setParam('compensate_item', protocol);
            grid.setFilterProperty('compensate_item__pk', protocol, 100);
        } else {
            grid.setParam('compensate_item', undefined);
            grid.setFilterProperty('compensate_item__pk', undefined, 100, false);
            grid.getStore().removeAll();
        }
    }

});

edocs.protocolo.box.MainGrid.registerSpecialType({
    title: 'Requerimento de Ressarcimento de Despesa',
    iconCls: '',
    restWindow: 'edocs.protocolo.requestform.compensateexpense.Window',
    specialType: 'compensateexpense',
    group: 'Auxílios, indenizações, vales e valores a receber e a antecipar'
});
