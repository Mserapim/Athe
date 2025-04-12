/**
 *
 **/

Ext._define('rh.ferias.reports.PendingHolidays', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){

		if(this.getEmployeeField().getValue()){

	        engine.mq.Report.request({
	            report: '/to/mpe/rh/ferias/ferias_pendentes_MATRICULA',
	            waitMessage: 'Gerando relatório...',
	            params: {

	                outfile: 'periodos_pendentes',
	                report_name: 'Periodos Aquisitivos Pendentes',
	                id_servidor: this.getEmployeeField().getValue()
	            }

	        }, type);
		}else Ext.Msg.show({
            msg: 'Preencha os campos',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    getEmployeeField: function(){
		if(!this._employeefield)
			this._employeefield = Ext._create('core.fields.AutocompleteField', {
                name: 'employee',
                rest: 'rh.employee.Restful',
                fieldLabel: 'Servidor',
                width: 350
			});

		return this._employeefield;
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
	        		title: 'Periodos Aquisitivos Pendentes',
	        		name: 'fieldServidor',
	        		width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
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
			   title: 'Relatório -> Periodos Aquisitivos Pendentes'
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

		rh.ferias.reports.PendingHolidays.superclass.constructor.call(this, cfg);
	}
});