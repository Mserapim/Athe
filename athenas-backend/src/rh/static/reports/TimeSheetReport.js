Ext._define('rh.reports.TimeSheetReport', {
    extend: 'toolkit.widget.TabPanel',


    getFormPanel: function () {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                // frame: true,
                labelWidth: 100,
                autoHeight: true,
                width: 500,
                items: [
                    this.getEmployeeField(),
                    this.getMonthField(),
                    this.getYearField(),
                ]
            });

        return this._formPanel;
    },

    getEmployeeField: function () {
        if (!this._employeefield)
            this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'servidor',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350
            });

        return this._employeefield;
    },

    getYearField: function () {
        if (!this._yearField)
            this._yearField = Ext._create('Ext.form.TextField', {
                name: 'year',
                fieldLabel: 'Ano',
                width: 350
            });

        return this._yearField;
    },

    getMonthField: function () {
        if (!this._monthField) {
            this._monthField = new Ext.form.ComboBox({
                fieldLabel: 'Mês',
                hiddenName: 'mes',
                width: 350,
                store: [
                    [1, 'JANEIRO'],
                    [2, 'FEVEREIRO'],
                    [3, 'MARÇO'],
                    [4, 'ABRIL'],
                    [5, 'MAIO'],
                    [6, 'JUNHO'],
                    [7, 'JULHO'],
                    [8, 'AGOSTO'],
                    [9, 'SETEMBRO'],
                    [10, 'OUTUBRO'],
                    [11, 'NOVEMBRO'],
                    [12, 'DEZEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local'
            });
        }
        return this._monthField;
    },

    getMain: function () {
        if (!this._panel)
            this._panel = Ext._create('Ext.Panel', {
                layout: 'border',
                region: 'center',
                height: 650,
                split: true,
                autoEl: { tag: 'center' },
                items: [
                    {
                        region: 'center',
                        border: false,
                        items: [
                            {
                                xtype: 'fieldset',
                                title: 'Folha de Ponto',
                                width: 650,
                                style: 'margin: 5px',
                                align: 'left',
                                items: [
                                    this.getFormPanel(),
                                    {
                                        xtype: 'button',
                                        iconCls: 'icon-siatu icon-siatu-move-down',
                                        style: 'margin-top: 10px',
                                        text: 'Gerar Relatório',
                                        width: 100,
                                        height: 25,
                                        scope: this,
                                        handler: this.generate,
                                    }
                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function () {
        selected = this.getEmployeeField().getComboField().getStore().find('pk', this.getEmployeeField().getValue());
        employee_type = this.getEmployeeField().getComboField().getStore().getAt(selected).data.tipo;
        var report = '/to/mpe/rh/ponto/main';
        if (employee_type == 'E') {
            report = '/to/mpe/rh/ponto/main_estagiario';
        }
        engine.mq.Report.request({
            report: report,
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'folha_ponto',
                    report_name: 'Folha de Ponto',
                    servidor: this.getEmployeeField().getValue(),
                    ano: this.getYearField().getValue(),
                    mes: this.getMonthField().getValue()
                }
            ),
        });
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Folha de Ponto -----',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getMain(),
                ],
            }
        );

        rh.reports.TimeSheetReport.superclass.constructor.call(this, cfg);
    }
});
