/*****************************************************************************
*                                                                            *
*                            RELATÓRIO CONTRACHEQUE                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.PayCheck', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    _paycheckPkList: '',

    _getStoreOfEndpoint: function (endpoint) {
        if (!this._stores) {
            this._stores = {};
        }

        if (this._stores.hasOwnProperty(endpoint)) {
            return this._stores[endpoint];
        }

        this._stores[endpoint] =  Ext._create('Ext.data.JsonStore', {
            url: core.callAction('GFPReportUsuario', endpoint),
            fields: ['codigo', 'descricao'],
            root: 'result',
            totalProperty: 'totalRows',
            autoLoad: false,
        });

        return this._stores[endpoint];
    },

    _setPeriodParam: function (value) {
        this.getComplementField().clearValue();
        this.getComplementField().getStore().setBaseParam('periodo', value);

        this.getPayrollTypeField().clearValue();
        this.getPayrollTypeField().getStore().setBaseParam('periodo', value);
        this.getPayrollTypeField().getStore().load({});
    },

    _periodLoadEvent: function (store, records, options) {
        if (store.data.length === 0) {
            return;
        }

        var firstValue = store.getAt(0).get(this.getPeriodField().valueField);
        this.getPeriodField().setValue(firstValue);

        this._setPeriodParam(firstValue);
    },

    getPeriodField: function (cfg) {
        if (this._periodField) {
            return this._periodField;
        }

        this._periodField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Período',
            hiddenName: 'periodo',
            valueField: 'codigo',
            displayField: 'descricao',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            store: this._getStoreOfEndpoint('get_store/periodo'),
            listeners: {
                scope: this,
                select: function (combo, record, index) {
                    this._setPeriodParam(record.data.codigo);
                },
            },
        });

        this._periodField.getStore().on({
            scope: this,
            load: this._periodLoadEvent,
        });

        return this._periodField;
    },

    _setPayrollTypeParam: function (value) {
        this.getComplementField().clearValue();
        this.getComplementField().getStore().setBaseParam('folhatipo', value);
        this.getComplementField().getStore().load({});
    },

    _payrollTypeLoadEvent: function(store, records, options) {
        if (store.data.length === 0) {
            return;
        }

        var firstValue = store.getAt(0).get(this.getPayrollTypeField().valueField);
        this.getPayrollTypeField().setValue(firstValue);

        this._setPayrollTypeParam(firstValue);
    },

    getPayrollTypeField: function (cfg) {
        if (this._payrollTypeField) {
            return this._payrollTypeField;
        }

        this._payrollTypeField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Tipo folha',
            hiddenName: 'folhatipo',
            valueField: 'codigo',
            displayField: 'descricao',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            store: this._getStoreOfEndpoint('get_store/folhatipo'),
            listeners: {
                scope: this,
                select: function (combo, record, index) {
                    this._setPayrollTypeParam(record.data.codigo);
                },
            },
        });

        this._payrollTypeField.getStore().on({
            scope: this,
            load: this._payrollTypeLoadEvent,
        });

        return this._payrollTypeField;
    },

    _complementLoadEvent: function (store, records, options) {
        if (store.data.length === 0) {
            return;
        }

        this._complementField.setValue(
            store.getAt(0).get(this._complementField.valueField)
        );
    },

    getComplementField: function (cfg) {
        if (this._complementField) {
            return this._complementField;
        }

        this._complementField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Complemento',
            hiddenName: 'complemento',
            valueField: 'codigo',
            displayField: 'descricao',
            editable: false,
            triggerAction: 'all',
            anchor: '99%',
            store: this._getStoreOfEndpoint('get_store/complemento'),
        });

        this._complementField.getStore().on({
            scope: this,
            load: this._complementLoadEvent,
        });

        return this._complementField;
    },

    _fetchPaycheckList: function (cfg) {
        var mask = new Ext.LoadMask(
            this.ownerCt.getEl() || this.getEl(),
            { msg: 'Processando...' }
        );
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('GFPReportUsuario', 'paycheck_by_period_and_type'),
            params: this.getForm().getValues(),
            scope: this,
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    this._paycheckPkList = result.pk;
                    this.requestReport(cfg);
                    return;
                }

                Ext.Msg.show({
                    title: 'Contracheque',
                    msg: result.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
            failure: function (xhr) {
                Ext.Msg.show({
                    title: 'Contracheque',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
            callback: function () {
                mask.hide();
            },
        });
    },

    _getPeriodDisplay: function () {
        return this.getDisplayByValue({
            store: this.getPeriodField().getStore(),
            valueField: 'codigo',
            value: this.getPeriodField().getValue(),
            displayField: 'descricao',
        });
    },

    _getHelpTemplate: function () {
        if (this._helpTemplate) {
            return this._helpTemplate;
        }

        this._helpTemplate = new Ext.Template(
            '<p style="color:red"><b>Atenção:</b></p>',
            '<p>Para imprimir e visualizar o contracheque, <b>basta selecionar o PERÍODO desejado</b> e clicar no botão <b>"Gerar"</b>.</p>',
            '<p> 1) Caso os campos <b>"Tipo Folha"</b> e <b>"Complemento"</b> estejam <u>em branco</u>, será gerado com <u>todos os lançamentos</u> existentes no período (folha normal e complementar).</p>',
            '<p> 2) Caso deseje imprimir apenas um tipo: normal ou complementar, preencha os demais campos.</p>',
        );

        return this._helpTemplate;
    },

    _showHelp: function () {
        var win = Ext._create('Ext.Window', {
            title: 'Ajuda',
            width: 900,
            height: 200,
            padding: 10,
            bodyStyle: 'font-size: 12pt',
            html: this._getHelpTemplate().apply(),
            buttonAlign: 'center',
            buttons: [{
                text: 'OK',
                scope: this,
                handler: function () {
                    win.destroy();
                },
            }],
        });

        win.show();
    },

    getHelpIcon: function () {
        return ['/', global.Context, '/static/images/question.png'].join('');
    },

    getHelpButton: function (cfg) {
        if (this._helpButton) {
            return this._helpButton;
        }

        this._helpButton = Ext._create('Ext.Button', {
            text: 'Ajuda',
            icon: this.getHelpIcon(),
            scope: this,
            handler: function () {
                this._showHelp();
            },
        });

        return this._helpButton;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: '/to/mpe/gfp/paycheck_by_id',

    getReportFilename: function (cfg) {
        var filename = `contracheque-${this.slugify(this.getEmployeeName())}`;

        var display = this._getPeriodDisplay();
        if (display && typeof display === 'string') {
            filename = `${filename}-${display}`;
        }

        return filename;
    },

    getReportName: function (cfg) {
        var reportName = 'Contra-cheque';

        var display = this._getPeriodDisplay();
        if (display && typeof display === 'string') {
            reportName = `${reportName} - ${display}`;
        }

        return reportName;
    },

    getParams: function (cfg) {
        var params = {
            contracheque: this._paycheckPkList,
        };

        return Ext.apply(params, {
            outfile: this.getReportFilename(cfg),
            report_name: this.getReportName(cfg),
        });
    },

    generateButtonHandle: function (cfg) {
        this._fetchPaycheckList(cfg);
    },

    onFetchEmployeeSuccess: function (data) {
        this.getPayrollTypeField().getStore().setBaseParam('servidor', this.getEmployeeId());
        this.getComplementField().getStore().setBaseParam('servidor', this.getEmployeeId());
        this.getPeriodField().getStore().setBaseParam('servidor', this.getEmployeeId());
        this.getPeriodField().getStore().load({});
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 86,
            items: [
                this.getEmployeeHiddenField(cfg),
                this.getPeriodField(cfg),
                this.getPayrollTypeField(cfg),
                this.getComplementField(cfg),
            ],
            buttonAlign: 'left',
            buttons: [
                this.getGenerateButton(cfg),
                this.getHelpButton(cfg),
            ],
        });

        rh.gfp
          .reports
          .employee
          .forms
          .PayCheck
          .superclass
          .constructor
          .call(this, cfg);
    },
});
