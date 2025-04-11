 Ext._define('rh.reports.transparency.PensionerPayment', {
	extend: 'toolkit.widget.TabPanel',

	_buildPaycheck: function(type){

        engine.mq.Report.request({
            report: '/to/mpe/gfp/transparency/Payroll_Genrevent_Pensioner',
            waitMessage: 'Gerando relatório...',
            params: {
            	ano: this.getYear().getValue(),
            	mes: this.getMonth().getValue(),
                outfile: 'relatorio_pagamentos_pensionistas',
                report_name: 'Relatório de Pagamentos a Pensionistas'
            }
        }, type);
    },

    getYear: function(){
		if(!this._yearField)
			this._yearField = Ext._create('Ext.form.NumberField', {
                fieldLabel: 'Ano',
                minValue: 2010,
                maxValue: 2100,
                name: 'ano',
                allowBlank: false,
                width: 200
			});

		return this._yearField;
	},

    getMonth: function (cfg) {
        if (!this._monthField)
            this._monthField = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Mês',
                allowBlank: false,
                triggerAction: 'all',
                editable: false,
                store: [
                    ['1', 'JANEIRO'],
                    ['2', 'FEVEREIRO'],
                    ['3', 'MARÇO'],
                    ['4', 'ABRIL'],
                    ['5', 'MAIO'],
                    ['6', 'JUNHO'],
                    ['7', 'JULHO'],
                    ['8', 'AGOSTO'],
                    ['9', 'SETEMBRO'],
                    ['10', 'OUTUBRO'],
                    ['11', 'NOVEMBRO'],
                    ['12', 'DEZEMBRO'],
                ]
            });
        return this._monthField;
    },

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    scope: this,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	// title: 'Informações do Contra-Cheque',
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Relatório de Pagamentos a Pensionistas',
	        		name: 'fieldServidor',
	        		width: 350,
	        		align: 'center',
	        		scope: this,
	        		items:[
	        		this.getMonth(),
	        		this.getYear(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        menu: {
                        	scope: this,
		                    items: [
		                        {
		                            text: 'Arquivo PDF ',
		                            type: 'PDF',
		                            iconCls: 'icon-ged icon-ged-application-pdf',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildPaycheck(item.type);
		                            }
		                        },
		                        {
		                            text: 'Arquivo ODT',
		                            type: 'ODT',
		                            iconCls: 'icon-ged icon-ged-application-msword',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildPaycheck(item.type);
		                            }
		                        },
		                        {
		                            text: 'Arquivo XLS',
		                            type: 'XLS',
		                            iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildPaycheck(item.type);
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

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relatório -> Pagamento a pensionistas'
			}
		);
		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[ 
					this.getMain(),
				]
			}
		);
		rh.reports.transparency.PensionerPayment.superclass.constructor.call(this, cfg);
	}
});