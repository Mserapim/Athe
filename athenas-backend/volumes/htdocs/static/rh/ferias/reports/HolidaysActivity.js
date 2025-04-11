Ext._define('rh.ferias.reports.HolidaysActivity', {
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
                    this.getStartDate(),
                    this.getEndDate(),
                    this.getType(),
                    this.getEmployeeField()
                ]
            });

        return this._formPanel;
    },

    getStartDate: function () {
        if (!this._startdate)
            this._startdate = Ext._create('Ext.form.DateField', {
                name: 'start_date',
                fieldLabel: "Data Início",
                hidden: false,
                width: 350,
            });
        return this._startdate;
    },

    getEndDate: function () {
        if (!this._enddate)
            this._enddate = Ext._create('Ext.form.DateField', {
                name: 'end_date',
                fieldLabel: "Data Fim",
                hidden: false,
                width: 350,
            });
        return this._enddate;
    },

    getType: function () {
        if (!this._typeField) {
            this._typeField = new Ext.form.ComboBox({
                fieldLabel: 'Tipo',
                hiddenName: 'type',
                width: 350,
                store: [
                    ['S', 'SERVIDOR'],
                    ['M', 'MEMBRO'],
                ],
                triggerAction: 'all',
                mode: 'local',
                listeners: {
                    scope: this,
                    select: function (combo, record, index) {
                        if (record != undefined &&
                            record != '' &&
                            this.getEmployeeField().getValue() != undefined &&
                            this.getEmployeeField().getValue() != ''
                        ) {
                            Ext.Msg.show({
                                'title': 'Alerta!',
                                'icon': Ext.Msg.INFO,
                                'buttons': Ext.Msg.OK,
                                'msg': 'Quando Tipo é escolhido o campo Servidor é desmarcado.',
                            });
                            this.getEmployeeField().setValue(undefined);
                        }
                    },
                }
            });
        }
        return this._typeField;
    },

    getEmployeeField: function () {
        if (!this._employeefield)
            this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350,
                comboListeners: {
                    scope: this,
                    changevalid: function (combo, value, oldvalue, valid) {
                        if (this._observeEmployee != value)
                            this._observeEmployee = false;

                        if (value != undefined &&
                            value != '' &&
                            this.getType().getValue() != undefined &&
                            this.getType().getValue() != '' &&
                            !this._observeEmployee
                        ) {
                            this._observeEmployee = value;
                            Ext.Msg.show({
                                'title': 'Alerta!',
                                'icon': Ext.Msg.INFO,
                                'buttons': Ext.Msg.OK,
                                'msg': 'Quando Servidor é escolhido o campo Tipo é desmarcado.',
                            });
                            this.getType().setValue(undefined);
                        }
                    }
                }
            });
        return this._employeefield;
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
                                title: 'Atividade de Férias',
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
                                        // handler: this.generate,
                                         menu: {
                                            scope: this,
                                            items: [
                                                {
                                                    text: 'Arquivo PDF ',
                                                    type: 'PDF',
                                                    iconCls: 'icon-ged icon-ged-application-pdf',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                                {
                                                    text: 'Arquivo ODT',
                                                    type: 'ODT',
                                                    iconCls: 'icon-ged icon-ged-application-msword',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                                {
                                                    text: 'Arquivo XLS',
                                                    type: 'XLS',
                                                    iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
                                                    scope: this,
                                                    handler: function (item) {
                                                        this.generate(item.type);
                                                    }
                                                },
                                            ]
                                        },
                                    }
                                ]
                            },

                        ]
                    }
                ]
            });

        return this._panel;
    },


    generate: function (type) {
        var startdate = Ext.util.Format.date(this.getStartDate().getValue(), 'Y-m-d');
        var enddate = Ext.util.Format.date(this.getEndDate().getValue(), 'Y-m-d');
        selected = this.getEmployeeField().getComboField().getStore().find('pk', this.getEmployeeField().getValue());
        if(startdate == '' || enddate == ''){
            Ext.Msg.show({
                title: this.title,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'As datas são de preenchimento obrigatório.'
            }, type);
            return;
        }
        if(selected == -1){
            mat = ''
        }
        else{
            mat = this.getEmployeeField().getComboField().getStore().getAt(selected).data.matricula
        }
        engine.mq.Report.request({
            report: '/to/mpe/rh/ferias/atividades_ferias',
            waitMessage: 'Gerando relatório...',
            params: Ext.apply(
                {
                    outfile: 'atividade_ferias',
                    report_name: 'Atividade de Férias',
                    mat: mat,
                    tipo: this.getType().getValue(),
                    dt_inicial: startdate,
                    dt_final: enddate
                }
            ),
        });
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Relatório -> Atividade de Férias',
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
        this._observeEmployee = false;
        this._observeType = false;
        rh.ferias.reports.HolidaysActivity.superclass.constructor.call(this, cfg);
    }
});
