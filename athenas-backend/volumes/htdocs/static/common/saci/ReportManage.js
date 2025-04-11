Ext._define('common.saci.ReportManage', {
    extend: 'toolkit.widget.TabPanel',

    report: '/to/mpe/common/siacmp/Analytic_of_Care',

    _reportName: 'Relatório SIACMP',

    _filename: 'siacmp',

    getDepartmentField: function(cfg) {
        if(!this._departmentField)
            this._departmentField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Local',
                allowBlank: true,
                rest: "judicial.params.WorkplaceRestful",
                name: "department",
                gridConfig: {
                    columnAction: false,
                    configOrderToolBar: ['search', '->']
               }
            });

        return this._departmentField;
    },

    filename: function(type) {
        return "".concat(this._filename,"-",{1: 'Analitico', 2 : 'Sintetico', 3: 'Entrada'}[type]);
    },

    reportName: function() {
        return this._reportName;
    },

    getInitialDate: function(){
        if(!this._startfield)
            this._startfield = Ext._create('Ext.form.DateField', {
                anchor: '100%',
                fieldLabel: 'Início',
                name: 'initial',
                maxValue: new Date(),
                allowBlank: false
            });

        return this._startfield;
    },

    getFinalDate: function(){
        if(!this._endfield)
            this._endfield = Ext._create('Ext.form.DateField', {
                anchor: '100%',
                fieldLabel: 'Fim',
                name: 'final',
                value: new Date(),
                maxValue: new Date(),
                allowBlank: false
            });

        return this._endfield;
    },

    getSelectionTypeReport: function() {
        if(!this._typeReport) {
            this._typeReport = Ext._create('Ext.form.RadioGroup', {
                xtype: 'radiogroup',
                fieldLabel: 'Tipo',
                hideLabel: true,
                disabled: false,
                items: [
                    { boxLabel: 'Analítico', name: 'type', inputValue: '1', checked: true },
                    { boxLabel: 'Sintético', name: 'type', inputValue: '2' },
                    { boxLabel: 'Controle de Entrada', name: 'type', inputValue: '3' }
                ]
            });
        }
        return this._typeReport;
    },

    generate: function(values) {
        if(values.tipo == 3)
            this.report = '/to/mpe/common/siacmp/analytic_of_care_visitors';
        else
            this.report = '/to/mpe/common/siacmp/Analytic_of_Care';


        engine.mq.Report.request({
            report: this.report,
            params: Ext.apply(
                values,
                {
                    outfile: this.filename(values.tipo),
                    report_name: this.reportName()
                }
            ),
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
        });
    },

    formatValues: function() {
        var values = {
            success: true
        };
        try {
            try {

                var initial_date = this.getInitialDate().getValue();
                var final_date = this.getFinalDate().getValue();

                values.local = this.getDepartmentField().getValue() || '0';

                var atendente = this.getEmployee().getValue();

                if(atendente!=''){
                    values.atendente = atendente;
                }

                if(!Date.parse(initial_date))
                    throw "Informe uma data inicial válida";
                else
                    values.data_inicial = initial_date.format('Y-m-d');

                if(!Date.parse(final_date))
                    throw "Informe uma data final válida";
                else
                    values.data_final = final_date.format('Y-m-d');

                values.tipo = this.getSelectionTypeReport().getValue().inputValue;
            } catch(e) {

                values.success = false;
                values.msg = e
            }

        } finally {
            return values;
        }
    },

    genereteReport: function() {
        var values = this.formatValues();

        if(values.success) {
            this.generate(values);
        }else {
            Ext.Msg.show({
                title: 'Validação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: values.msg
            });
        }

    },

    getEmployee: function() {
        if (!this._employee) {
            this._employee = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Atendente',
                allowBlank: true,
                rest: "rh.employee.Restful",
                name: "employee",
                gridConfig: {
                    configOrderToolBar: ['search', '->'],
                    hideColumns: ['matricula', 'departure_unicode', 'elective_unicode'],
                    columnAction: false,
                }
            });
        }

        return this._employee;
    },

    getMain: function(){
        if(!this._panel)
        this._panel = Ext._create('Ext.Panel', {
            layout: 'border',
            region: 'center',
            height: 650,
            split: true,
            autoEl: {tag: 'center'},
            items: [
                {
                    region: 'center',
                    border: false,
                    items: [
                        {
                            xtype: 'fieldset',
                            title: 'Relatório de Atendimentos ao Cidadão',
                            width: "33%",
                            style: 'margin: 5px',
                            align: 'center',
                            items: [
                                this.getDepartmentField(),
                                this.getInitialDate(),
                                this.getFinalDate(),
                                this.getEmployee(),
                                this.getSelectionTypeReport(),
                                {
                                    xtype: 'button',
                                    iconCls: 'icon-siatu icon-siatu-move-down',
                                    style: 'margin-top: 10px',
                                    text: 'Gerar relatório',
                                    width: 100,
                                    height: 25,
                                    scope: this,
                                    handler: this.genereteReport,
                                }
                            ]
                        },
                    ]
                }
            ]
        });

        return this._panel;
    },


    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Relatório de atendimento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items:[
                    this.getMain(),
                ]
            }
        );

        common.saci.ReportManage.superclass.constructor.call(this, cfg);
    }
});
