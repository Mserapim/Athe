Ext._define('edocs.reports.IncomingMovementReport', {
    extend: 'toolkit.widget.TabPanel',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    panelTitle: 'Movimentações de entrada',

    reportPath: '/to/mpe/protocolo/movimentacoes_entrada',

    reportName: 'EDOC - Movimentações de entrada',

    filename: 'edoc-relatorio-movimentacoes-de-entrada',

    MAIN_PANEL_WIDTH: 600,

    TIP: [
        '<p>',
            '<b>Nota: </b>',
            'O relatório será gerado com um período máximo de 12 meses, ',
            'mesmo que o período informado ultrapasse essa constante.',
        '</p>'
    ].join(''),

    isInt: function (value) {
        return /^-?[0-9]+$/.test(value);
    },

    getFormattedDate: function (date) {
        return (date instanceof Date ? date.format('Y-m-d') : null);
    },

    getFormattedReportParams: function(cfg) {
        var params = {};

        var origin = this.getOriginDepartmentField().getValue();
        var destination = this.getDestinationDepartmentField().getValue();
        var interested = this.getInterestedPersonField().getValue();
        var documentType = this.getDocumentTypeField().getValue();
        var confidentiality = this.getConfidentialityField().getValue().inputValue;
        var startDate = this.getStartDateField().getValue();
        var endDate = this.getEndDateField().getValue();
        var reportType = this.getReportTypeField().getValue();

        params.lotacao_origem = (this.isInt(origin) ? origin.toString() : null);
        params.lotacao_destino = (this.isInt(destination) ? destination.toString() : null);
        params.interessado = (this.isInt(interested) ? interested.toString() : null);
        params.tipo_documento = (this.isInt(documentType) ? documentType.toString() : null);
        params.sigilosidade = (this.isInt(confidentiality) ? confidentiality.toString() : null);
        params.data_inicial = this.getFormattedDate(startDate);
        params.data_final = this.getFormattedDate(endDate);
        params.tipo_relatorio = (this.isInt(reportType) ? reportType.toString() : null);

        return params;
    },

    requestReport: function(name, path, filename, params) {
        engine.mq.Report.request({
            report: path,
            params: Ext.apply(params, {
                outfile: filename,
                report_name: name
            }),
            el: this.getEl(),
            waitMessage: this.waitMessage
        }, this.outputFormat());
    },

    validateFields: function() {
        var exception = {
            title: 'Erro de validação'
        };

        if (!this.getFormPanel().getForm().isValid()) {
            exception.message = 'Por favor, preencha todos os campos obrigatórios.';
            throw exception;
        }
    },

    generateReport: function(preventClose) {
        try {
            this.validateFields();
            this.requestReport(
                this.reportName,
                this.reportPath,
                this.filename,
                this.getFormattedReportParams()
            );
        } catch(e) {
            Ext.Msg.show({
                title: e.title || 'Erro',
                msg: e.message || e,
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR
            });
        }
    },

    getOriginDepartmentField: function (cfg) {
        if (!this._originDepartmentField) {
            this._originDepartmentField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Local de origem',
                rest: 'rh.workplace.Restful',
                emptyText: 'Informe a origem das movimentações (opcional)',
                preFilter: [
                    {
                        property: 'ativo',
                        value: true,
                        stage: 0
                    },
                    {
                        property: 'habilita_protocolo',
                        value: true,
                        stage: 1
                    }
                ],
            });
        }

        return this._originDepartmentField;
    },

    getDestinationDepartmentField: function (cfg) {
        if (!this._destinationDepartmentField) {
            this._destinationDepartmentField = Ext._create('core.fields.ComboField', {
                fieldLabel: '<b>Local de destino</b>',
                displayField: 'description',
                allowBlank: false,
                anchor: '99.9%',
                emptyText: 'Informe uma lotação à qual você esteja vinculado',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('EDOCManage', 'work_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'}
                        ]
                    })
                })
            });
        }

        return this._destinationDepartmentField;
    },

    getInterestedPersonField: function (cfg) {
        if (!this._interestedPersonField) {
            this._interestedPersonField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Interessado(a)',
                rest: 'rh.person.Restful',
                emptyText: 'Informe a pessoa interessada (opcional)',
                preFilter: [
                    {
                        property: 'enable_protocol',
                        value: true,
                        stage: 1001
                    }
                ],
            });
        }

        return this._interestedPersonField;
    },

    getDocumentTypeField: function (cfg) {
        if (!this._documentTypeField) {
            this._documentTypeField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Tipo de documento',
                emptyText: 'Informe o tipo de documento do protocolo (opcional)',
                rest: 'edocs.protocolo.TipoDocumentoRestful',
                preFilter: [
                    {
                        property: 'habilita',
                        value: 'on',
                        stage: 1001
                    }
                ]
            });
        }

        return this._documentTypeField;
    },

    getConfidentialityField: function (cfg) {
        if (!this._confidentialityField) {
            this._confidentialityField = Ext._create('Ext.form.RadioGroup', {
                fieldLabel: 'Quanto à sigilosidade do protocolo',
                items: [
                    {
                        boxLabel: 'Somente SEM sigilo',
                        name: 'sigilosidade',
                        inputValue: '0',
                        checked: true
                    },
                    {
                        boxLabel: 'Somente COM sigilo',
                        name: 'sigilosidade',
                        inputValue: '1'
                    },
                    {
                        boxLabel: 'Ambos',
                        name: 'sigilosidade',
                        inputValue: ''
                    },
                ]
            });
        }

        return this._confidentialityField;
    },

    getStartDateField: function(cfg) {
    	if (!this._startDateField) {
    		this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: '<b>De</b>',
                allowBlank: false,
                name: 'data_inicial',
                anchor: '95%'
            });
        }

    	return this._startDateField;
    },

    getEndDateField: function(cfg) {
    	if (!this._endDateField) {
    		this._endDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: '<b>Até</b>',
                allowBlank: false,
                name: 'data_final',
                anchor: '95%'
            });
        }

    	return this._endDateField;
    },

    getReportTypeField: function (cfg) {
        if (!this._reportTypeField) {
            this._reportTypeField = Ext._create('Ext.form.ComboBox', {
                name: 'tipo_relatorio',
                fieldLabel: 'Tipo de relatório',
                triggerAction: 'all',
                editable: false,
                width: 171,
                value: '0',
                store: [
                    ['0', 'SINTÉTICO'],
                    ['1', 'ANALÍTICO'],
                ]
            });
        }

        return this._reportTypeField;
    },

    getResetButton: function(cfg) {
        if (!this._resetButton) {
            this._resetButton = Ext._create('Ext.Button', {
                iconCls: 'icon-edocs icon-protocolo-clear',
                text: 'Limpar',
                handler: function() {
                    this.getFormPanel().getForm().reset();
                    this.getDestinationDepartmentField().focus();
                },
                scope: this
            });
        }

        return this._resetButton;
    },

    getTipPanel: function (cfg) {
        if (!this._tipPanel) {
            this._tipPanel = Ext._create('Ext.Panel', {
                border: false,
                bodyStyle: 'padding-top: 20px; padding-bottom: 20px;',
                items: [{
                    xtype: 'label',
                    html: this.TIP,
                    style: {fontSize: '8pt'}
                }]    
            });
        }
        return this._tipPanel;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelAlign: 'top',
                defaults: {
                    style: {marginBottom: '10px'},
                },
                items: [
                    this.getOriginDepartmentField(cfg),
                    this.getDestinationDepartmentField(cfg),
                    this.getInterestedPersonField(cfg),
                    this.getDocumentTypeField(cfg),
                    {
                        xtype: 'panel',
                        border: false,
                        layout: 'column',
                        defaults: {
                            border: false,
                            layout: 'form',
                        },
                        items: [
                            {
                                columnWidth: 0.35,
                                items: this.getStartDateField(cfg)
                            },
                            {
                                columnWidth: 0.35,
                                items: this.getEndDateField(cfg)
                            },
                            {
                                columnWidth: 0.3,
                                items: this.getReportTypeField(cfg)
                            }
                        ]
                    },
                    this.getConfidentialityField(cfg),
                    this.getTipPanel(cfg),
                ],
                buttons: [
                    this.getRunReportButton(),
                    this.getResetButton(),
                ],
                buttonAlign: 'center'
            });
        }

        return this._formPanel;
    },

    getMainPanel: function (cfg) {
        if (!this._mainPanel) {
            // Posiciona o panel no centro.
            var panelWidth = this.MAIN_PANEL_WIDTH;
            var panelLeft = (window.innerWidth / 2) - (panelWidth / 2);
            var panelTop = 15;

            this._mainPanel = Ext._create('Ext.Panel', {
                title: this.panelTitle,
                border: true,
                x: panelLeft,
                y: panelTop,
                width: panelWidth,
                bodyStyle: 'padding: 10px',
                items: [this.getFormPanel(cfg)]
            });
        }

        return this._mainPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'EDOC - Relatórios',
        });

        Ext.apply(cfg, {
            layout: 'absolute',
            items: this.getMainPanel(cfg),
        });

        edocs.reports.IncomingMovementReport.superclass.constructor.call(this, cfg);
    }
});
