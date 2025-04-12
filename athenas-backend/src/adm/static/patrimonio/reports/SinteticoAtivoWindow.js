/**
 *
 **/
Ext._define('adm.patrimonio.reports.SinteticoAtivoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: '/to/mpe/adm/patrimonio/Sintetico_de_Bens_Ativo',

    _filename: 'sintetico-de-bens-ativo',

    _reportName: 'Sintético de Bens Ativo',

    getValues: function() {
        var values = adm.patrimonio.reports.SinteticoAtivoWindow.superclass.getValues.call(this);

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
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Conta',
                        name: 'conta',
                        rest: 'adm.patrimonio.parametro.ContaRestful',
                        gridColumnAction: false
                    },
                    {
                        fieldLabel: 'Nota',
                        hiddenName: 'tipo_nota',
                        xtype: 'combo',
                        width: 270,
                        store: [
                            ['nota-fiscal', 'Nota Fiscal'],
                            ['nota-doacao', 'Doação'],
                            ['nota-convenio', 'Convênio']
                        ]
                    },
                    {
                        xtype: 'checkbox',
                        name: 'gerencial',
                        checked: false,
                        inputValue: '1',
                        boxLabel: 'Relatório Gerencial (Não consolidado)',
                        hidden: true
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
    filename: function() {
        var values = this.getValues();

        return [
            'sintetico-de-bens-ativo',
            values.data_final.split('-').join('')
        ].join('-');
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
        adm.patrimonio.reports.SinteticoAtivoWindow.superclass.constructor.call(this, cfg);
    }
});
