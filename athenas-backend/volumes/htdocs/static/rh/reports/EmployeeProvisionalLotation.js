Ext._define('rh.reports.EmployeeProvisionalLotation', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){
        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/provisional_designation',
            waitMessage: 'Gerando relatório...',
            params: {

                outfile: 'lotacoes_provisorias',
                report_name: 'Lotações Provisórias',
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
	        	region: 'center',
	        	border: false,
	        	items: [
	        	{
	        		xtype: 'fieldset',
	        		title: 'Lotações Provisórias',
	        		width: 500,
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
			   title: 'Relatório -> Lotações Provisórias'
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

		rh.reports.EmployeeProvisionalLotation.superclass.constructor.call(this, cfg);
	}
});