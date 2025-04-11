/**
 *
 **/

Ext._define('rh.ferias.reports.HolidayHistory', {
	extend: 'toolkit.widget.TabPanel',

	_buildReport: function(type){

		if(this.getEmployeeField().getValue() && this.getType().getValue()){

			selected = this.getEmployeeField().getComboField().getStore().find('pk', this.getEmployeeField().getValue());

	        engine.mq.Report.request({
	            report: '/to/mpe/rh/ferias/historico_ferias',
	            waitMessage: 'Gerando relatório...',
	            params: {

	                outfile: 'historico_ferias',
	                report_name: 'Histório de Férias',
	                matricula: this.getEmployeeField().getComboField().getStore().getAt(selected).data.matricula,
	                tipo: this.getType().getValue()
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

	getType: function(){
        if(!this._ativo){
            this._ativo = Ext._create('Ext.form.ComboBox', {
                fieldLabel: 'Tipo',
                hiddenName: 'type',
                width: 350,
                triggerAction: 'all',
                store: [
                    ['S', 'Servidor'],
                    ['M', 'Membro']
                ],
            });
        }

        return this._ativo;
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
	        		title: 'Histório de Férias',
	        		name: 'fieldServidor',
	        		width: 500,
	        		style: 'margin: 5px',
	        		align: 'center',
	        		items:[
	        			this.getEmployeeField(),
	        			this.getType(),
                    {
                        xtype: 'button',
                        iconCls: 'icon-siatu icon-siatu-move-down',
                        style: 'margin-top: 10px',
                        text: 'Gerar Relatório',
                        width: 100,
                        height: 25,
                        scope: this,
                        // handler: this._buildReport,
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
			   title: 'Relatório -> Histórico de Férias'
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

		rh.ferias.reports.HolidayHistory.superclass.constructor.call(this, cfg);
	}
});