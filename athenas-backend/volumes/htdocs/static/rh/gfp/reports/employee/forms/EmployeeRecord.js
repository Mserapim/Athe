/*****************************************************************************
*                                                                            *
*                         RELATÓRIO FICHA FUNCIONAL                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.EmployeeRecord', {
    extend: 'rh.gfp.reports.employee.forms.BaseForm',

    _extraParams: {
        todas_anot: 1,
        endereco: 1,
        dependente: 1,
        anot_geral: 1,
        anot_afastamento: 1,
        anot_ausencia: 1,
        anot_carreira: 1,
        anot_enquadramento: 1,
        anot_elogio: 1,
        anot_evento: 1,
        anot_falta: 1,
        anot_ferias: 1,
        anot_folga_eleitoral: 1,
        anot_gratificacao: 1,
        anot_licenca: 1,
        anot_pena_disciplinar: 1,
        anot_plantao: 1,
        anot_recesso: 1,
        anot_remocao: 1,
        anot_tempo_dobro: 1,
        anot_tempo_servico: 1,
        anot_transposicao: 1,
        anot_viagem: 1,
        anot_aposentadoria: 0,
        anot_promocao: 0,
        upload_dir: '',
    },

    getEmployeeField: function (cfg) {
        if (this._employeeField) {
            return this._employeeField;
        }

        this._employeeField = Ext._create('Ext.form.ComboBox', {
            fieldLabel: 'Servidor',
            hiddenName: 'servidor',
            displayField: 'name',
            valueField: 'id',
            triggerAction: 'all',
            editable: false,
            anchor: '99%',
            store: [[0, ' - - - - - - - - - - ']],
        });

        return this._employeeField;
    },


    /*****************************************************************************
    *                     PROPRIEDADES E MÉTODOS SOBRESCRITOS                    *
    *****************************************************************************/

    reportPath: '/to/mpe/rh/servidor/ficha_funcional',

    onFetchEmployeeSuccess: function (data) {
        this.getEmployeeField().getStore().loadData([
            [this.getEmployeeId(), this.getEmployeeName()],
        ]);
        this._extraParams.upload_dir = this.getStorageDir();
        this.getEmployeeField().setValue(this.getEmployeeId());
    },

    getReportName: function (cfg) {
        return 'Ficha Funcional';
    },

    getReportFilename: function (cfg) {
        return `ficha-funcional-${this.slugify(this.getEmployeeName())}`;
    },

    getParams: function (cfg) {
        var params = this.getForm().getValues();
        Ext.apply(params, this._extraParams);

        return Ext.apply(params, {
            outfile: this.getReportFilename(cfg),
            report_name: this.getReportName(cfg),
        });
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            border: false,
            labelWidth: 66,
            items: [ this.getEmployeeField(cfg) ],
            buttonAlign: 'left',
            buttons: [ this.getGenerateButton(cfg) ],
        });

        rh.gfp
          .reports
          .employee
          .forms
          .EmployeeRecord
          .superclass
          .constructor
          .call(this, cfg);
    },
});
