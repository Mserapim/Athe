/**
 *
 **/
Ext._define('rh.gfp.transparencychoice.reports.Payroll', {
    extend: 'Ext.Window',

    // report: '/to/mpe/gfp/transparency/Payroll',
    report: '/to/mpe/gfp/transparency/Payroll_Genrevent',

    _reportName: 'Transparência - Folha de Pagamento',

    _filename: 'transparencia-folha-pagamento',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 65,
                items: [
                    {
                        xtype: 'combobox',
                        hiddenName: 'category',
                        // name: 'category',
                        fieldLabel: 'Categoria',
                        store: [
                            ['S', 'SERVIDOR'],
                            ['M', 'MEMBRO']
                        ],
                        allowBlank: false,
                        triggerAction: 'all',
                        value: 0
                    },
                    {
                        xtype: 'combobox',
                        hiddenName: 'state',
                        // name: 'state',
                        fieldLabel: 'Ativo',
                        store: [
                            [1, 'SIM'],
                            [0, 'NÃO']
                        ],
                        allowBlank: false,
                        triggerAction: 'all',
                        value: 0
                    },
                    {
                        xtype: 'numberfield', 
                        hiddenName: 'month',
                        name: 'month',
                        fieldLabel: 'Mês', 
                        maxLength: 2,
                        maxValue: 2,
                        allowDecimals: false, 
                        allowBlank: false, 
                    },
                    {
                        xtype: 'numberfield', 
                        hiddenName: 'year',
                        name: 'year',
                        fieldLabel: 'Ano', 
                        maxLength: 4,
                        allowDecimals: false, 
                        allowBlank: false, 
                    }
                ]
            });

        return this._formPanel;
    },

    getValues: function() {
        return this.getFormPanel().getForm().getValues();
    },

    filename: function() {
        return this._filename;
    },

    reportName: function() {
        return this._reportName;
    },

    generate: function(preventClose) {
        var values = this.getValues();

        engine.mq.Report.request({
            report: this.report,
            params: Ext.apply(
                values,
                {
                    outfile: this.filename(),
                    report_name: this.reportName()
                }
            ),
            el: this.getEl(),
            waitMessage: 'Gerando relatório...',
        });

        if(!preventClose) this.close();
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: [
                    {
                        text: 'Gerar',
                        scope: this,
                        handler: function() { this.generate(false); }
                    },
                    {
                        text: 'Gerar e novo',
                        scope: this,
                        handler: function() { this.generate(true); }
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        rh.gfp.transparencychoice.reports.Payroll.superclass.constructor.call(this, cfg);
    }
});
