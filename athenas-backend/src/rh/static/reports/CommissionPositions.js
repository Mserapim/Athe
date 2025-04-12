/**
 *
 **/

Ext._define('rh.reports.CommissionPositions', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){

        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/commission_positions',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_cargos_em_comissao',
                report_name: 'Relatório Cargos em Comissão'
            }
        }, type);
    },

	getMain: function(){
		if(!this._panel)
		this._panel = new Ext.Panel({
		    layout: 'border',
		    region: 'center',
		    height: 650,
		    split: true,
		    autoEl: {tag: 'center'},
		    items: [
	        {
	        	// title: 'Informações do Contra-Cheque',
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Cargos em Comissão',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        // handler: this._buildPaycheck,
                        menu: {
                        	scope: this,
		                    items: [
		                        {
		                            text: 'Arquivo PDF ',
		                            type: 'PDF',
		                            iconCls: 'icon-ged icon-ged-application-pdf',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildReport(item.type);
		                            }
		                        },
		                        {
		                            text: 'Arquivo ODT',
		                            type: 'ODT',
		                            iconCls: 'icon-ged icon-ged-application-msword',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildReport(item.type);
		                            }
		                        },
		                        {
		                            text: 'Arquivo XLS',
		                            type: 'XLS',
		                            iconCls: 'icon-ged icon-ged-application-vnd-ms-excel',
		                            scope: this,
		                            handler: function (item) {
		                                this._buildReport(item.type);
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
			   title: 'Relatório -> Cargos em Comissão'
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

		rh.reports.CommissionPositions.superclass.constructor.call(this, cfg);
	}
});