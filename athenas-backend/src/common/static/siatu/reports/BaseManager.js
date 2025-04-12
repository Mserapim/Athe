Ext._define('common.siatu.reports.BaseManager', {
    extend: 'toolkit.widget.TabPanel',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    panelTitle: 'SIATU - Relatórios',

    reportPath: undefined,

    reportName: 'SIATU - Relatório',

    filename: 'siatu-relatorio',

    MAIN_PANEL_WIDTH: 600,

    isInt: function (value) {
        return /^-?[0-9]+$/.test(value);
    },

    getFormattedDate: function (date) {
        return (date instanceof Date ? date.format('Y-m-d') : null);
    },

    getFormattedReportParams: function(cfg) {
        var params = {};

        var startDate = this.getStartDateField().getValue();
        var endDate = this.getEndDateField().getValue();
        var attendant = this.getAttendantField().getValue();
        var service = this.getServiceField().getValue();

        params.data_inicial = this.getFormattedDate(startDate);
        params.data_final = this.getFormattedDate(endDate);
        params.atendente = (this.isInt(attendant) ? attendant.toString() : null);
        params.servico = (this.isInt(service) ? service.toString() : null);

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

    getResetButton: function(cfg) {
        if (!this._resetButton)
            this._resetButton = Ext._create('Ext.Button', {
                iconCls: 'icon-siatu icon-siatu-clear',
                text: 'Limpar',
                handler: function() {
                    this.getFormPanel().getForm().reset();
                    this.getStartDateField().focus();
                },
                scope: this
            });
        return this._resetButton;
    },

    getServiceField: function(cfg) {
        if (!this._serviceField) {
            var percentage = 98;
            var width = Math.round((percentage * this.MAIN_PANEL_WIDTH) / 100);

            this._serviceField = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Serviço',
                allowBlank: true,
                name: 'area',
                width: width,
                treeConfig: {
                    listeners: {
                        render: function(tree) {
                            tbar = tree.getToolbar();
                            tbar.remove(tbar.getComponent(0)); //Adicionar
                            tbar.remove(tbar.getComponent(0)); //Editar
                            tbar.remove(tbar.getComponent(0)); //Remover
                            tbar.remove(tbar.getComponent(0)); //Separador
                            tbar.remove(tbar.getComponent(0)); //Mover
                            tbar.remove(tbar.getComponent(0)); //Separador
                        },
                        load: function(node) {
                            Ext.each(
                                node.childNodes,
                                function(childNode) {
                                    if ((childNode.text == 'Administrativo') ||
                                        (childNode.text == 'Almoxarifado') ||
                                        (childNode.text == 'Informática') ||
                                        (childNode.text == 'Banco de dados') ||
                                        (childNode.text == 'Manutenção de Informática') ||
                                        (childNode.text == 'Redes e comunicação') ||
                                        (childNode.text == 'Sistemas de informação') ||
                                        (childNode.text == 'Transporte')) {
                                            childNode.disable();
                                    }
                                },
                                this
                            );
                        }
                    }
                }
            })
        }
        return this._serviceField;
    },

    getAttendantField: function(cfg) {
        if (!this._attendantField) {
            this._attendantField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Atendente',
                name: 'atendente',
                rest: 'common.siatu.atendente.Restful',
                allowBlank: true,
                anchor: '99.7%',
                gridColumnAction: false,
                gridConfig: {
                    hideItemsToolbar: ['add', 'remove', 'edit', 'notificacao']
                }
            });
        }
        return this._attendantField;
    },

    getEndDateField: function(cfg) {
    	if (!this._endDateField)
    		this._endDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'Até',
                allowBlank: false,
                name: 'data_final',
                anchor: '99%'
            });
    	return this._endDateField;
    },

    getStartDateField: function(cfg) {
    	if (!this._startDateField)
    		this._startDateField = Ext._create('Ext.form.DateField', {
                fieldLabel: 'De',
                allowBlank: false,
                name: 'data_inicial',
                anchor: '95%'
            });
    	return this._startDateField;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelAlign: 'top',
                items: [
                    {
                        xtype: 'panel',
                        border: false,
                        layout: 'column',
                        defaults: {
                            border: false,
                            columnWidth: 0.5,
                            layout: 'form',
                        },
                        items: [
                            {
                                items: this.getStartDateField(cfg)
                            },
                            {
                                items: this.getEndDateField(cfg)
                            }
                        ]
                    },
                    this.getAttendantField(cfg),
                    this.getServiceField(cfg),
                ],
                buttons: [
                    this.getRunReportButton(),
                    this.getResetButton()
                ],
                buttonAlign: 'center'
            });
        }
        return this._formPanel;
    },

    getMainPanel: function(cfg) {
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

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'SIATU - Relatórios'
        });

        Ext.apply(cfg, {
            layout: 'absolute',
            items: this.getMainPanel(cfg)
        });

        common.siatu.reports.BaseManager.superclass.constructor.call(this, cfg);
    }
});
