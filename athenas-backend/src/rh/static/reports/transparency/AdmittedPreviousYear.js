/**
 *
 **/

Ext._define('rh.reports.AdmittedPreviousYearReport', {
	extend: 'toolkit.widget.TabPanel',

	_buildPaycheck: function(type){

        engine.mq.Report.request({
            report: '/to/mpe/portaltransparencia/rh/admitted_in_the_previous_year',
            waitMessage: 'Gerando relatório...',
            params: {
            	ano: this.getYear().getValue(),
                outfile: 'servidores_admitidos_ano_anterior',
                report_name: 'Relatório de Servidores Admitidos no Ano Anterior'
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
			});

		return this._yearField;
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
	        		title: 'Servidores Admitidos no Ano Anterior',
	        		name: 'fieldServidor',
	        		width: 350,
	        		align: 'center',
	        		scope: this,
	        		items:[
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
			   title: 'Relatório -> Servidores Admitidos no Ano Anterior'
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

		// this.getCurrentPayroll();

		rh.reports.AdmittedPreviousYearReport.superclass.constructor.call(this, cfg);
	}
});