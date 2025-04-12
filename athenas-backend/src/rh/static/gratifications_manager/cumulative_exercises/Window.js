 Ext._define('rh.gratifications_manager.cumulative_exercises.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.gratifications_manager.cumulative_exercises.Restful',

    width: 650,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "textfield", 
                        fieldLabel: "Subtituto", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "servidor_unicode",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Titularidade", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "titularidade",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Subtituído",
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "servidor_substituido_unicode",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Cumulativa", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "cumulativa",
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Data Início',
                        name: 'data_inicio',
                        xtype: 'datefield',
                        disabled: true,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Data Fim',
                        name: 'data_fim',
                        xtype: 'datefield',
                        disabled: true,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Data Início Pgto',
                        name: 'data_pgto_inicio',
                        xtype: 'datefield',
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Data Fim Pgto',
                        name: 'data_pgto_fim',
                        xtype: 'datefield',
                    },
                    {
                        maxLength: 40, 
                        allowBlank: true, 
                        fieldLabel: "Ano de Pagamento", 
                        name: "pay_year", 
                        width: 100,
                        xtype: "textfield",
                        disabled: cfg.values.paid_out || cfg.values.indeferido,
                    },
                    {
                        xtype: "combo", 
                        fieldLabel: "Mês de Pagamento", 
                        allowBlank: true, 
                        lazyRender: true, 
                        hiddenName: "pay_month", 
                        mode: "local", 
                        triggerAction: "all", 
                        store: [
                            [1, "JANEIRO"], 
                            [2, "FEVEREIRO"], 
                            [3, "MARÇO"], 
                            [4, "ABRIL"], 
                            [5, "MAIO"], 
                            [6, "JUNHO"], 
                            [7, "JULHO"], 
                            [8, "AGOSTO"], 
                            [9, "SETEMBRO"], 
                            [10, "OUTUBRO"], 
                            [11, "NOVEMBRO"], 
                            [12, "DEZEMBRO"], 
                        ], 
                        name: "pay_month",
                        width: 300,
                        disabled: cfg.values.paid_out || cfg.values.indeferido,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Gedoc',
                        name: 'gedoc',
                        xtype: 'textfield'
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Parcelas de pagamento',
                        name: 'payment_installments',
                        xtype: 'textfield',
                        disabled: true,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Período de Venda (Janela)',
                        name: 'periodo',
                        xtype: 'textfield',
                        disabled: true,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Apto a pagamento',
                        name: 'able_to_pay',
                        xtype: 'checkbox'
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Pago',
                        name: 'paid_out',
                        xtype: 'checkbox',
                        disabled: true,
                    },
                    {
                        allowBlank: true,
                        fieldLabel: 'Retroativo',
                        name: 'retroativo',
                        xtype: 'checkbox',
                        disabled: true,
                    },
                ]
            });

        return this._formPanel;
    }
});
