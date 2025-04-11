/**
 *
 **/
Ext._define('adm.patrimonio.reports.AnaliticoAtivoWindow', {
    extend: 'adm.patrimonio.reports.BaseWindow',

    report: 'to/mpe/adm/patrimonio/analitico/main',

    controller: 'PATReportAnalitico',

    getValues: function() {
        var values = adm.patrimonio.reports.AnaliticoWindow.superclass.getValues.call(this);
        var wdt;

        try {
            wdt = Date.parseDate(values.data_inicial, 'd/m/Y');
        }
        catch(e) {
            wdt = new Date('1/1/1900');
        }
        finally {
            values.data_inicial = Ext.util.Format.date(wdt, 'Y-m-d');
        }

        try {
            wdt = Date.parseDate(values.data_final, 'd/m/Y');
        }
        catch(e) {
            wdt = new Date();
        }
        finally {
            values.data_final = Ext.util.Format.date(wdt, 'Y-m-d');
        }

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
                title: 'Relatório Analitico',
                width: 350
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.reports.AnaliticoWindow.superclass.constructor.call(this, cfg);
    }
});
