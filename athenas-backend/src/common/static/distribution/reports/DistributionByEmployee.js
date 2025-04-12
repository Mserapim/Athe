Ext._define('common.distribution.reports.DistributionByEmployee', {
    extend: 'Ext.Window',

    mixins: {
        '1': 'engine.mq.OutputFormatReportMixin'
    },

    reportPath: '/to/mpe/common/distribution/report_by_server',

    reportName: 'Quantitativo de distribuição por servidor',

    filename: 'relatorio-quantitativo-de-distribuicao-por-servidor',

    getReportParams: function () {
        var params = {};

        selections = this.getOriginCheckboxGrid().getSelectionModel().getSelections();
        params.local = selections.map(function (selection) {
            return selection.data.pk;
        }).join(',');

        params.mes = this.getMonthField().getValue();
        params.ano = this.getYearField().getValue();

        params.distribuicao = null;
        if (this.getDistributionField().checked && this.pkset)
            params.distribuicao = this.pkset;

        return params;
    },

    requestReport: function (name, path, filename, params) {
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

    validateFields: function () {
        var exception = {
            title: 'Erro de validação'
        };

        if (!this.getFormPanel().getForm().isValid()) {
            exception.message = 'Por favor, preencha todos os campos obrigatórios.';
            throw exception;
        }

        if (this.getOriginCheckboxGrid().getSelectionModel().getSelections().length < 1) {
            exception.message = 'Por favor, indique pelo menos uma origem.';
            throw exception;
        }
    },

    generateReport: function (preventClose) {
        try {
            this.validateFields();
            this.requestReport(
                this.reportName,
                this.reportPath,
                this.filename,
                this.getReportParams()
            );
        } catch (e) {
            Ext.Msg.show({
                title: e.title || 'Erro',
                msg: e.message || e,
                buttons: Ext.Msg.OK,
                icon: Ext.Msg.ERROR
            });
        }
    },

    getYearField: function (cfg) {
        if (!this._yearField) {
            this._yearField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Ano',
                allowBlank: false,
                width: 180,
                value: new Date().getFullYear()
            });
        }

        return this._yearField;
    },

    getMonthField: function (cfg) {
        if (!this._monthField)
            this._monthField = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Mês',
                allowBlank: false,
                width: 180,
                triggerAction: 'all',
                editable: false,
                store: [
                    ['1', 'JANEIRO'],
                    ['2', 'FEVEREIRO'],
                    ['3', 'MARÇO'],
                    ['4', 'ABRIL'],
                    ['5', 'MAIO'],
                    ['6', 'JUNHO'],
                    ['7', 'JULHO'],
                    ['8', 'AGOSTO'],
                    ['9', 'SETEMBRO'],
                    ['10', 'OUTUBRO'],
                    ['11', 'NOVEMBRO'],
                    ['12', 'DEZEMBRO'],
                ]
            });
        return this._monthField;
    },

    getDistributionField: function (cfg) {
        if (!this._distributionField) {
            this._distributionField = Ext._create('Ext.form.Checkbox', {
                boxLabel: 'Gerar somente para as distribuições selecionadas',
                checked: false,
                allowBlank: true,
                disabled: cfg.pkset.length > 0 ? false : true,
                style: { marginTop: '10px' }
            });
        }

        return this._distributionField;
    },

    getCloseButton: function (cfg) {
        if (!this._closeButton) {
            this._closeButton = Ext._create('Ext.Button', {
                text: 'Fechar',
                scope: this,
                handler: this.close
            });
        }

        return this._closeButton;
    },

    getOriginCheckboxGrid: function () {
        if (!this._multiReportGrid) {
            var selectionModel = new Ext.grid.CheckboxSelectionModel({ checkOnly: true });

            this._multiReportGrid = Ext._create('Ext.grid.GridPanel', {
                fieldLabel: 'Origem',
                sm: selectionModel,
                stripRows: true,
                style: { border: '1px solid #99bbe8' },
                columnLines: true,
                height: 150,
                anchor: '99%',
                autoExpandColumn: 'description',
                store: Ext._create('Ext.data.Store', {
                    autoLoad: true,
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('CDDistribution', 'employee_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            { name: 'pk', type: 'int' },
                            { name: 'description', type: 'string' }
                        ]
                    })
                }),
                columns: [
                    selectionModel,
                    { header: 'Id', dataIndex: 'pk', hidden: true, width: 50 },
                    { header: 'Descrição', dataIndex: 'description', id: 'description' },
                ],
            });
        }

        return this._multiReportGrid;
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 50,
                items: [
                    {
                        xtype: 'panel',
                        layout: 'column',
                        defaults: { columnWidth: 0.5, layout: 'form' },
                        items: [
                            { items: this.getMonthField(cfg) },
                            { items: this.getYearField(cfg) }
                        ]
                    },
                    this.getOriginCheckboxGrid(cfg),
                    this.getDistributionField(cfg),
                ],
            });
        }

        return this._formPanel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Relatório quantitativo de distribuição por servidor',
            width: 600,
            height: 300,
            modal: true,
            resizable: false,
        });

        Ext.apply(cfg, {
            border: false,
            layout: 'fit',
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                this.getRunReportButton(),
                this.getCloseButton(),
            ],
        });

        common.distribution.reports.DistributionByEmployee.superclass.constructor.call(this, cfg);
    }
});
