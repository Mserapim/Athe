Ext._define('common.siatu.reports.AttendanceAvaliationGraphicsManager', {
    extend: 'toolkit.widget.TabPanel',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    _reportPath: '/to/mpe/common/siatu/atendentes_avaliacao_periodo/graficos',

    _reportName: 'Relatório de Gráficos de Avaliações de Atendimentos',

    _filename: 'siatu-relatorio-graficos-avaliacoes-atendimentos',

    MAIN_PANEL_WIDTH: 600,

    TIP: [
        '<p>',
            '<b>DICA: </b>',
            'Para gerar um relatório mais geral ',
            'deixe um ou mais campos em branco.',
        '</p>'
    ].join(''),

    _getWidthByPercentage: function(input) {
        return Math.round((input.percentage * input.maxWidth) / 100);
    },

    showError: function(title, msg) {
        Ext.Msg.show({
            title: title,
            msg: msg,
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR
        });
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

    _isInt: function(value) {
        return value % 1 === 0;
    },

    getFormattedReportParams: function(cfg) {
        var params = {};

        params.atendente = this.getAttendantField().getValue() || 0;
        params.ano = this.getYearField().getValue() || 0;
        params.servico = this.getServiceField().getValue().trim() || 0;

        return params;
    },

    validateFields: function() {
        var exception = {
            title: 'Erro de validação'
        };

        var serviceId = this.getServiceField().getValue().trim();
        if (isNaN(serviceId) || !this._isInt(serviceId)) {
            exception.message = "Por favor, preencha o campo '" +
                this.getServiceField().fieldLabel +
                "' corretamente.";
            throw exception;
        }
    },

    generateReport: function(preventClose) {
        try {
            this.validateFields();
            this.requestReport(
                this._reportName,
                this._reportPath,
                this._filename,
                this.getFormattedReportParams()
            );
        } catch(e) {
            this.showError(e.title || 'Erro', e.message || e);
        }
    },

    getResetButton: function(cfg) {
        if (!this._resetButton)
            this._resetButton = Ext._create('Ext.Button', {
                iconCls: 'icon-siatu icon-siatu-clear',
                text: 'Limpar',
                handler: function() {
                    this.getFormPanel().getForm().reset();
                    this.getYearField().focus();
                },
                scope: this
            });
        return this._resetButton;
    },

    getServiceField: function(cfg){
        if (!this._serviceField){
            var percentage = 98;
            var width = Math.round((percentage * this.MAIN_PANEL_WIDTH) / 100);

            this._serviceField = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Serviço',
                name: 'area',
                width: width,
                treeConfig:{
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

    getAttendantField: function(cfg){
        if (!this._attendantField){
            this._attendantField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Atendente',
                name: 'atendente',
                rest: 'common.siatu.atendente.Restful',
                gridColumnAction: false,
                gridConfig: {
                    hideItemsToolbar: ['add', 'remove', 'edit', 'notificacao']
                }
            });
        }
        return this._attendantField;
    },

    getYearStore: function(cfg, initialYear) {
        initialYear = initialYear || 1990;
        var currentYear = (new Date()).getFullYear();
        var store = [];
        for (var year=currentYear; year >= initialYear; year--)
            store.push([year.toString(), year.toString()]);
        return store;
    },

    getYearField: function(cfg) {
        if (!this._yearField)
            this._yearField = Ext._create('Ext.form.ComboBox', {
                name: 'ano',
                fieldLabel: 'Ano',
                triggerAction: 'all',
                editable: false,
                store: this.getYearStore(),
                anchor: '90%'
            });
        return this._yearField;
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

    getFormPanel: function(cfg) {
        if (!this._formPanel)
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
                            layout: 'form',
                        },
                        items: [
                            {
                                columnWidth: 0.3,
                                items: this.getYearField(cfg)
                            },
                            {
                                columnWidth: 0.7,
                                items: this.getAttendantField(cfg)
                            }
                        ]
                    },
                    this.getServiceField(cfg),
                    this.getTipPanel(cfg),
                ],
                buttons: [
                    this.getRunReportButton(),
                    this.getResetButton()
                ],
                buttonAlign: 'center'
            });
        return this._formPanel;
    },

    getMainPanel: function(cfg) {
        if (!this._mainPanel) {
            // Posiciona o panel no centro.
            var panelWidth = this.MAIN_PANEL_WIDTH;
            var panelLeft = (window.innerWidth / 2) - (panelWidth / 2);
            var panelTop = 15;

            this._mainPanel = Ext._create('Ext.Panel', {
                title: 'Gráficos de Avaliações de Atendimentos',
                border: true,
                x: panelLeft,
                y: panelTop,
                width: panelWidth,
                bodyStyle: 'padding: 10px',
                items: [this.getFormPanel(cfg)],
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

        common.siatu.reports.AttendanceAvaliationGraphicsManager.superclass.constructor.call(this, cfg);
    }
});
