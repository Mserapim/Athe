/**
 *
 **/
Ext._define('adm.patrimonio.reports.SinteticoAtivoLiquidoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: '/to/mpe/adm/patrimonio/Sintetico_Liquido_de_Bens_Ativo',

    _filename: 'sintetico-liquido-de-bens-ativo',

    _reportName: 'Sintético Liquido de Bens Ativos',

    getValues: function() {
        var values = adm.patrimonio.reports.SinteticoAtivoLiquidoWindow.superclass.getValues.call(this);

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
                        xtype: 'combobox',
                        hiddenName: 'proprio',
                        fieldLabel: 'Tipo',
                        store: [
                            [1, 'PRÓPRIO'],
                            [0, 'TERCEIRO']
                        ],
                        allowBlank: false,
                        triggerAction: 'all',
                        value: 1
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
                width: 350
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.reports.SinteticoAtivoLiquidoWindow.superclass.constructor.call(this, cfg);
    }
});
