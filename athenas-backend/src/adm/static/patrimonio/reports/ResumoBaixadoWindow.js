/**
 *
 **/
Ext._define('adm.patrimonio.reports.ResumoBaixadoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: '/to/mpe/adm/patrimonio/Resumo_Sintetico_de_Bens_Baixado',

    _filename: 'resumo-sintetico-de-bens-baixado',

    _reportName: 'Resumo Sintético de Bens Baixado',

    getValues: function() {
        var values = this.getFormPanel().getForm().getValues();

        values.data_inicial = this.castDate(values.data_inicial);
        values.data_final = this.castDate(values.data_final);

        return values;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 45,
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        hiddenName: 'proprio',
                        choiceId: 'patrimonio.REPORT_TYPE_SIMPLE'
                    },
                    {
                        xtype: 'datefield',
                        name: 'data_inicial',
                        fieldLabel: 'De',
                        allowBlank: false
                    },
                    {
                        xtype: 'datefield',
                        name: 'data_final',
                        fieldLabel: 'Até',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: this.reportName(),
                width: 285
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.reports.ResumoBaixadoWindow.superclass.constructor.call(this, cfg);
    }
});
