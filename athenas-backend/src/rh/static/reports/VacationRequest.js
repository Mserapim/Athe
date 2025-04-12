Ext._define('rh.reports.VacationRequest', {
	extend: 'toolkit.widget.TabPanel',

	_buildPaycheck: function(){
		var employee = this.getEmployee().getValue();
        engine.mq.Report.request({
            report: '/to/mpe/portalservidor/Ferias',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_ferias',
                report_name: 'Requerimento de Férias',
                servidor: employee
            }
        });
    },
    getEmployee: function() {
        if (!this._employee) {
            this._employee = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Servidor',
                allowBlank: true,
                rest: "rh.employee.Restful",
            });
        }

        return this._employee;
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
	        		title: 'Formulário de Férias',
	        		name: 'fieldServidor',
	        		width: "33%",
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        		this.getEmployee(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Formulário',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this._buildPaycheck,
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
			   title: 'Relatório -> Formulário de Férias'
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

		rh.reports.VacationRequest.superclass.constructor.call(this, cfg);
	}
});