/*****************************************************************************
*                                                                            *
*                     RELATÓRIO COMPROVANTE DE RENDIMENTOS                   *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.ComprovanteRendimentos', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    _getCalendarYearDisplay: function () {
        return this.getDisplayByValue({
            store: this.getCalendarYearField().getStore(),
            valueField: 'pk',
            value: this.getCalendarYearField().getValue(),
            displayField: 'nome',
        });
    },

    _calendarYearLoadEvent: function (store, records, options) {
        if (store.data.length === 0) {
            return;
        }

        var firstValue = store.getAt(0).get(this.getCalendarYearField().valueField);
        this.getCalendarYearField().setValue(firstValue);
    },

    getCalendarYearStore: function (cfg) {
        if (this._calendarYearStore) {
            return this._calendarYearStore;
        }

        this._calendarYearStore =  Ext._create('Ext.data.JsonStore', {
            url: core.callAction('GFPComprovanteRendimentosServidor', 'get_store/periodos'),
            fields: ['pk', 'nome'],
            root: 'result',
            totalProperty: 'totalRows',
            autoLoad: false,
        });

        return this._calendarYearStore;
    },

    getNaturalPersonField: function (cfg) {
        if (this._naturalPersonField) {
            return this._naturalPersonField;
        }

        this._naturalPersonField = Ext._create('Ext.form.Hidden', {
            name: 'pessoa_fisica',
            value: 0,
            allowBlank: false,
        });

        return this._naturalPersonField;
    },

    getCalendarYearField: function (cfg) {
        if (this._calendarYearField) {
            return this._calendarYearField;
        }

        this._calendarYearField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Demonstrativo',
            hiddenName: 'declaracao',
            displayField: 'nome',
            valueField: 'pk',
            triggerAction: 'all',
            editable: false,
            anchor: '99%',
            store: this.getCalendarYearStore(cfg),
        });

        this._calendarYearField.getStore().on({
            scope: this,
            load: this._calendarYearLoadEvent,
        });

        return this._calendarYearField;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: '/to/mpe/gfp/comprovanterendimentos',

    getReportName: function (cfg) {
        var reportName = 'Comprovante de Rendimentos';

        var display = this._getCalendarYearDisplay();
        if (display && typeof display === 'string') {
            reportName = `${reportName} - ${display}`;
        }

        return reportName;
    },

    getReportFilename: function (cfg) {
        var filename = `comprovante-de-rendimentos-${this.slugify(this.getEmployeeName())}`;

        var display = this._getCalendarYearDisplay();
        if (display && typeof display === 'string') {
            filename = `${filename}-${display}`;
        }

        return filename;
    },

    onFetchEmployeeSuccess: function (data) {
        this.getNaturalPersonField().setValue(this.getNaturalPersonId());
        this.getCalendarYearField().getStore().setBaseParam('servidor', this.getEmployeeId());
        this.getCalendarYearField().getStore().load({});
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 90,
            items: [
                this.getNaturalPersonField(cfg),
                this.getCalendarYearField(cfg),
            ],
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],
        });

        rh.gfp
          .reports
          .employee
          .forms
          .ComprovanteRendimentos
          .superclass
          .constructor
          .call(this, cfg);
    },
});
